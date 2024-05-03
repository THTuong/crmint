from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from google.cloud import bigquery
from typing import NewType, TypeVar
import string
import json
from backend.controller import models

#Define some variable
class AudienceOperationBase:
  """Abtract class for operation on audiences."""


Audience = NewType('Audience', dict)
AudiencePatch = NewType('AudiencePatch', dict)
AudienceOperation = TypeVar('AudienceOperation', bound=AudienceOperationBase)

#Init Facebook API
def init_facebook_api(app_id: str, app_secret: str, access_token: str) -> None:
    """Initialize the Facebook API client."""
    FacebookAdsApi.init(app_id, app_secret, access_token)

#Create a empty custom audience
def create_empty_custom_audience(account_id: str, app_id: str, app_secret: str, access_token: str, audience_name: str, audience_description: str) -> None:
    """Creates an empty custom audience using Facebook API.
    Args:
    account_id: The account id of the Facebook ads account
    access_token: The access token of the Facebook developer app
    app_secret: The app secret of the Facebook developer app
    app_id: The app id of the Facebook developer app
    audience_name: The name of the audience to create
    audience_description: A description of the audience
    """
    try:
        init_facebook_api(app_id, app_secret, access_token)
        ad_account = AdAccount(f'act_{account_id}')
        params = {
            'name': audience_name,
            'subtype': 'CUSTOM',
            'description': audience_description,
            'customer_file_source': 'USER_PROVIDED_ONLY'
        }
        audience = ad_account.create_custom_audience(params=params)
        print(f'Created empty custom audience with ID: {audience["id"]}')
    except FacebookRequestError as e:
        print(f'Error creating custom audience: {e}')

#Get patch of data
def get_audience_patches(bq_client: bigquery.Client, table_ref: bigquery.TableReference, schema: str,data: str) -> list[AudiencePatch]:
    """Return a list of audience from an existing BigQuery table.
    Args:
    bq_client: BigQuery client
    table_ref: Reference to a BigQuery table.
    template: JSON string for Audience API body.
    """
    patches = {
        'payload': {
            'schema': json.loads(schema),
            'data': []
        }
    }
    rows = bq_client.list_rows(table_ref)
    data_template = string.Template(data)
    for row in rows:
        patch = data_template.substitute(row)
        patches['payload']['data'].append(json.loads(patch))
    return patches

#Update audience
def update_audience(app_id: str, app_secret: str, access_token: str, audience_id: str, patches: list[AudiencePatch]) -> None:
    """Creates an empty custom audience using Facebook API.
    Args:
    audience_id: The audience ID
    app_id: The app id of the Facebook developer app
    app_secret: The app secret of the Facebook developer app
    access_token: The access token of the Facebook developer app
    bq_project_id: The BigQuery project ID
    bq_dataset_id: The dataset ID
    bq_table_id: The table ID
    schema: the define of schema
    data: data param
    """
    try:
        init_facebook_api(app_id, app_secret, access_token)
        audience = CustomAudience('{audience_id}')
        audience.create_user(
            params = patches
        )
    except FacebookRequestError as e:
        print(f'Error creating custom audience: {e}')