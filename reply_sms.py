import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import subprocess
import csv
import time
import datetime

# Load environment variables
load_dotenv()

with open('private-key.pem', 'r') as file:
    private_key = file.read()

# Set up credentials using environment variables
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = {
    "type": os.getenv("GOOGLE_SERVICE_ACCOUNT_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    # "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("GOOGLE_PRIVATE_KEY") else None,
    "private_key": private_key,
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
}
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
client = gspread.authorize(creds)

# Replace with your actual Google Spreadsheet IDs and ranges
SPREADSHEET_ID_SEND = '1Q_yDUxr12gGxAYdbFtxyl0zwVQHn8Lc592Ss-eo-F9Y'
SPREADSHEET_ID_RECEIVE = '1a3NxzLS6wUCXVVLacS0_yFZcTS6MvdAr7preu_wq25M'
RANGE_NAME_SEND = 'Sheet1!A:A'
RANGE_NAME_RECEIVE = 'Sheet1!A:H'  # Include additional columns for date

def fetch_sheet_data(client, spreadsheet_id, range_name):
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(range_name.split('!')[0])
    values = worksheet.get(range_name.split('!')[1])
    return values

def append_sheet_data(client, spreadsheet_id, range_name, values):
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(range_name.split('!')[0])
    worksheet.append_rows(values)
    return

def convert_timestamp(timestamp_ms):
    timestamp_s = timestamp_ms / 1000.0
    readable_datetime = datetime.datetime.fromtimestamp(timestamp_s)
    return readable_datetime.strftime('%Y-%m-%d %H:%M:%S')

def get_latest_exported_date():
    try:
        with open('./data/sms_exported.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header
            latest_date = 0
            for row in csv_reader:
                date_str = row[2]
                date_timestamp = int(datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                if date_timestamp > latest_date:
                    latest_date = date_timestamp
            return latest_date
    except FileNotFoundError:
        return 0

def export_sms_to_csv(phone_number):
    adb_command = r"""adb shell content query --uri content://sms/inbox --projection address,body,date --where \"address='{}'\"""".format(phone_number)
    try:
        result = subprocess.run(adb_command, capture_output=True, text=True, shell=True)
        output_lines = result.stdout.strip().split('Row')
        with open('./data/sms_exported.csv', 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['address', 'body', 'date'])  # Write headers
            for line in output_lines:
                if line.startswith(': '):
                    parts = line.split(', ')
                    if len(parts) >= 3:
                        address = parts[0].split('=')[1].strip().strip('+')
                        body = parts[1].split('=')[1].strip()
                        date = int(parts[2].split('=')[1].strip())
                        date = convert_timestamp(date)
                        csv_writer.writerow([address, body, date])
        
        print("Initial SMS export to CSV completed.")
        monitor_new_messages(client, phone_number)
    except subprocess.CalledProcessError as e:
        print(f"Error executing adb command: {e}")

def monitor_new_messages(client, phone_number):
    sent_numbers = fetch_sheet_data(client, SPREADSHEET_ID_SEND, RANGE_NAME_SEND)
    sent_numbers = {str(row[0]) for row in sent_numbers}

    while True:
        latest_exported_date = get_latest_exported_date()
        adb_command = r"""adb shell content query --uri content://sms/inbox --projection address,body,date --where \"address='{}'\"""".format(phone_number)
        result = subprocess.run(adb_command, capture_output=True, text=True, shell=True)
        output_lines = result.stdout.strip().split('Row')

        with open('./data/sms_exported.csv', 'a', newline='', encoding='utf-8') as export_file:
            csv_writer = csv.writer(export_file)
            for line in output_lines:
                if line.startswith(': '):
                    parts = line.split(', ')
                    if len(parts) >= 3:
                        date = int(parts[2].split('=')[1].strip())
                        date = convert_timestamp(date)
                        date_timestamp = int(datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
                        if date_timestamp > latest_exported_date:
                            address = parts[0].split('=')[1].strip().strip('+')
                            body = parts[1].split('=')[1].strip()

                            lines = body.splitlines()
                            number, cellid, lat, long, timeofshutdown, typeofloc, imei, imsi = "", "", "", "", "", "", "", ""
                            for line in lines:
                                if "MSISDN" in line:
                                    number = line.strip().split(" ")[1]
                                elif "Cell ID" in line:
                                    cellid = line.strip().split(" ")[2]
                                elif "Lat" in line:
                                    lat = line.strip().split(" ")[1]
                                elif "Long" in line:
                                    long = line.strip().split(" ")[1]
                                elif "LBS Dttm" in line:
                                    timeofshutdown = line.strip().split(" ")[2] + " " + line.strip().split(" ")[3].strip(";")
                                    try:
                                        typeofloc = (line.strip().split(" ")[4].strip()).strip("\"")
                                    except:
                                        typeofloc = ""
                                elif "Subscriber not latched or switched off" in line.strip():
                                    typeofloc = "OFF"
                                elif "IMEI" in line:
                                    imei = line.strip().split(" ")[1]
                                elif "IMSI" in line:
                                    try:
                                        imsi = line.strip().split(" ")[1]
                                    except:
                                        imsi = ""

                            number = number[2:]
                            date_str = convert_timestamp(date_timestamp)
                            today_date = datetime.datetime.now().strftime('%Y-%m-%d')

                            if number in sent_numbers:
                                new_row = [number, cellid, f"{lat},{long}", typeofloc, timeofshutdown, imei, imsi, today_date]
                                append_sheet_data(client, SPREADSHEET_ID_RECEIVE, RANGE_NAME_RECEIVE, [new_row])
                                print(f"New message processed: {new_row}")

                            csv_writer.writerow([address, body, date_str])
                            print(f"New message received: Address={address}, Body={body}, Date={date_str}")

        time.sleep(10)

def main():
    # phone_number = "+917021265165"  # Replace with the actual phone number
    phone_number = os.getenv("PHONE_NUMBER")
    export_sms_to_csv(phone_number)

if __name__ == '__main__':
    main()