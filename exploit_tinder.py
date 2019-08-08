import argparse
import json
import os 
import requests
from pathlib import Path

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'X-Auth-Token': '',
    'app-version': '1020358',
    'platform': 'web'
}

TEASERS_URL = 'https://api.gotinder.com/v2/fast-match/teasers'
UNBLURRED_PHOTO_DIR = 'tinder_photos'

parser = argparse.ArgumentParser(
    description='Downloads the unblurred photos of the users that liked your Tinder profile.')
parser.add_argument(
    'X_Auth_Token', help='Your X-Auth-Token. To learn how to get your X-Auth-Token, follow the instructions detailed at the README.md file')

args = parser.parse_args()

HEADERS['X-Auth-Token'] = args.X_Auth_Token

get_profiles = requests.get(TEASERS_URL, headers=HEADERS)

# Check if the request has succeeded
if get_profiles.status_code == 200:
    print('[+] Successfully logged in.')
else:
    exit(
        f'[!] GET failed. The status code is not 200 [{get_profiles.status_code}].\nYour X-Auth-Token is invalid or may have expired.')

# Parse the page response as JSON
try:
    print('[+] Parsing the page response as JSON... ', end='')
    json_resp = json.loads(get_profiles.text)
    print('OK.')
except:
    exit('Failed.')

# Checking if the directory to store photos exists and creating it if not present
if not Path(UNBLURRED_PHOTO_DIR).exists():
    print(f'[+] Creating "{UNBLURRED_PHOTO_DIR}" directory... ', end='')
    Path(UNBLURRED_PHOTO_DIR).mkdir(parents=True)
    print('OK.')

print(f'[+] Entering "{UNBLURRED_PHOTO_DIR}" directory... ', end='')
os.chdir(UNBLURRED_PHOTO_DIR)
print('OK.')

# Iterate over the users that liked your profile
for user in json_resp['data']['results']:
    if not Path(user['user']['_id']).exists():
        print(
            f"  [+] Creating '{user['user']['_id']}' directory... ", end='')
        Path(user['user']['_id']).mkdir()
        print('OK.')

    print(f"  [+] Entering '{user['user']['_id']}' directory... ", end='')
    os.chdir(user['user']['_id'])
    print('OK.')

    # Iterate over the photos of each user
    for photo in user['user']['photos']:
        photo_name = photo['url'].split('/')[-1]

        # Download the photos of a user
        if not Path(photo_name).exists():
            print(f'    [+] Downloading {photo_name}... ', end='', flush=True)
            get_photo = requests.get(photo['url'])
            get_photo.raise_for_status()
            with open(photo_name, 'wb') as fil:
                fil.write(get_photo.content)
            print('OK.')

    print(f"  [+] Exiting '{user['user']['_id']}' directory... ", end='')
    os.chdir('..')
    print('OK.')
