from jobs.workers import worker
from jobs.workers.fb import fb_utils

class FBEmptyAudienceCreate(worker.Worker):
    PARAMS = [
        ('account_id', 'string', True, 'Ads Account Id'),
        ('app_id', 'string', True, 'FB App Id'),
        ('app_secret', 'string', True, 'FB App Secret'),
        ('access_token', 'string', True, 'Access Token'),  # Added comma here
        ('audience_name', 'string', True, 'Audience Name'),
        ('audience_description', 'string', True, 'Audience Description')
    ]
    
    def _execute(self) -> None:
        fb_utils.create_empty_custom_audience_create(
            self._params['account_id'], 
            self._params['app_id'], 
            self._params['app_secret'], 
            self._params['access_token'], 
            self._params['audience_name'], 
            self._params['audience_description']
        )
