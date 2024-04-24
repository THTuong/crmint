from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError

def init_facebook_api(app_id: str, app_secret: str, access_token: str) -> None:
    """Initialize the Facebook API client."""
    FacebookAdsApi.init(app_id, app_secret, access_token)

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
            'customer_file_source': 'NONE'
        }
        audience = ad_account.create_custom_audience(params=params)
        print(f'Created empty custom audience with ID: {audience["id"]}')
    except FacebookRequestError as e:
        print(f'Error creating custom audience: {e}')