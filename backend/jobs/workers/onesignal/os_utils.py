import requests
import json

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