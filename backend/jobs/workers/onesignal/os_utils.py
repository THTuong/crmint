import requests
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

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

def send_email(api_id, from_email, from_name, reply_to_email, subject, contents):
    segment = {
        "data": [
            {
                "id": 28,
                "attributes": {
                    "user_pseudo_id": "1720789419",
                    "createdAt": "2024-07-16T09:55:01.920Z",
                    "updatedAt": "2024-07-19T03:49:45.276Z",
                    "pii": [
                        {
                            "id": 2,
                            "email": "haituong0101987@gmail.com",
                            "first_name": "Tuong",
                            "last_name": "Tran"
                        }
                    ]
                }
            },
            {
                "id": 32,
                "attributes": {
                    "user_pseudo_id": "1720548553",
                    "createdAt": "2024-07-16T09:56:19.513Z",
                    "updatedAt": "2024-07-19T03:56:23.449Z",
                    "pii": [
                        {
                            "id": 4,
                            "email": "haituong1703@gmail.com",
                            "first_name": "Hai",
                            "last_name": "Tuong"
                        }
                    ]
                }
            },
        ],
        "meta": {
            "pagination": {
            "page": 1,
            "pageSize": 25,
            "pageCount": 1,
            "total": 3
            }
        }
    }
    message = Mail()
    to_emails = []
    for user in segment['data']:
        pii_list = user['attributes']['pii']
        if pii_list:
            for pii in pii_list:
                email = pii.get('email')
                first_name = pii.get('first_name', '')
                last_name = pii.get('last_name', '')
                if email:
                    to_emails.append(To(email=email, name=f"{first_name} {last_name}".strip()))
    message.to = to_emails
    
    # Extract email addresses from the segment
    message.from_email = From(email=from_email, name=from_name)
    if(reply_to_email):
        message.reply_to = ReplyTo(email=reply_to_email)
    message.subject = Subject(subject)
    contents = contents.replace('\\"', '"')
    message.content = [Content(mime_type="text/html", content=contents)]

    sendgrid_client = SendGridAPIClient(api_id)
    response = sendgrid_client.send(message)
    return response