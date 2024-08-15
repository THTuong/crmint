from jobs.workers.bigquery import bq_worker
from jobs.workers.google import gg_utils

class GoogleCreateCustomList(bq_worker.BQWorker):
    PARAMS = [
        ('customer_id', 'string', True, '', 'Customer ID'),
        ('name', 'string', True, '', 'Audience Name'),
        ('life_span', 'number', True, '', 'Life Span'),
        ('api_url', 'string', True, '', 'Segment'),
        ('developer_token', 'string', True, '', 'Developer Token'),
        ('refresh_token', 'string', True, '', 'Refresh Token'),
        ('client_id', 'string', True, '', 'Client ID'),
        ('client_secret', 'string', True, '', 'Client Secret')
    ]
    
    def _execute(self) -> None:
        gg_utils.create_google_custom_audience(
            self._params['customer_id'],
            self._params['name'],
            self._params['life_span'],
            self._params['api_url'],
            self._params['developer_token'],
            self._params['refresh_token'],
            self._params['client_id'],
            self._params['client_secret']
        )