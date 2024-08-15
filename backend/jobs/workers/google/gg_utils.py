import hashlib
import requests
from google.ads.googleads.client import GoogleAdsClient
import uuid

def create_customer_match_user_list(client, customer_id, name,life_span):
    # Creates the UserListService client.
    user_list_service_client = client.get_service("UserListService")
    
    # Creates the user list operation.
    user_list_operation = client.get_type("UserListOperation")
    
    # Creates the new user list.
    user_list = user_list_operation.create
    user_list.name = f"{name}#{uuid.uuid4()}"
    user_list.crm_based_user_list.upload_key_type = (
        client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
    )
    user_list.membership_life_span = life_span
    response = user_list_service_client.mutate_user_lists(
        customer_id=customer_id, operations=[user_list_operation]
    )
    user_list_resource_name = response.results[0].resource_name
    return user_list_resource_name

def add_users_to_customer_match_user_list(client,customer_id,user_list_resource_name,api_url):
    # Creates the OfflineUserDataJobService client.
    offline_user_data_job_service_client = client.get_service(
        "OfflineUserDataJobService"
    )
    offline_user_data_job = client.get_type("OfflineUserDataJob")
    offline_user_data_job.type_ = (client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST)
    offline_user_data_job.customer_match_user_list_metadata.user_list = (user_list_resource_name)
    create_offline_user_data_job_response = (offline_user_data_job_service_client.create_offline_user_data_job(customer_id=customer_id, job=offline_user_data_job))
    offline_user_data_job_resource_name = (create_offline_user_data_job_response.resource_name)
    request = client.get_type("AddOfflineUserDataJobOperationsRequest")
    request.resource_name = offline_user_data_job_resource_name
    request.operations = build_offline_user_data_job_operations(client,api_url)
    offline_user_data_job_service_client.run_offline_user_data_job(resource_name=offline_user_data_job_resource_name)
    
def build_offline_user_data_job_operations(client,api_url):
    raw_records = []
    current_page = 1
    total_pages = 1
    while current_page <= total_pages:
        response = requests.get(f"{api_url}&pagination[page]={current_page}")
        response_json = response.json()
        total_pages = response_json['meta']['pagination']['pageCount']
        for item in response_json['data']:
            for pii_item in item['attributes']['pii']:
                record = {
                    "email": pii_item.get("email"),
                    "phone": pii_item.get("phone"),
                }
                raw_records.append(record)
        
        current_page += 1
        
    operations = []
    for record in raw_records:
        user_data = client.get_type("UserData")
        
        if "email" in record:
            user_identifier = client.get_type("UserIdentifier")
            user_identifier.hashed_email = normalize_and_hash(
                record["email"], True
            )
            # Adds the hashed email identifier to the UserData object's list.
            user_data.user_identifiers.append(user_identifier)
            
        if "phone" in record:
            user_identifier = client.get_type("UserIdentifier")
            user_identifier.hashed_phone_number = normalize_and_hash(
                record["phone"], True
            )
            # Adds the hashed phone number identifier to the UserData object's list.
            user_data.user_identifiers.append(user_identifier)
        if user_data.user_identifiers:
            operation = client.get_type("OfflineUserDataJobOperation")
            operation.create = user_data
            operations.append(operation)
            
    return operations

def normalize_and_hash(s, remove_all_whitespace):
    if remove_all_whitespace:
        # Removes leading, trailing, and intermediate whitespace.
        s = "".join(s.split())
    else:
        # Removes only leading and trailing spaces.
        s = s.strip().lower()

    # Hashes the normalized string using the hashing algorithm.
    return hashlib.sha256(s.encode()).hexdigest()

def create_google_custom_audience(customer_id,name,life_span,api_url,developer_token,refresh_token,client_id,client_secret):
    credentials = {
        "developer_token": developer_token,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "use_proto_plus": True
    }
    client = GoogleAdsClient.load_from_dict(credentials)
    user_list_resource_name = create_customer_match_user_list(client, customer_id, name, life_span)
    add_users_to_customer_match_user_list(client,customer_id,user_list_resource_name,api_url)
    return f"Success to create {user_list_resource_name}"