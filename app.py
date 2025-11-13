import streamlit as st
import pandas as pd
import pickle
import requests  # For Google Geocoding
from sklearn.metrics.pairwise import cosine_similarity
from geopy.geocoders import Nominatim  # For fallback geocoding
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime # Import for formatting date/time

# -----------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Gout - Local Event Finder",
    page_icon="📍",
    layout="wide"
)

# --- HIDE THE HEADER ANCHOR LINKS ---
st.markdown("""
    <style>
        /* This hides the link icon on headers */
        a[data-testid="stHeaderActionLinks"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# MODEL & DATA LOADING
# -----------------------------------------------------------------
@st.cache_data
def load_models():
    """
    Loads the ML models and data from disk.
    Uses Streamlit's cache to only do this once.
    """
    print("Loading models...")
    try:
        with open('model/vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        with open('model/tfidf_matrix.pkl', 'rb') as f:
            tfidf_matrix = pickle.load(f)
        events_df = pd.read_pickle('model/events_data.pkl')
        print("Models loaded successfully.")
        return vectorizer, tfidf_matrix, events_df
    except FileNotFoundError:
        return None, None, None

vectorizer, tfidf_matrix, events_df = load_models()

if vectorizer is None:
    st.error("Model files not found. Please run `model.py` first.")
    st.stop()

# -----------------------------------------------------------------
# RECOMMENDATION FUNCTION
# -----------------------------------------------------------------
def get_recommendations(query, top_n=50): # We get 50 to have a large pool to filter
    """
    Finds the top_n most similar events to a user's query.
    """
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    recommendations = events_df.iloc[top_indices]
    return recommendations

# -----------------------------------------------------------------
# GEOCODING FUNCTION (with Google API and fallback)
# -----------------------------------------------------------------
@st.cache_data
def geocode_user_address(address):
    """
    Converts a user's address string into lat/lon using Google Geocoding API.
    Falls back to Nominatim if Google API key is not found.
    """
    # Try to use Google Geocoding API first
    try:
        api_key = st.secrets["GOOGLE_GEOCODING_API_KEY"]
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {'address': address, 'key': api_key}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            print(f"Google Geocoding success for: {address}")
            return (location["lat"], location["lng"])
        else:
            print(f"Google Geocoding Error: {data['status']}")
            
    except KeyError:
        # If GOOGLE_GEOCODING_API_KEY is not in secrets, fall back to Nominatim
        print("Warning: GOOGLE_GEOCODING_API_KEY not found. Falling back to Nominatim (less accurate).")
    except Exception as e:
        # Other errors (like request failure)
        print(f"Error calling Google Geocoding API: {e}. Falling back to Nominatim.")

    # --- Fallback to Nominatim (the free one) ---
    try:
        geolocator = Nominatim(user_agent="gout-app-v3", timeout=10)
        user_location = geolocator.geocode(address)
        if user_location:
            print(f"Nominatim success for: {address}")
            return (user_location.latitude, user_location.longitude)
    except Exception as e:
        print(f"Error with Nominatim: {e}")
    
    # If both fail
    print(f"Failed to geocode address: {address}")
    return None

# -----------------------------------------------------------------
# (Sidebar is empty)
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# MAIN PAGE CONTENT
# -----------------------------------------------------------------
st.title("📍 Gout: AI-Powered Event Finder")
st.markdown("*Find local events, right now, tailored to your vibe.*")
st.markdown("---") 

st.subheader("What are you looking for?")
user_query = st.text_input(
    "What are you looking for?",
    placeholder="e.g., 'live music', 'food truck', 'family event'",
    label_visibility="collapsed"
)

# --- 3-COLUMN LAYOUT for location filters ---
col1_loc, col2_loc, col3_dist = st.columns([1, 1.5, 1.5], gap="small") 

with col1_loc:
    st.write("**Use current location**")
    location = streamlit_geolocation() # The icon button

with col2_loc:
    st.write("**Or Enter Your Address**")
    user_address = st.text_input(
        "Enter your address",
        placeholder="e.g., 59 north pl, west haven, ct",
        label_visibility="collapsed"
    )

with col3_dist:
    st.write("**Distance (in miles)**")
    distance_miles = st.slider(
        "Filter distance (in miles)",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        label_visibility="collapsed"
    )
    
# --- ROLLBACK: Moved slider to its own row ---
st.write("**Number of results**")
result_limit = st.slider(
    "Number of results to show",
    min_value=5,
    max_value=50,
    value=10, # Default to 10 results
    step=5,
    label_visibility="collapsed"
)
# --- END ROLLBACK ---


st.markdown("---") 
search_button = st.button("Search for Events", type="primary", use_container_width=True)

if search_button:
    
    if not user_query:
        st.warning("Please enter something to search for.")
        st.stop() 

    st.markdown("---")
    
    # --- 1. Get ALL Recommendations First ---
    recommendations_df = get_recommendations(user_query, top_n=50) 
    
    if recommendations_df.empty:
        st.warning("No matching events found. Try a different search.")
        st.stop()

    # --- 2. Filter by Distance ---
    final_recommendations = recommendations_df
    user_lat_lon = None
    user_location_found = False

    # --- LOGIC FIX: Prioritize typed address ---
    if user_address: 
        user_lat_lon = geocode_user_address(user_address)
        
        if user_lat_lon:
            user_location_found = True
            st.success(f"Using your typed address. Finding events within {distance_miles} miles.")
        else:
            st.error("Could not find that address. Please try again.")
            
    # ELSE: Check if the button was clicked
    elif location and 'latitude' in location:
        user_lat_lon = (location['latitude'], location['longitude'])
        user_location_found = True
        st.success(f"Using your current location. Finding events within {distance_miles} miles.")
    
    else: 
        st.info("Enter your address or use the 'Current Location' button to filter by distance.")
        
    # --- Filter logic ---
    if user_location_found and user_lat_lon:
        distances = []
        for index, row in recommendations_df.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                event_lat_lon = (row['latitude'], row['longitude'])
                dist = geodesic(user_lat_lon, event_lat_lon).miles
                distances.append(dist)
            else:
                distances.append(float('inf'))
        
        recommendations_df['distance_miles'] = distances
        
        # Filter by distance, sort, THEN take the top results
        final_recommendations = recommendations_df[
            recommendations_df['distance_miles'] <= distance_miles
        ].sort_values('distance_miles').head(result_limit) # Use slider limit
    else:
        # If no location was used, just show the top results
         final_recommendations = recommendations_df.head(result_limit)

    # --- 3. Display Final Results (List Only) ---
    if final_recommendations.empty:
        st.warning(f"No relevant events found. Try expanding your distance or search term.")
    else:
        st.header(f"Your Top {len(final_recommendations)} Recommendations")
        for index, row in final_recommendations.iterrows():
            st.subheader(row['title'])
            
            # --- DISPLAY CATEGORY ---
            if 'category' in row and pd.notna(row['category']):
                st.markdown(f"**Category:** `{row['category']}`")
                
            # --- DATE/TIME FIX ---
            try:
                # Parse the ISO format string
                dt_object = datetime.fromisoformat(row['datetime'])
                # Format it into a friendly string
                friendly_date = dt_object.strftime("%A, %B %d, %Y at %I:%M %p")
                st.markdown(f"**When:** {friendly_date}")
            except Exception:
                # Fallback if the date format is weird
                st.markdown(f"**When:** {row['datetime']}")
            # --- END DATE/TIME FIX ---
                
            if 'distance_miles' in row and row['distance_miles'] != float('inf'):
                st.markdown(f"**Distance:** {row['distance_miles']:.2f} miles away")
            
            st.markdown(f"**Location:** {row['location_name']}")
            st.write(row['description'])
            st.markdown(f"[View on Eventbrite]({row['source_url']})")
            st.markdown("---")

else:
    st.info("Enter your search, set your location, and click 'Search for Events' to begin.")