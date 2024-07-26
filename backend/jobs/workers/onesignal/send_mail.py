from jobs.workers.bigquery import bq_worker
from jobs.workers.onesignal import os_utils

class SendMail(bq_worker.BQWorker):
    PARAMS = [
        ('api_id', 'string', True, '', 'Send Grid API'),
        ('from_email', 'string', False, '', 'From Email'),
        ('from_name', 'string', False, '', 'From Name'),
        ('reply_to_email', 'string', False, '', 'Reply Email'),
        ('segment_id', 'string', False, '', 'Segment ID'),
        ('segment', 'string', False, '', 'Segment'),
        ('subject', 'string', False, '', 'Subject of email'),
        ('contents', 'text', False, '', 'Content of email'),
        ('time_schedule', 'text', False, '', 'Time Schedule')
    ]
    
    def _execute(self) -> None:
        os_utils.send_email(
            self._params['api_id'],
            self._params['from_email'],
            self._params['from_name'],self._params['reply_to_email'],
            self._params['segment'],
            self._params['subject'],self._params['contents'])