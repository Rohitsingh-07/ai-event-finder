import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import folium
from streamlit_folium import st_folium

# --- 1. Load All Model Files ---
print("Loading models...")
try:
    # Load the vectorizer
    with open('model/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

    # Load the TF-IDF matrix
    with open('model/tfidf_matrix.pkl', 'rb') as f:
        tfidf_matrix = pickle.load(f)

    # Load the corresponding event data
    events_df = pd.read_pickle('model/events_data.pkl')

except FileNotFoundError:
    st.error("Model files not found. Please run `model.py` first.")
    st.stop()

print("Models loaded successfully.")

# --- 2. Recommendation Function ---
def get_recommendations(query, top_n=5):
    """Finds the top_n most similar events to a user's query."""

    # 1. Convert the user's query into a TF-IDF vector
    query_vector = vectorizer.transform([query])

    # 2. Calculate cosine similarity between the query and all events
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # 3. Get the indices of the top_n most similar events
    # We use .argsort() to sort by similarity, then take the top_n
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]

    # 4. Get the actual event data using these indices
    recommendations = events_df.iloc[top_indices]

    return recommendations

# -----------------------------------------------------------------
# PAGE CONFIGURATION (Must be the first Streamlit command)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Gout - Local Event Finder",
    page_icon="📍",
    layout="wide"
)

# --- 3. Build The Streamlit UI ---
st.title("📍 Gout: AI-Powered Event Finder")
st.markdown("*Find local events, right now, tailored to your vibe.*")

# --- Search Bar ---
user_query = st.text_input(
    "What are you looking for?",
    placeholder="e.g., 'live music', 'food truck', 'family event'"
)

if user_query:
    st.markdown("---")

    # --- 4. Get Recommendations ---
    recommendations_df = get_recommendations(user_query)

    if recommendations_df.empty:
        st.warning("No matching events found. Try a different search.")
    else:
        # --- 5. Display Results (List and Map) ---
        col1, col2 = st.columns([1.5, 1]) # Make list column wider

        # --- Column 1: Event List ---
        with col1:
            st.header(f"Top 5 Results for \"{user_query}\"")

            for index, row in recommendations_df.iterrows():
                st.subheader(row['title'])
                st.markdown(f"**Date:** {row['datetime']}")
                st.markdown(f"**Location:** {row['location_name']}")
                st.markdown(f"**Address:** {row['address']}")
                st.write(row['description'])
                st.markdown(f"[View on Eventbrite]({row['source_url']})")
                st.markdown("---")

        # --- Column 2: Map ---
        # --- Column 2: Map ---
        with col2:
            st.header("Event Map")

            # Filter out events that we couldn't geocode
            map_data = recommendations_df.dropna(subset=['latitude', 'longitude'])

            if map_data.empty:
                st.warning("Could not find coordinates for any recommended events.")
                # Show a blank map centered on West Haven
                m = folium.Map(location=[41.2709, -72.9463], zoom_start=11)
            else:
                # Create a map centered on the first event
                m = folium.Map(
                    location=[map_data.iloc[0]['latitude'], map_data.iloc[0]['longitude']], 
                    zoom_start=11
                )

                # Add a pin for each event
                for index, row in map_data.iterrows():
                    folium.Marker(
                        [row['latitude'], row['longitude']],
                        popup=f"<strong>{row['title']}</strong><br>{row['location_name']}",
                        tooltip=row['title']
                    ).add_to(m)

            # Display the map
            st_folium(m, width=700, height=500, returned_objects=[])

else:
    st.info("Start by typing what you're interested in above.")