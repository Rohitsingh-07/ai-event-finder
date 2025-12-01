import requests
import json

# -----------------------------------------------------------------
# STEP 1: YOUR CAPTURED COOKIES & HEADERS
# -----------------------------------------------------------------
cookies = {
    'MEETUP_BROWSER_ID': 'id=0cae29ee-232c-48a4-be50-02c483737431',
    'MEETUP_TRACK': 'id=699a2153-667e-4d2c-82d3-2cad573d6831',
    'SIFT_SESSION_ID': '15155fc3-3a3c-4f56-8c1b-7f1ae70cf5d1',
    'COOKIE_ID_PICOX_ID': 'fcf333f8-22b3-4195-a6d4-470694136c11',
    'orion_lsid': 'fd276fb6-2814-4467-914d-e26d9c50d793',
    '_fbp': 'fb.1.1764625200122.120167570691195185',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Mon+Dec+01+2025+16%3A40%3A00+GMT-0500+(Eastern+Standard+Time)&version=202309.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=8258ab7e-9b97-40b4-8d1b-bf3c388f0441&interactionCount=0&landingPath=https%3A%2F%2Fwww.meetup.com%2F&groups=C0002%3A1%2CC0001%3A1%2CC0004%3A1%2CC0003%3A1',
    'cjConsent': 'MHxOfDB8Tnww',
    '_scid': 'G4sdqoSe-z8HDqAwRAMonCaQ2Sxsp_aq',
    '_scid_r': 'G4sdqoSe-z8HDqAwRAMonCaQ2Sxsp_aq',
    '_uetsid': '4a48bc00cefe11f08b216f4d904d52e0',
    '_uetvid': '4a48f9a0cefe11f0aded197f3568974d',
    'cjUser': '7f982435-08f0-443a-a60a-b2d743ca3de9',
    '_clck': '1v0xe76%5E2%5Eg1h%5E0%5E2161',
    '_ScCbts': '%5B%22229%3Bchrome.2%3A2%3A5%22%5D',
    '_hjSessionUser_6522278': 'eyJpZCI6IjRmODdmOTEzLWM0MjktNWFhOC05YjEzLTk0NjQyMWZmNDgxYyIsImNyZWF0ZWQiOjE3NjQ2MjUyMDE4OTIsImV4aXN0aW5nIjpmYWxzZX0=',
    '_hjSession_6522278': 'eyJpZCI6IjQ4ZjMwZmFiLWI4OTQtNDFlYS1iZTUzLTg0NWE5NDZkOWFmOSIsImMiOjE3NjQ2MjUyMDE4OTMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=',
    '_hjHasCachedUserAttributes': 'true',
    'g_state': '{"i_l":0,"i_ll":1764625202118,"i_b":"6+wq8hTj1Es1LOX/U5z+dKszhbJi1Lptpf1H52u+G3Q"}',
    'SIFT_SESSION_ID': '15155fc3-3a3c-4f56-8c1b-7f1ae70cf5d1',
    '_sctr': '1%7C1764565200000',
    '__stripe_mid': '88fb9bc7-8ce6-48de-9071-5c93608b5d74f9eea8',
    '__stripe_sid': 'd19891a2-62a2-4716-8be7-f98903661acfdf705f',
    '_clsk': '1by470f%5E1764625202781%5E1%5E1%5Ev.clarity.ms%2Fcollect',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US',
    'apollographql-client-name': 'nextjs-web',
    'content-type': 'application/json',
    'origin': 'https://www.meetup.com',
    'priority': 'u=1, i',
    'referer': 'https://www.meetup.com/',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
}

json_data = {
    'operationName': 'getLocationSearch',
    'variables': {
        'query': 'New',
        'dataConfiguration': '{}',
    },
    'extensions': {
        'persistedQuery': {
            'version': 1,
            'sha256Hash': '9c04de696e6a6697b82523524e59c52448f569689ed93b0821c9ff6437dc2089',
        },
    },
}

print("Testing Meetup API...")

try:
    response = requests.post('https://www.meetup.com/gql2', cookies=cookies, headers=headers, json=json_data)
    
    if response.status_code == 200:
        data = response.json()
        # Pretty print the JSON to see what we got
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Exception: {e}")