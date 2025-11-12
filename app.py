import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim  # For user address
from geopy.distance import geodesic    # For distance calculation
from streamlit_geolocation import streamlit_geolocation # The working component

# -----------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Gout - Local Event Finder",
    page_icon="📍",
    layout="wide"
)

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
def get_recommendations(query, top_n=50):
    """
    Finds the top_n most similar events to a user's query.
    We get 50 so we have a large pool to filter by distance.
    """
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    recommendations = events_df.iloc[top_indices]
    return recommendations

# -----------------------------------------------------------------
# GEOCODING FUNCTION (for user address)
# -----------------------------------------------------------------
@st.cache_data
def geocode_user_address(address):
    """
    Converts a user's address string into lat/lon.
    Uses cache to avoid re-querying the same address.
    """
    try:
        geolocator = Nominatim(user_agent="gout-app-v3", timeout=10)
        user_location = geolocator.geocode(address)
        if user_location:
            return (user_location.latitude, user_location.longitude)
    except Exception as e:
        print(f"Error geocoding user address: {e}")
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
    label_visibility="collapsed" # Hides the default label
)

# -------------------------------------------------------------
# --- NEW 3-COLUMN LAYOUT for all filters ---
# -------------------------------------------------------------
st.write("**Set your location and search radius:**")
col1_loc, col2_loc, col3_dist = st.columns([1, 1.5, 1.5], gap="small") 

with col1_loc:
    st.write("Current Location") # Label for the button
    location = streamlit_geolocation() # This creates the icon button

with col2_loc:
    st.write("Or Enter Your Address")
    user_address = st.text_input(
        "Enter your address",
        placeholder="e.g., 123 Main St",
        label_visibility="collapsed"
    )

with col3_dist:
    st.write("Distance (in miles)")
    distance_miles = st.slider(
        "Filter distance (in miles)",
        min_value=1,
        max_value=50,
        value=10, # Default to 10 miles
        step=1,
        label_visibility="collapsed" # Hide label, we made our own
    )
# -------------------------------------------------------------
# --- END OF NEW 3-COLUMN LAYOUT ---
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
    # --- 2. Filter by Distance --- (This logic is unchanged)
    # -------------------------------------------------------------
    final_recommendations = recommendations_df
    user_lat_lon = None
    user_location_found = False

    # --- Priority 1: Check if the user typed an address ---
    if user_address: 
        user_lat_lon = geocode_user_address(user_address)
        
        if user_lat_lon:
            user_location_found = True
            st.success(f"Using your typed address. Finding events within {distance_miles} miles.")
        else:
            st.error("Could not find that address. Please try again.")
            final_recommendations = recommendations_df.head(5)

    # --- Priority 2: Check if the location button was clicked ---
    elif location and 'latitude' in location:
        user_lat_lon = (location['latitude'], location['longitude'])
        user_location_found = True
        st.success(f"Using your current location. Finding events within {distance_miles} miles.")
    
    # --- ELSE: No location given at all ---
    else: 
        st.info("Enter your address or use the 'Current Location' button to filter by distance.")
        final_recommendations = recommendations_df.head(5)


    # --- IF a location was found (either by button or text) ---
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
    
    # -------------------------------------------------------------
    # --- 3. Display Final Results (List and Map) ---
    # -------------------------------------------------------------
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
                map_center = [41.2709, -72.9463] # Default to West Haven
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