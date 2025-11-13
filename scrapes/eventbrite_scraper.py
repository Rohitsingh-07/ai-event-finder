import requests
import pandas as pd
import time

# -----------------------------------------------------------------
# STEP 1: YOUR COOKIES AND HEADERS
# This is the original, working configuration
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
    'SS': 'AE3DLHTguMArw88gNHZxD8zUPqB8SiN6uw',
    'AN': '',
    'AS': '20750610-7ab6-49ac-8f66-fc591997795c',
    '_gid': 'GA1.2.1197275584.1762927415',
    '_gcl_au': '1.1.419380958.1762927415',
    'IR_gbd': 'eventbrite.com',
    '__spdt': '9b420a15fcb446c290e6a932e9c65551',
    '_tt_enable_cookie': '1',
    '_ttp': '01K9VAK426NH2G28GYX3G559Y7_.tt.1',
    '_pin_unauth': 'dWlkPU16RTFNakJtTURBdFlqZzFNUzAwTTJNMkxXSmlNRGd0WWpFMk1tRmhNbVExTmpkbQ',
    '_fbp': 'fb.1.1762927416660.98732095680540312',
    '_cs_c': '0',
    '_hp2_ses_props.1404198904': '%7B%22ts%22%3A1762927416826%2C%22d%22%3A%22www.eventbrite.com%22%2C%22h%22%3A%22%2Fd%2Fct--west-haven%2Fevents%2F%22%7D',
    'tcm': '{"purposes":{"SaleOfInfo":"Auto","Functional":"Auto","Analytics":"Auto","Advertising":"Auto"},"timestamp":"2025-11-12T06:03:35.026Z","confirmed":false,"prompted":false,"updated":false}',
    '__hstc': '195498867.5012ca7a00283b1f77042b2faf4dd941.1762927417066.1762927417066.1762927417066.1',
    'hubspotutk': '5012ca7a00283b1f77042b2faf4dd941',
    '__hssrc': '1',
    'location': '{%22current_place%22:%22Connecticut%22%2C%22current_place_parent%22:%22U.S.%22%2C%22country%22:%22United%20States%22%2C%22latitude%22:41.580163%2C%22longitude%22:-72.756629%2C%22slug%22:%22united-states--connecticut%22%2C%22place_type%22:%22region%22%2C%22place_id%22:%2285688629%22%2C%22is_online%22:false}',
    'SP': 'AGQgbbkap2MNH8dDue9W8Om76RBh8Qe_ctLlqnUnIEw_-maBcehQJ0a7-A-QRo6VA6TLcTMLYt73DDBGReDvWFEtY-CuVe2n5-NO2hleG1mN0GFdnGS7Xd3wnkskTap8GZlWgy2JmoPi-8oLjj7zyIshgZcVeMaNPlypyh7EGEaP8UfppyZ5qP3lUM7lIYlEyDNAAwtipCmudmA872r8OZealeeTb73pASBXWt89ZHVYSqMvVtnBAQ',
    'session': 'identifier%3D34415c3ee2bc411d8763052e9bd37f12%26issuedTs%3D1762929382%26originalTs%3D1762927413%26s%3Dc8c2ab0171bfa83bf08e04a50a634a41176a69baf45256bb47ebbc9b59093671',
    '_ga_TQVES5V6SH': 'GS2.1.s1762927416$o1$g1$t1762929385$j58$l0$h0',
    '_ga': 'GA1.1.1251841201.1762927415',
    '_hp2_id.1404198904': '%7B%22userId%22%3A%225836808813787335%22%2C%22pageviewId%22%3A%228022548442199499%22%2C%22sessionId%22%3A%228750206208241354%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D',
    'IR_21676': '1762929385622%7C0%7C1762929385622%7C%7C',
    'ttcsid_C3DHGPITO1NMNN16MDBG': '1762927415370::GaUlWxSi-aeivVpSjh9b.1.1762929385900.0',
    'ttcsid': '1762927415370::AuBpczaDH8L6CQ6Mjcl6.1.1762929385900.0',
    '_cs_id': '8e2b0543-0636-a6e4-c7b4-69280d1b494a.1762927416.1.1762929386.1762927416.1751381409.1797091416917.1.x',
    '__hssc': '195498867.6.1762927417066',
    '_uetsid': '5317d600bf8d11f0a1b305a5a360cee6',
    '_uetvid': '368fe490a14211ef83dab32e01022cca',
    '_dd_s': 'rum=0&expire=1762930286876',
    '_cs_s': '12.0.U.9.1762931186915',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6',
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

# -----------------------------------------------------------------
# STEP 2: MAKE THE ORIGINAL, WORKING REQUEST
# -----------------------------------------------------------------
print("--- Starting stable scraper ---")
print("Fetching 20 events...")

try:
    # This is your original GET request with the hardcoded event IDs
    response = requests.get(
        'https://www.eventbrite.com/api/v3/destination/events/?event_ids=1549842654099,1320078683879,1388545209099,1364385456629,1607418414749,1712166208219,1871457773579,1512708284199,1617757408959,1355200343709,1867120400379,1657055811539,1777673512329,1702065195819,1708736800769,1510992211379,1791962430869,1758351419429,1731624638909,1626462124999&page_size=20&expand=event_sales_status,image,primary_venue,saves,ticket_availability,primary_organizer,public_collections',
        cookies=cookies,
        headers=headers,
        timeout=10
    )

    all_events_data = [] # Create an empty list to store results

    if response.status_code == 200:
        data = response.json()
        
        # This is the path we know works for this response
        event_list = data['events']
        
        print(f"--- Found {len(event_list)} events. Processing... ---")
        
        # Loop through each event in the list
        for event in event_list:
            try:
                # Extract the data using the keys
                title = event['name']
                summary = event.get('summary', 'No summary provided.')
                event_url = event['url']
                start_date = event['start_date']
                start_time = event['start_time']
                full_datetime = f"{start_date}T{start_time}"

                # Location is nested
                venue = event.get('primary_venue')
                if venue:
                    location_name = venue.get('name', 'N/A')
                    if 'address' in venue and venue['address']:
                        address = venue['address'].get('localized_address_display', 'Address not specified')
                    else:
                        address = "Address not specified"
                else:
                    location_name = "Online Event"
                    address = "Online"

                # Create a dictionary for this one event
                event_data = {
                    "title": title,
                    "datetime": full_datetime,
                    "location_name": location_name,
                    "address": address,
                    "description": summary,
                    "source_url": event_url,
                    "source_site": "Eventbrite"
                }
                
                # Add this dictionary to our main list
                all_events_data.append(event_data)

            except Exception as e:
                print(f"\nWarning: Could not parse an event. Error: {e}\n")

    else:
        print(f"Error: Failed to fetch data. Status code: {response.status_code}")
        print("Response Text:", response.text)

except requests.exceptions.RequestException as e:
    print(f"A connection error occurred: {e}")

# -----------------------------------------------------------------
# STEP 3: SAVE ALL DATA TO CSV
# -----------------------------------------------------------------
if all_events_data:
    print(f"\nSuccessfully processed {len(all_events_data)} events in total.")
    
    df = pd.DataFrame(all_events_data)
    save_path = 'data/eventbrite_events.csv'
    
    try:
        df.to_csv(save_path, index=False, encoding='utf-8')
        print(f"--- Data saved successfully to {save_path} ---")
    except PermissionError:
        print(f"\n[ERROR] Permission denied. Is '{save_path}' open in Excel?")
    
else:
    print("No events were processed.")