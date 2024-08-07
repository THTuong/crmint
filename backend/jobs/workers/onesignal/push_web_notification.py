from jobs.workers.bigquery import bq_worker
from jobs.workers.onesignal import os_utils

class PushWebNotification(bq_worker.BQWorker):
    PARAMS = [
        ('app_id', 'string', True, 'fb5bd557-43ac-4655-a295-e009908a8b06', 'App ID'),
        ('include_subscription_ids', 'string', True, '', 'Subscription IDs'),
        ('contents', 'text', True, '', 'Content of notification'),
        ('chrome_web_image', 'string', True, '', 'Image of notification'),
        ('headings_str', 'text', True, '', 'Title of notification'),
        ('url', 'string', True, '', 'URL of notification')
    ]

    def _execute(self) -> None:
        os_utils.send_notification(self._params['app_id'],
            self._params['include_subscription_ids'],
            self._params['contents'],self._params['headings_str'],
            self._params['chrome_web_image'],self._params['url'])