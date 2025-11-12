# ----------------------------------------------------
# Step 1: Import all the libraries
# ----------------------------------------------------
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time # Good practice to add a small delay

# ----------------------------------------------------
# Step 2: Define the target URL and headers
# ----------------------------------------------------
# This is the new URL for the library calendar
URL = "https://nhfpl.libcal.com/calendar"

# We also need the base URL to fix relative links
BASE_URL = "https://nhfpl.libcal.com" 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# ----------------------------------------------------
# Step 3: Fetch the webpage
# ----------------------------------------------------
print("Fetching NHFPL webpage...")
response = requests.get(URL, headers=HEADERS)

if response.status_code != 200:
    print(f"Error: Failed to fetch page. Status code: {response.status_code}")
    exit()

print("Webpage fetched successfully!")
html_content = response.text

# ----------------------------------------------------
# Step 4: Parse the HTML
# ----------------------------------------------------
soup = BeautifulSoup(html_content, 'html.parser')

# ----------------------------------------------------
# Step 5: Extract the event data (Using the new "map")
# ----------------------------------------------------
all_events_data = []

# This is our new "Event Container" class
event_cards = soup.find_all('div', class_='s-lc-fs-i')
print(f"Found {len(event_cards)} event(s) on the page.")

for card in event_cards:
    try:
        # --- This section is re-mapped ---
        
        # 1. Find the title and link
        # The link tag is inside the h3 tag
        title_tag = card.find('h3', class_='s-lc-fs-i-h-title').find('a')
        title = title_tag.text.strip()
        
        # 2. Get the link URL
        relative_link = title_tag['href']
        # The links on this site are relative (e.g., "/event/12345")
        # We must add the base URL to make them work.
        full_link = BASE_URL + relative_link

        # 3. Find the date
        date = card.find('span', class_='s-lc-fs-i-date-value').text.strip()

        # 4. Find the time
        time = card.find('span', class_='s-lc-fs-i-time-value').text.strip()
        
        # --- End of re-mapped section ---

        # ----------------------------------------------------
        # Step 6: Structure the data as a dictionary
        # ----------------------------------------------------
        event_data = {
            "title": title,
            "date": date,
            "time": time,
            "location": "New Haven Free Public Library", # Add this, as it's not on the card
            "details_url": full_link
        }
        
        all_events_data.append(event_data)

    except AttributeError as e:
        # This will catch any cards that are formatted differently
        # (e.g., "past event" dividers) and skip them.
        print(f"Skipping a non-event card. Error: {e}")
    
    # Be a good web citizen: pause for a tiny moment
    time.sleep(0.1) 

# ----------------------------------------------------
# Step 7: Save the data to a *new* CSV file
# ----------------------------------------------------
if not all_events_data:
    print("No event data was successfully scraped.")
else:
    print(f"\nSuccessfully scraped {len(all_events_data)} events.")
    print("Example event:")
    print(all_events_data[0])
    
    # We save to a new file to keep our data sources separate
    save_path = 'data/nhfpl_events.csv'
    
    df = pd.DataFrame(all_events_data)
    df.to_csv(save_path, index=False)
    
    print(f"\nData saved successfully to {save_path}")