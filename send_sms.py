import requests
import time
from ppadb.client import Client as AdbClient

# Connect to ADB server
adb_client = AdbClient(host="127.0.0.1", port=5037)
device = adb_client.devices()[0]

# Google Sheets setup
API_KEY = 'AIzaSyCxrvxY0Nmf5txZwCIuTBWEEIw7HVC8bro'  # Replace with your API key
SPREADSHEET_ID = '1Q_yDUxr12gGxAYdbFtxyl0zwVQHn8Lc592Ss-eo-F9Y'#all numbers  # Replace with your Google Spreadsheet ID
# SPREADSHEET_ID = '1eDQNGhNQY1PR7iPGneQNG8XIzmjBASxEJ2WG4T0oSTs' # shortlisted numbers location
RANGE_NAME = 'Sheet1!A:A'  # Replace with the specific cell range you want to read from

# Construct the URL to access the Google Sheets API
url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}?key={API_KEY}'
print(url)
# print(url)

# Make the request to the Google Sheets API
response = requests.get(url)
result = response.json()
if 'values' not in result:
    print('No data found.')
    phone_number = None
else:
    a=0
    phone_number = 917021265165
    for values in result['values']:
        for value in values:
            if(value and value.isnumeric() ):
                a=a+1
                message = f"91{value}"
                print(message)
                device.shell(f'am start -n com.google.android.apps.messaging/.ui.conversation.LaunchConversationActivity -a android.intent.action.SENDTO -d sms:+{phone_number} --es sms_body "{message}" --ez exit_on_sent true')
                time.sleep(5)
                device.shell('input tap 645 1453')
                # device.shell('input tap 964 2200')
                print(a)
                time.sleep(53)

# am start -a android.intent.action.SENDTO -d sms:{phone_number} --es sms_body "{message}" --ez exit_on_sent true