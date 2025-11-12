import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle  # We use pickle to save our model files
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

print("Starting model training...")

# --- Step 1: Load and Prepare Data ---
# Load the CSV file you just created
try:
    df = pd.read_csv('data/eventbrite_events.csv')
    # --- NEW STEP: Geocoding Addresses ---
    print("Starting geocoding... (This may take a moment)")

    # Initialize the geocoder
    geolocator = Nominatim(user_agent="gout-app-v1", timeout=10)

    # Use a rate limiter to avoid getting blocked (1 request per second)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # Create empty lists to store our new coordinates
    latitudes = []
    longitudes = []

    # Loop through each address in our DataFrame
    for address in df['address']:
        if address == "Online" or not address:
            latitudes.append(None)
            longitudes.append(None)
            continue

        try:
            # Try to find the location
            location = geocode(address)
            if location:
                latitudes.append(location.latitude)
                longitudes.append(location.longitude)
            else:
                latitudes.append(None)
                longitudes.append(None)
        except Exception as e:
            print(f"Error geocoding address '{address}': {e}")
            latitudes.append(None)
            longitudes.append(None)

        time.sleep(1) # Be respectful to the API

    # Add the new lists as columns to our DataFrame
    df['latitude'] = latitudes
    df['longitude'] = longitudes
    print("Geocoding complete.")
    # --- END OF NEW STEP ---
except FileNotFoundError:
    print("Error: 'data/eventbrite_events.csv' not found.")
    print("Please make sure your eventbrite_scraper.py ran successfully.")
    exit()

# We need to fill any missing descriptions with an empty string
# or the model will crash.
df['description'] = df['description'].fillna('')

# --- Step 2: Build the TF-IDF Model ---
# Initialize the TF-IDF Vectorizer
# stop_words='english' tells it to ignore common words (e.g., 'the', 'is', 'a')
print("Building TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(stop_words='english')

# 'fit_transform' learns the vocabulary and converts descriptions to a matrix
tfidf_matrix = vectorizer.fit_transform(df['description'])

print("Model built successfully.")
print(f"Matrix shape: {tfidf_matrix.shape}") # (events, unique_words)

# --- Step 3: Save the Model Files ---
# We save the vectorizer and the matrix so our app can use them
# without having to re-train every time.
print("Saving model files to /model directory...")

# Let's create a new folder for our models
import os
os.makedirs('model', exist_ok=True) # Creates 'model' folder if it doesn't exist

# Save the vectorizer
with open('model/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

# Save the TF-IDF matrix
with open('model/tfidf_matrix.pkl', 'wb') as f:
    pickle.dump(tfidf_matrix, f)

# We also need to save the data that corresponds to the matrix
# This is a simple way to link our matrix rows back to our data
df.to_pickle('model/events_data.pkl')

print("--- Model training complete. Files saved! ---")