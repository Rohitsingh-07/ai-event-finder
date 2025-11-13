import requests
import json # Import json for pretty printing

# -----------------------------------------------------------------
# YOUR WORKING COOKIES, HEADERS, PARAMS, PAYLOAD
# -----------------------------------------------------------------

cookies = {
    'stableId': '6f8617a2-14e6-4f02-9411-4173a935953c',
    'guest': 'identifier%3D7799f31a-2f50-494b-bc7d-ebee43a05cfb%26a%3D13f1%26s%3D63522b5c27a0d78b9d900c01eda083867e3ab8ced28814d7aec5dcf033133b2f',
    'G': 'v%3D2%26i%3D7799f31a-2f50-494b-bc7d-ebee43a05cfb%26a%3D13f1%26s%3D5db8c90d85a87f2bcbce5375bfe05a4b0eee0c1c',
    'eblang': 'lo%3Den_US%26la%3Den-us',
    'mgref': 'eafil',
    'csrftoken': '0eaae89e1fa411f0b711ff221839204c',
    '_hp2_props.1404198904': '%7B%7D',
    'IR_PI': '77be4a34-1705-11f0-88a0-9b6dfbd14725%7C1745344994484',
    'ebEventToTrack': '',
    'AN': '',
    '_gcl_au': '1.1.419380958.1762927415',
    '__spdt': '9b420a15fcb446c290e6a932e9c65551',
    '_tt_enable_cookie': '1',
    '_ttp': '01K9VAK426NH2G28GYX3G559Y7_.tt.1',
    '_pin_unauth': 'dWlkPU16RTFNakJtTURBdFlqZzFNUzAwTTJNMkxXSmlNRGd0WWpFMk1tRmhNbVExTmpkbQ',
    '_fbp': 'fb.1.1762927416660.98732095680540312',
    '_cs_c': '0',
    'tcm': '{"purposes":{"SaleOfInfo":"Auto","Functional":"Auto","Analytics":"Auto","Advertising":"Auto"},"timestamp":"2025-11-12T06:03:35.026Z","confirmed":false,"prompted":false,"updated":false}',
    'hubspotutk': '5012ca7a00283b1f77042b2faf4dd941',
    'location': '{%22current_place%22:%22Connecticut%22%2C%22current_place_parent%22:%22U.S.%22%2C%22country%22:%22United%20States%22%2C%22latitude%22:41.580163%2C%22longitude%22:-72.756629%2C%22slug%22:%22united-states--connecticut%22%2C%22place_type%22:%22region%22%2C%22place_id%22:%2285688629%22%2C%22is_online%22:false}',
    'SS': 'AE3DLHSFE4XJHy6HqJtaAr18RD2ME8JyXw',
    'AS': 'fa211bfa-db40-401d-9d0d-1a0ba0303687',
    '_gid': 'GA1.2.1688157392.1763068110',
    '_ga_TQVES5V6SH': 'GS2.1.s1763068111$o3$g0$t1763068111$j60$l0$h0',
    '_ga': 'GA1.1.1251841201.1762927415',
    '_hp2_id.1404198904': '%7B%22userId%22%3A%225836808813787335%22%2C%22pageviewId%22%3A%226914038307705613%22%2C%22sessionId%22%3A%222603128313681845%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D',
    'IR_gbd': 'eventbrite.com',
    'IR_21676': '1763068111707%7C0%7C1763068111707%7C%7C',
    '_uetsid': 'e8c165b0c0d411f0afd31fd1c66a1e4b',
    '_uetvid': '368fe490a14211ef83dab32e01022cca',
    '_cs_id': '8e2b0543-0636-a6e4-c7b4-69280d1b494a.1762927416.5.1763068111.1763068111.1751381409.1797091416917.1.x',
    '__hstc': '195498867.5012ca7a00283b1f77042b2faf4dd941.1762927417066.1762968119314.1763068112252.3',
    '__hssrc': '1',
    '__hssc': '195498867.1.1763068112252',
    '_hp2_ses_props.1404198904': '%7B%22ts%22%3A1763068111699%2C%22d%22%3A%22www.eventbrite.com%22%2C%22h%22%3A%22%2Fd%2Funited-states--connecticut%2Fall-events%2F%22%7D',
    'SP': 'AGQgbbkVN5Gl2dCSGvhkoWOnS4Vk8z3nUksvGBnuUUM2jWLuNsuU1dMdsfKsYu4ykky87B8lOAiBldolaZ8N3weJ9Zdw3XCY9chGfK08pHTG5n2phlo00ANvzqP9kALifytiAM88TNxhr14b6FGRd6QYgUEgiIIFlkZHk2dhVCtNZQJmu_uHFWrOogq9HbDNdk_wvzg0V4jM0im65QFw1EyWO_6bL24oeNXoMyIfRz-OJTCHWpXmcnU',
    'session': 'identifier%3D85f23eda1cae447fbc297c17f581ed89%26issuedTs%3D1763068121%26originalTs%3D1763068109%26s%3D5c7c02e837120e2e4e5a73332b8a63117c46a6b6948155157a6baf53373177a7',
    '_cs_s': '1.0.U.9.1763069942872',
    '_dd_s': 'rum=0&expire=1763069056922',
    'ttcsid': '1763068111937::5IdmzLb_uLdPMXDxqx0W.3.1763068156932.0',
    'ttcsid_C3DHGPITO1NMNN16MDBG': '1763068111937::tuUtMQ9d9uypHYGpFpYE.3.1763068156932.0',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6',
    'content-type': 'application/json',
    'origin': 'https://www.eventbrite.com',
    'priority': 'u=1, i',
    'referer': 'https://www.eventbrite.com/d/united-states--connecticut/all-events/',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'x-csrftoken': '0eaae89e1fa411f0b711ff221839204c',
    'x-requested-with': 'XMLHttpRequest',
}

params = {
    'stable_id': '6f8617a2-14e6-4f02-9411-4173a935953c',
}

base_json_data = {
    'event_search': {
        'dates': 'current_future',
        'dedup': True,
        'places': [
            '85688629', # This is the ID for "Connecticut"
        ],
        'page': 1, # We will start at page 1
        'page_size': 20,
        'aggs': [
            'places_borough',
            'places_neighborhood',
        ],
        'online_events_only': False,
    },
    'expand.destination_event': [
        'primary_venue',
        'image',
        'ticket_availability',
        'saves',
        'event_sales_status',
        'primary_organizer',
        'public_collections',
    ],
    'debug_experiment_overrides': {
        'search_exp_4': 'A',
    },
    'browse_surface': 'search',
}

url = 'https://www.eventbrite.com/api/v3/destination/search/'

# -----------------------------------------------------------------
# STEP 2: DEBUG REQUEST
# -----------------------------------------------------------------
print("--- Starting DEBUG scraper ---")
print("Fetching page 1...")

# Set payload for page 1
payload = base_json_data.copy()
payload['event_search']['page'] = 1

try:
    response = requests.post(
        url, 
        params=params,
        json=payload,
        cookies=cookies, 
        headers=headers,
        timeout=10
    )

    if response.status_code == 200:
        print("Successfully fetched data. Printing JSON response:")
        data = response.json()
        # Use json.dumps for pretty printing
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: Failed to fetch page 1. Status code: {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"A connection error occurred: {e}")