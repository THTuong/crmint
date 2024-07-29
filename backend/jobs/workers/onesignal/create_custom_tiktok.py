from jobs.workers.bigquery import bq_worker
from jobs.workers.onesignal import os_utils

class CreateCustomAudience(bq_worker.BQWorker):
    PARAMS = [
        ('advertiser_id', 'string', True, '', 'Advertiser ID'),
        ('custom_audience_name', 'string', True, '', 'Audience Name'),
        ('segment', 'string', True, '', 'Segment')
        ('token', 'string', True, '', 'Token')
    ]
    
    def _execute(self) -> None:
        os_utils.send_email(
            self._params['advertiser_id'],
            self._params['custom_audience_name'],
            self._params['segment'],self._params['token'])