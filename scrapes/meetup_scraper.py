import requests
import pandas as pd
import json

# -----------------------------------------------------------------
# STEP 1: COOKIES AND HEADERS (From your cURL)
# -----------------------------------------------------------------
cookies = {
    'MEETUP_BROWSER_ID': 'id=0cae29ee-232c-48a4-be50-02c483737431',
    'MEETUP_TRACK': 'id=699a2153-667e-4d2c-82d3-2cad573d6831',
    # ... (The rest of your cookies are handled automatically by requests if we copy them all, 
    # but for clarity/stability, we often just need the headers)
}

headers = {
    'accept': '*/*',
    'content-type': 'application/json',
    'origin': 'https://www.meetup.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    # ... (Other headers from your cURL)
}

# -----------------------------------------------------------------
# STEP 2: THE GRAPHQL PAYLOAD
# -----------------------------------------------------------------
# This is the query structure Meetup expects
json_data = {
    'operationName': 'getLocationSearch',
    'variables': {
        'query': 'Connecticut', # We changed "New" to "Connecticut"
        'dataConfiguration': '{}',
    },
    'extensions': {
        'persistedQuery': {
            'version': 1,
            'sha256Hash': '9c04de696e6a6697b82523524e59c52448f569689ed93b0821c9ff6437dc2089',
        },
    },
}

print("Fetching Meetup data...")

try:
    response = requests.post(
        'https://www.meetup.com/gql2', 
        cookies=cookies, 
        headers=headers, 
        json=json_data,
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        
        # -----------------------------------------------------------------
        # STEP 3: PARSE THE RESPONSE
        # -----------------------------------------------------------------
        # We need to find where the events are hidden in this GraphQL response.
        # Based on the query name 'getLocationSearch', this might return LOCATIONS, not events.
        # Let's inspect the data first to be sure.
        
        print("Successfully fetched data!")
        
        # Save raw JSON to inspect it (Debugging step)
        with open('meetup_debug.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Saved raw response to 'meetup_debug.json'. Please check this file!")
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"An error occurred: {e}")