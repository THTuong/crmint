from jobs.workers.bigquery import bq_worker
from jobs.workers.onesignal import os_utils
import requests

class PushWebNotification(bq_worker.BQWorker):
    """Worker to update FB audiences using values from a BigQuery table."""
    PARAMS = [
        ('app_id', 'string', True, '634a14e3-11d3-48a5-bea6-42dcbcaf69b1', 'App ID'),
        ('include_subscription_ids', 'string', True, '', 'Subscription IDs'),
        ('contents', 'text', True, '', 'Content of notification'),
        ('chrome_web_image', 'string', True, '', 'Image of notification'),
        ('headings', 'text', True, '', 'Title of notification'),
        ('url', 'string', True, '', 'URL of notification')
    ]

    def _execute(self) -> None:
        os_utils.send_notification(self._params['app_id'],
            self._params['include_subscription_ids'],
            self._params['contents'],
            self._params['chrome_web_image'],self._params['headings'],self._params['url'])