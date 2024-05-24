from jobs.workers.bigquery import bq_worker
import requests

class PushWebNotification(bq_worker.BQWorker):
    """Worker to update FB audiences using values from a BigQuery table."""
    PARAMS = [
        ('app_id', 'string', True, '634a14e3-11d3-48a5-bea6-42dcbcaf69b1', 'Audience ID'),
        ('include_subscription_ids', 'text', True, '', 'Subscription IDs'),
        ('contents', 'text', True, '', 'Content of notification'),
        ('image', 'string', True, '', 'Image of notification'),
        ('url', 'string', True, '', 'URL of notification')
    ]

    def _execute(self) -> None:
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "app_id": self._params['app_id'],
            "include_external_user_ids": self._params['include_subscription_ids'].split(','),  # Assuming subscription IDs are comma-separated
            "contents": {"en": self._params['contents']},
            "headings": {"en": "Your Notification Title"},
            "image": self._params['image'],
            "url": self._params['url']
        }
        
        try:
            response = requests.post('https://onesignal.com/api/v1/notifications', headers=headers, json=payload)
            response.raise_for_status()  # Raise an HTTPError if the response was an unsuccessful status code
            print(f"Notification sent successfully: {response.json()}")
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"An Error Occurred: {err}")