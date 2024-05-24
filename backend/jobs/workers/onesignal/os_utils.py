import requests
import json

def send_notification(app_id, subscription_ids, data_str, contents_str, headings_str, image_url, target_url):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic MWZhMjQ3NDQtY2FhMy00MzUzLWIyMzctMDVjYjkyMWJmNzRl"
    }

    # Convert input strings to dictionaries
    data = json.loads(data_str)
    contents = json.loads(contents_str)
    headings = json.loads(headings_str)

    payload = {
        "app_id": app_id,
        "include_subscription_ids": subscription_ids.split(","),
        "data": data,
        "contents": contents,
        "headings": headings,
        "chrome_web_image": image_url,
        "url": target_url
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