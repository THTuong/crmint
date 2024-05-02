# Copyright 2020 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CRMint's worker executing Standard SQL scripts in BigQuery."""

from typing import Optional

from jobs.workers.bigquery import bq_utils
from jobs.workers.bigquery import bq_worker
import json
import requests

class BQScriptExecutor(bq_worker.BQWorker):
  """Worker to run SQL scripts in BigQuery.

  We expect the given SQL script to contain all the necessary logic to
  create, alter, and delete resources, such as tables, views, user-defined
  functions (UDFs), and row-level access policies. This can be achieved using
  Data Definition Language (DDL) statements in standard SQL.

  For example, to store query results in a table you can use the
  `CREATE OR REPLACE TABLE ...` statement, more details in the documentation:
  https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language#create_table_statement.

  You can read about the available DDL statements in the BigQuery documentation:
  https://cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language.
  """

  PARAMS = [
      ('script', 'sql', True, '', 'SQL script'),
      ('bq_dataset_location', 'string', False, None, ('BQ Dataset Location '
                                                      '(optional)')),
  ]

  def execute_script(self,
                     script: str,
                     location: Optional[str] = None) -> None:
    """Runs a SQL script.

    Args:
      script: String containing the SQL script in the standard SQL dialect.
      location: Optional string representing the location where to run the job.
      dry_run: Boolean Whether to test the total bytes processed only.
    """
    client = self._get_client()
    job = client.query(script,location=location,job_id_prefix=self._get_prefix())
    self._wait(job)
    results = job.result()
    for row in results:
      data = json.loads(json.loads(row.pipeline))
      requests.post('https://qwiklabs-gcp-01-2fcae7a3b1d9.as.r.appspot.com/api/pipelines/import', json=data)
  def _execute(self) -> None:
    self.execute_script(self._params['script'],
                        self._params['bq_dataset_location'])