import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
import requests # For Google Places API

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
        a[data-testid="stHeaderActionLinks"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# LOAD API KEY FROM SECRETS
# -----------------------------------------------------------------
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_PLACES_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Google Places API Key not found. Please add it to your Streamlit Secrets.")
    st.stop()

# -----------------------------------------------------------------
# MODEL & DATA LOADING
# -----------------------------------------------------------------
@st.cache_data
def load_models():
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
# HELPER FUNCTIONS
# -----------------------------------------------------------------
def get_recommendations(query, top_n=50):
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    recommendations = events_df.iloc[top_indices]
    return recommendations

@st.cache_data
def geocode_user_address(address):
    try:
        geolocator = Nominatim(user_agent="gout-app-v3", timeout=10)
        user_location = geolocator.geocode(address)
        if user_location:
            return (user_location.latitude, user_location.longitude)
    except Exception as e:
        print(f"Error geocoding user address: {e}")
    return None

# --- NEW: Google Places Autocomplete Function ---
@st.cache_data
def get_address_suggestions(query):
    """
    Calls Google Places API to get address suggestions.
    """
    if not query:
        return []
    
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "key": GOOGLE_API_KEY,
        "types": "address",
        "components": "country:us" # Restrict to USA
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            predictions = response.json().get("predictions", [])
            # Return just the text description of each prediction
            return [pred["description"] for pred in predictions]
        else:
            print(f"Google Places API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error calling Google API: {e}")
        return []

# --- NEW: Callback function to set the address ---
def set_address(address):
    """
    Callback function to update the session state
    when a suggestion button is clicked.
    """
    st.session_state.user_address_input = address


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

# -------------------------------------------------------------
# --- ADVANCED 3-COLUMN LAYOUT with Autocomplete ---
# -------------------------------------------------------------
st.write("**Set your location and search radius:**")
col1_loc, col2_loc, col3_dist = st.columns([1, 1.5, 1.5], gap="small") 

with col1_loc:
    st.write("Current Location")
    location = streamlit_geolocation()

with col2_loc:
    st.write("Or Enter Your Address")
    
    # 1. Initialize session state for the text input
    if "user_address_input" not in st.session_state:
        st.session_state.user_address_input = ""

    # 2. Create the text input, bound to session state
    user_address = st.text_input(
        "Enter your address",
        key="user_address_input",
        label_visibility="collapsed"
    )

    # 3. Get suggestions based on the *current* state of the input
    suggestions = get_address_suggestions(user_address)
    
    # 4. Create a container for the suggestion buttons
    suggestions_container = st.container()
    with suggestions_container:
        for suggestion in suggestions:
            # 5. Create a button for each suggestion
            # When clicked, it calls set_address() to update the state
            st.button(
                suggestion, 
                key=suggestion, 
                on_click=set_address, 
                args=(suggestion,)
            )

with col3_dist:
    st.write("Distance (in miles)")
    distance_miles = st.slider(
        "Filter distance (in miles)",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        label_visibility="collapsed"
    )
# -------------------------------------------------------------
# --- END OF ADVANCED LAYOUT ---
# -------------------------------------------------------------

st.markdown("---") 
search_button = st.button("Search for Events", type="primary", use_container_width=True)

if search_button:
    
    if not user_query:
        st.warning("Please enter something to search for.")
        st.stop() 

    st.markdown("---")
    
    recommendations_df = get_recommendations(user_query)
    
    if recommendations_df.empty:
        st.warning("No matching events found. Try a different search.")
        st.stop()

    # -------------------------------------------------------------
    # --- 2. Filter by Distance ---
    # -------------------------------------------------------------
    final_recommendations = recommendations_df
    user_lat_lon = None
    user_location_found = False

    # Priority 1: Check the text box (which is now in session_state)
    # We check st.session_state.user_address_input because 'user_address' is overwritten
    if st.session_state.user_address_input: 
        user_lat_lon = geocode_user_address(st.session_state.user_address_input)
        
        if user_lat_lon:
            user_location_found = True
            st.success(f"Using your typed address. Finding events within {distance_miles} miles.")
        else:
            st.error("Could not find that address. Please try again.")
            final_recommendations = recommendations_df.head(5)

    # Priority 2: Check if the location button was clicked
    elif location and 'latitude' in location:
        user_lat_lon = (location['latitude'], location['longitude'])
        user_location_found = True
        st.success(f"Using your current location. Finding events within {distance_miles} miles.")
    
    # ELSE: No location given at all
    else: 
        st.info("Enter your address or use the 'Current Location' button to filter by distance.")
        final_recommendations = recommendations_df.head(5)

    # (The rest of your logic for filtering and displaying is unchanged)
    
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
        
        final_recommendations = recommendations_df[
            recommendations_df['distance_miles'] <= distance_miles
        ].sort_values('distance_miles')
    
    if final_recommendations.empty:
        st.warning(f"No relevant events found within {distance_miles} miles.")
    else:
        col1_results, col2_results = st.columns([1.5, 1])
        
        with col1_results:
            st.header("Your Recommendations")
            for index, row in final_recommendations.iterrows():
                st.subheader(row['title'])
                st.markdown(f"**Date:** {row['datetime']}")
                if 'distance_miles' in row and row['distance_miles'] != float('inf'):
                    st.markdown(f"**Distance:** {row['distance_miles']:.2f} miles away")
                st.markdown(f"**Location:** {row['location_name']}")
                st.write(row['description'])
                st.markdown(f"[View on Eventbrite]({row['source_url']})")
                st.markdown("---")
        
        with col2_results:
            st.header("Event Map")
            map_data = final_recommendations.dropna(subset=['latitude', 'longitude'])
            
            if user_lat_lon:
                map_center = user_lat_lon
                zoom_level = 11
            elif not map_data.empty:
                map_center = [map_data.iloc[0]['latitude'], map_data.iloc[0]['longitude']]
                zoom_level = 11
            else:
                map_center = [41.2709, -72.9463]
                zoom_level = 11

            m = folium.Map(location=map_center, zoom_start=zoom_level)

            if not map_data.empty:
                for index, row in map_data.iterrows():
                    folium.Marker(
                        [row['latitude'], row['longitude']],
                        popup=f"<strong>{row['title']}</strong>",
                        tooltip=row['title']
                    ).add_to(m)
            
            if user_lat_lon:
                folium.Marker(
                    [user_lat_lon[0], user_lat_lon[1]],
                    popup="<strong>Your Location</strong>",
                    tooltip="Your Location",
                    icon=folium.Icon(color='red', icon='user')
                ).add_to(m)
            
            st_folium(m, width=700, height=500, returned_objects=[])

else:
    st.info("Enter your search, set your location, and click 'Search for Events' to begin.")