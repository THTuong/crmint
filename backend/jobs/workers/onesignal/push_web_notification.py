from jobs.workers.bigquery import bq_worker
import requests

class PushWebNotification(bq_worker.BQWorker):
    """Worker to update FB audiences using values from a BigQuery table."""
    PARAMS = [
        ('app_id', 'string', True, '634a14e3-11d3-48a5-bea6-42dcbcaf69b1', 'Audience ID'),
        ('include_subscription_ids', 'string', True, '', 'Subscription IDs'),
        ('contents', 'string', True, '', 'Content of notification'),
        ('image', 'string', True, '', 'Image of notification'),
        ('url', 'string', True, '', 'URL of notification')
    ]

    def _execute(self) -> None:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic MWZhMjQ3NDQtY2FhMy00MzUzLWIyMzctMDVjYjkyMWJmNzRl"
        }
        
        payload = {
            "app_id": self._params['app_id'],
            "include_external_user_ids": self._params['include_subscription_ids'].split(','),  # Assuming subscription IDs are comma-separated
            "contents": {"en": self._params['contents']},
            "headings": {"en": "Your Notification Title"},
            "image": self._params['image'],
            "url": self._params['url']
        }
        response = requests.post('https://onesignal.com/api/v1/notifications', headers=headers, json=payload)
        self.log_info(response)