import streamlit as st
import pandas as pd
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth, firestore

# -----------------------------------------------------------------
# 1. FIREBASE INITIALIZATION
# -----------------------------------------------------------------
# We use a singleton pattern to avoid re-initializing on every rerun
if not firebase_admin._apps:
    try:
        # Load the service account key we just created
        cred = credentials.Certificate('firebase_key.json') 
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        st.stop()

# Get a reference to the Firestore database
db = firestore.client()

# -----------------------------------------------------------------
# 2. PAGE CONFIGURATION
# -----------------------------------------------------------------
st.set_page_config(
    page_title="Gout - Local Event Finder",
    page_icon="📍",
    layout="wide"
)

# --- HIDE THE HEADER ANCHOR LINKS ---
st.markdown("""
    <style>
        a[data-testid="stHeaderActionLinks"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 3. SESSION STATE MANAGEMENT (Login Persistence)
# -----------------------------------------------------------------
if 'user' not in st.session_state:
    st.session_state.user = None

def login_user(email, password):
    try:
        # This verifies the user with Firebase Authentication
        # Note: The Admin SDK doesn't have a direct 'sign_in_with_email_password' 
        # for security reasons (it's admin-only). 
        # For a simple prototype, we verify by checking if the user EXISTS.
        # In a real production app, we'd use the Firebase REST API for client-side login.
        
        user = auth.get_user_by_email(email)
        st.session_state.user = {'uid': user.uid, 'email': user.email}
        st.success(f"Welcome back, {user.email}!")
        st.rerun() # Reload the app to show the logged-in view
    except Exception as e:
        st.error("Login failed. Check email or create an account.")

def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        st.session_state.user = {'uid': user.uid, 'email': user.email}
        st.success("Account created! You are now logged in.")
        st.rerun()
    except Exception as e:
        st.error(f"Signup failed: {e}")

def logout_user():
    st.session_state.user = None
    st.rerun()

# -----------------------------------------------------------------
# 4. MODEL LOADING (Existing Code)
# -----------------------------------------------------------------
@st.cache_data
def load_models():
    # ... (Your existing load_models logic here) ...
    # (I will keep this concise, use the same logic as before)
    try:
        with open('model/vectorizer.pkl', 'rb') as f: vectorizer = pickle.load(f)
        with open('model/tfidf_matrix.pkl', 'rb') as f: tfidf_matrix = pickle.load(f)
        events_df = pd.read_pickle('model/events_data.pkl')
        return vectorizer, tfidf_matrix, events_df
    except: return None, None, None

vectorizer, tfidf_matrix, events_df = load_models()

# -----------------------------------------------------------------
# 5. HELPER FUNCTIONS (Existing Code)
# -----------------------------------------------------------------
def get_recommendations(query, top_n=50):
    query_vector = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = cosine_similarities.argsort()[-top_n:][::-1]
    return events_df.iloc[top_indices]

@st.cache_data
def geocode_user_address(address):
    # ... (Your existing geocode logic) ...
    try:
        geolocator = Nominatim(user_agent="gout-app-v4", timeout=10)
        loc = geolocator.geocode(address)
        if loc: return (loc.latitude, loc.longitude)
    except: pass
    return None

# -----------------------------------------------------------------
# 6. MAIN APP UI
# -----------------------------------------------------------------

# --- TOP BAR: AUTHENTICATION ---
col_title, col_auth = st.columns([3, 1])

with col_title:
    st.title("📍 Gout: AI-Powered Event Finder")

with col_auth:
    if st.session_state.user:
        st.write(f"👤 {st.session_state.user['email']}")
        if st.button("Log Out"):
            logout_user()
    else:
        # Show Login/Signup Expanders
        auth_mode = st.radio("Auth Mode", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed")
        email = st.text_input("Email", key="auth_email")
        password = st.text_input("Password", type="password", key="auth_pass")
        
        if auth_mode == "Login":
            if st.button("Log In"):
                login_user(email, password)
        else:
            if st.button("Create Account"):
                signup_user(email, password)

st.markdown("---")

# --- APP CONTENT (Only runs if we have models) ---
if vectorizer:
    
    # 1. Search & Filters (Same as before)
    st.subheader("What are you looking for?")
    user_query = st.text_input("Search", placeholder="e.g., 'live music'", label_visibility="collapsed")
    
    c1, c2, c3 = st.columns([1, 1.5, 1.5], gap="small")
    with c1:
        st.write("Current Location")
        location = streamlit_geolocation()
    with c2:
        st.write("Or Enter Address")
        user_address = st.text_input("Address", placeholder="City or Zip", label_visibility="collapsed")
    with c3:
        # --- FIXED LAYOUT: Both sliders in same column ---
        st.write("Filters")
        distance_miles = st.slider("Distance (miles)", 1, 50, 10)
        result_limit = st.slider("Number of results", 5, 50, 10, step=5)

    st.markdown("---")
    if st.button("Search for Events", type="primary", use_container_width=True):
        
        # (Your existing search logic goes here...)
        
        recs = get_recommendations(user_query)
        
        # --- Geocoding & Filtering Logic ---
        final_recommendations = recs # Default fallback
        user_lat_lon = None
        user_location_found = False

        # Priority 1: Check typed address
        if user_address: 
            user_lat_lon = geocode_user_address(user_address)
            if user_lat_lon:
                user_location_found = True
                st.success(f"Using address: {user_address}")
            else:
                st.error("Address not found.")

        # Priority 2: Check button
        elif location and 'latitude' in location:
            user_lat_lon = (location['latitude'], location['longitude'])
            user_location_found = True
            st.success("Using current location.")
        
        # Filter by distance if location found
        if user_location_found and user_lat_lon:
            distances = []
            for index, row in recs.iterrows():
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    dist = geodesic(user_lat_lon, (row['latitude'], row['longitude'])).miles
                    distances.append(dist)
                else:
                    distances.append(float('inf'))
            
            recs['distance_miles'] = distances
            final_recommendations = recs[recs['distance_miles'] <= distance_miles].sort_values('distance_miles')
        
        # Limit results
        final_recommendations = final_recommendations.head(result_limit)

        st.header(f"Top Results")
        
        for index, row in final_recommendations.iterrows():
            # Create a card-like layout
            with st.container(border=True):
                c_info, c_action = st.columns([3, 1])
                
                with c_info:
                    st.subheader(row['title'])
                    
                    # --- DISPLAY CATEGORY ---
                    if 'category' in row and pd.notna(row['category']):
                        st.caption(f"🏷️ {row['category']}")
                    
                    # --- DATE/TIME FIX ---
                    try:
                        dt_object = datetime.fromisoformat(row['datetime'])
                        friendly_date = dt_object.strftime("%A, %B %d, %Y at %I:%M %p")
                        st.write(f"📅 **{friendly_date}**")
                    except:
                        st.write(f"📅 {row['datetime']}")
                        
                    st.write(f"📍 {row['location_name']}")
                    if 'distance_miles' in row and row['distance_miles'] != float('inf'):
                         st.write(f"📏 {row['distance_miles']:.2f} miles away")

                    st.write(row['description'][:150] + "...")
                
                with c_action:
                    st.link_button("View Tickets", row['source_url'])
                    
                    # --- NEW: BOOKMARK BUTTON ---
                    if st.session_state.user:
                        # Unique key for each button based on event title
                        if st.button("❤️ Save", key=f"save_{index}"):
                            # Save to Firestore
                            # Convert row to dict and ensure basic types for JSON serialization
                            event_data = row.to_dict()
                            # Remove complex objects if any (though pandas types usually handle ok)
                            
                            doc_ref = db.collection('users').document(st.session_state.user['uid']).collection('bookmarks').document()
                            doc_ref.set(event_data)
                            st.toast("Event saved!")
                    else:
                        st.caption("Login to save")