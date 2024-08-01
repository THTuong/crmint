import requests
import hashlib
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.exceptions import FacebookRequestError
import json

def chunk_list(data_list, chunk_size):
    """Splits a list into chunks of specified size."""
    for i in range(0, len(data_list), chunk_size):
        yield data_list[i:i + chunk_size]

def create_and_add_users_to_custom_audience(account_id, app_id, app_secret, access_token, audience_name, audience_description, user_api_url) -> None:
    if not audience_description:
        audience_description = ""
    try:
        # Initialize the Facebook API
        FacebookAdsApi.init(app_id, app_secret, access_token)
        ad_account = AdAccount(f'act_{account_id}')
        
        # Define the custom audience parameters
        params = {
            'name': audience_name,
            'subtype': 'CUSTOM',
            'description': audience_description,
            'customer_file_source': 'USER_PROVIDED_ONLY'
        }
        
        # Create the custom audience
        audience = ad_account.create_custom_audience(params=params)
        custom_audience_id = audience['id']
        
        # Fetch users from another API
        response = requests.get(user_api_url)
        if response.status_code == 200:
            users = response.json()  # Assuming the response is a JSON list of emails
        else:
            raise Exception(f'Failed to fetch users: {response.status_code} {response.text}')
        
        # Hash the user data using SHA-256
        hashed_users = [hashlib.sha256(user.encode('utf-8')).hexdigest() for user in users]
        
        # Add user data to the custom audience in chunks with session management
        chunk_size = 10000
        session_id = 1  # Starting session ID (you can use any unique identifier)
        total_users = len(hashed_users)
        batch_seq = 0

        for user_chunk in chunk_list(hashed_users, chunk_size):
            batch_seq += 1
            last_batch_flag = (batch_seq * chunk_size) >= total_users

            session = {
                'session_id': session_id,
                'batch_seq': batch_seq,
                'last_batch_flag': last_batch_flag,
                'estimated_num_total': total_users
            }

            payload = {
                'schema': 'EMAIL_SHA256',
                'data': user_chunk
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                f'https://graph.facebook.com/v19.0/{custom_audience_id}/users',
                params={'access_token': access_token},
                headers=headers,
                data=json.dumps({'session': session, 'payload': payload})
            )

            if response.status_code != 200:
                print(f'Error adding users to custom audience: {response.status_code} {response.text}')

        print(f'Added {total_users} users to custom audience with ID: {custom_audience_id}')
        
    except FacebookRequestError as e:
        print(f'Error creating custom audience: {e}')