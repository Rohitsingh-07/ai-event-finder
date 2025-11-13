import pandas as pd
import pickle
import os

print("Checking your model file: model/events_data.pkl")

# Define the file path
file_path = 'model/events_data.pkl'

if not os.path.exists(file_path):
    print(f"\n❌ FATAL ERROR: '{file_path}' not found.")
    print("Please run 'model.py' to create it.")
    exit()

try:
    # Load the saved events DataFrame
    with open(file_path, 'rb') as f:
        events_df = pd.read_pickle(f)
    
    print("\n--- Success! Model file loaded. ---")
    
    # Print all the column names in the file
    print("\nColumns found in your .pkl file:")
    print(list(events_df.columns))
    
    print("-" * 40)
    
    # Check for the 'category' column specifically
    if 'category' in events_df.columns:
        print("✅ SUCCESS: The 'category' column is in your model file.")
        print("\nHere's a sample of your category data:")
        print(events_df[['title', 'category']].head())
    else:
        print("❌ ERROR: The 'category' column was NOT found in your model file.")
        print("   This is why it's not showing up in your app.")
        print("\n   To fix this, you MUST run 'model.py' again.")

    print("-" * 40)

except Exception as e:
    print(f"\nAn error occurred while reading the file: {e}")