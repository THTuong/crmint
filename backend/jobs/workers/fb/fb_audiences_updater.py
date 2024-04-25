from google.cloud import bigquery

from jobs.workers.bigquery import bq_worker
from jobs.workers.fb import fb_utils

class FbAudiencesUpdater(bq_worker.BQWorker):
    """Worker to update FB audiences using values from a BigQuery table."""
    PARAMS = [
        ('audience_id', 'string', True, '',
        'Audience ID'),
        ('app_id', 'string', True, '','FB App Id'),
        ('app_secret', 'string', True, '','FB App Secret'),
        ('access_token', 'string', True, '',
        'Access Token'),
        ('bq_project_id', 'string', False, '', 'BQ Project ID'),
        ('bq_dataset_id', 'string', True, '', 'BQ Dataset ID'),
        ('bq_table_id', 'string', True, '', 'BQ Table ID'),
        ('bq_dataset_location', 'string', False, '', 'BQ Dataset Location'),
        ('schema', 'text', True, '',
        'JSON schema template to update a FB audience'),
        ('data', 'text', True, '',
        'JSON data template to update a FB audience'),
    ]

    def _execute(self) -> None:
        bq_client = self._get_client()
        data_ref = bigquery.DatasetReference(self._params['bq_project_id'], self._params['bq_dataset_id'])
        table_ref = bigquery.TableReference(data_ref, self._params['bq_table_id'])
        patches = fb_utils.get_audience_patches(bq_client, table_ref, self._params['schema'], self._params['data'])
        self.log_info(f'Retrieved #{len(patches)} audience configs from BigQuery')
        fb_utils.update_audience(
            self._params['audience_id'],
            self._params['app_id'],
            self._params['app_secret'],
            self._params['access_token'],
            patches
        )