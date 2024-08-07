import requests
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import hashlib
import csv

def get_subscription_ids(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        response_json = response.json()
        subscription_ids = [item['attributes']['user_pseudo_id'] for item in response_json['data']]
        return subscription_ids
    else:
        return {"error": "failed to get subscription ids", "status_code": response.status_code, "response": response.json()}

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def hash_value(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest() if value else None

def create_tiktok_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["email_sha256","phone_sha256"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for item in data:
            email = item.get('email')
            phone = item.get('phone')

            writer.writerow({
                "email_sha256": hash_value(email),
                "phone_sha256": hash_value(phone),
            })

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def upload_file(api_url, file_path, headers, params):
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        response = requests.post(api_url, headers=headers, params=params, files=files)
        return response

def send_notification(app_id, subscription_ids, contents_str, headings_str, chrome_web_image, url):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic YWNjMjA4ZWMtZjEzNS00ODk3LTkzYmItMWRlYzVhNDI1ZWZm"
    }

    # Convert input strings to dictionaries
    contents = json.loads(contents_str)
    headings = json.loads(headings_str)
    subscription_arr = get_subscription_ids(subscription_ids)
    
    for chunk in chunk_list(subscription_arr, 1000):
        payload = {
            "app_id": app_id,
            "include_subscription_ids": chunk,
            "contents": contents,
            "headings": headings,
            "chrome_web_image": chrome_web_image,
            "url": url
        }

        response = requests.post('https://onesignal.com/api/v1/notifications', headers=headers, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            push_id = response_json['id']
            status_url = f"https://api.onesignal.com/notifications/{push_id}?app_id={app_id}"
            
            status_response = requests.get(status_url, headers=headers)
            return status_response.json()
        else:
            return {"error": "failed to push notification", "status_code": response.status_code, "response": response.json()}

def send_email(api_id, from_email, from_name, reply_to_email, segment, subject, contents):
    response = requests.get(segment)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch segment data: {response.status_code}")
    segment_data = response.json()
    message = Mail()
    # Initialize the SendGrid client
    sendgrid_client = SendGridAPIClient(api_id)

    # Process each user in the segment data
    for user in segment_data['data']:
        pii_list = user['attributes'].get('pii', [])
        for pii in pii_list:
            email = pii.get('email')
            first_name = pii.get('first_name', '')
            last_name = pii.get('last_name', '')
            if email:  # Only proceed if there is an email address
                # Create a new Mail object for each recipient
                message = Mail(
                    from_email=From(email=from_email, name=from_name),
                    subject=Subject(subject),
                    to_emails=To(email=email, name=f"{first_name} {last_name}".strip())
                )
                if reply_to_email:
                    message.reply_to = ReplyTo(email=reply_to_email)
                message.subject = Subject(subject)
                # # Set the content of the email
                contents_processed = contents.replace('\\"', '"')  # Correct potential escaping issues
                message.content = [Content(mime_type="text/html", content=contents_processed)]
                print(f"Sending email to: {message}")

                # # Send the email
                response = sendgrid_client.send(message)
    return response

def create_custom_audience(advertiser_id, custom_audience_name, segment,token, output_file="/tmp/tiktok_audience.csv"):
    response = requests.get(segment)
    if response.status_code == 200:
        segment_data = response.json()
    else:
        raise Exception(f"Failed to fetch segment data: {response.status_code}")

    # Collecting data for CSV
    data = []
    for user in segment_data['data']:
        pii_list = user['attributes'].get('pii', [])
        for pii in pii_list:
            email = pii.get('email')
            phone = pii.get('phone')
            if email or phone:
                data.append({'email': email, 'phone': phone})

    # Create the CSV file with hashed data
    create_tiktok_csv(data, output_file)
    file_signature = calculate_md5(output_file)
    
    # Prepare the API URL, payload, headers, and file data for the API request
    api_url = "https://business-api.tiktok.com/open_api/v1.3/dmp/custom_audience/file/upload/"  # Replace with actual API URL
    payload = {
        'advertiser_id': advertiser_id,
        'file_signature': file_signature,
        'calculate_type': 'MULTIPLE_TYPES'
    }
    files = {
        'file': (output_file, open(output_file, 'rb'), 'text/csv')
    }
    headers = {
        'Access-Token': token
    }

    # Upload the CSV file
    upload_response = requests.post(api_url, headers=headers, data=payload, files=files)
    if upload_response.status_code == 200:
        response_json = upload_response.json()
        if response_json.get('message') == 'OK':
            file_path = response_json.get('data', {}).get('file_path')
            if file_path:
                url = "https://business-api.tiktok.com/open_api/v1.3/dmp/custom_audience/create/"
                payload = json.dumps({
                    "advertiser_id": advertiser_id,
                    "custom_audience_name": custom_audience_name,
                    "file_paths": [file_path],
                    "calculate_type": "MULTIPLE_TYPES"
                })
                headers = {
                    'Access-Token': token,
                    'Content-Type': 'application/json'
                }
                create_response = requests.post(url, headers=headers, data=payload)
                
                # Delete the CSV file after successful upload
                
                return create_response
        else:
            raise Exception(f"File upload failed with message: {response_json.get('message')}")
    else:
        raise Exception(f"File upload failed with status code: {upload_response.status_code}")  
    return upload_response