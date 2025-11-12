import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle  # We use pickle to save our model files

print("Starting model training...")

# --- Step 1: Load and Prepare Data ---
# Load the CSV file you just created
try:
    df = pd.read_csv('data/eventbrite_events.csv')
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