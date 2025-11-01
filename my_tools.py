import os
import requests
import base64
from crewai_tools import tool

# ---
# 1. UiPath Authentication Function
# ---
def get_uipath_access_token() -> str:
    """
    Authenticates with UiPath Orchestrator and returns a Bearer Token.
    Uses Client ID and Client Secret from environment variables.
    """
    # Load credentials from environment variables
    client_id = os.environ.get("UIPATH_CLIENT_ID")
    client_secret = os.environ.get("UIPATH_CLIENT_SECRET")
    account_name = os.environ.get("UIPATH_ACCOUNT_NAME")

    if not all([client_id, client_secret, account_name]):
        return "Error: UiPath auth environment variables are not set."

    auth_url = f"https://cloud.uipath.com/{account_name}/identity_/connect/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "OR.Jobs.Read OR.Queues.Read" # Must match the scopes you set in Admin
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting UiPath token: {e}")
        if response:
            print(f"Response body: {response.text}")
        return None

# ---
# 2. UiPath Orchestrator Tool
# ---
@tool("UiPath Orchestrator Tool")
def get_uipath_job_data(job_id: str) -> str:
    """
    Fetches the details for a specific job from the UiPath Orchestrator.
    You must provide the 'job_id' to get the information.
    """
    
    # --- 1. Get Authentication Token ---
    print("Attempting to get UiPath access token...")
    token = get_uipath_access_token()
    if not token:
        return "Error: Could not authenticate with UiPath."
    print("Successfully authenticated with UiPath.")

    # --- 2. Load Account/Tenant Names ---
    account_name = os.environ.get("UIPATH_ACCOUNT_NAME")
    tenant_name = os.environ.get("UIPATH_TENANT_NAME") 

    if not all([account_name, tenant_name]):
        return "Error: UiPath Account/Tenant names are not set."

    # --- 3. Make the API Call ---
    url = f"https://cloud.uipath.com/{account_name}/{tenant_name}/orchestrator_/odata/Jobs({job_id})"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": tenant_name
    }
    
    try:
        print(f"Fetching data for Job ID: {job_id}")
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raises an error for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error connecting to UiPath API: {e}. Response: {response.text}"


# ---
# 3. Kibana (Elasticsearch) Authentication
# ---
def get_kibana_auth_header() -> str:
    """
    Creates the Base64 encoded API Key header for Elasticsearch.
    """
    # Load credentials from environment variables
    api_id = os.environ.get("KIBANA_API_ID")
    api_secret = os.environ.get("KIBANA_API_SECRET")

    if not all([api_id, api_secret]):
        return "Error: Kibana API ID or Secret environment variables not set."

    # 1. Concatenate ID and Secret with a colon
    token_string = f"{api_id}:{api_secret}"
    
    # 2. Encode to Base64
    base64_token = base64.b64encode(token_string.encode('utf-8')).decode('utf-8')
    
    # 3. Return the final header string
    return f"ApiKey {base64_token}"

# ---
# 4. Kibana Query Tool
# ---
@tool("Kibana Query Tool")
def query_kibana_logs(search_query: str) -> str:
    """
    Queries Kibana (Elasticsearch) for logs matching a specific 'search_query'.
    Use this to find logs based on data from other systems, like a Job ID or Transaction ID.
    The query will search the 'message' field in the 'uipath-logs-*' index.
    """
    
    # --- 1. Get Authentication Header ---
    print("Getting Kibana/Elasticsearch auth header...")
    auth_header = get_kibana_auth_header()
    if "Error" in auth_header:
        return auth_header
    print("Successfully created Kibana auth header.")

    # --- 2. Load Host and Index Name ---
    host = os.environ.get("KIBANA_HOST")
    index_name = os.environ.get("KIBANA_INDEX", "uipath-logs-*") # Default index

    if not host:
        return "Error: KIBANA_HOST environment variable not set."

    # --- 3. Make the API Call ---
    url = f"{host}/{index_name}/_search"
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    # This is a simple "match" query. You can make this more complex.
    query_body = {
        "query": {
            "match": {
                "message": search_query
            }
        },
        "size": 10 # Get top 10 results
    }
    
    try:
        print(f"Querying Kibana for: {search_query}")
        response = requests.post(url, headers=headers, json=query_body)
        response.raise_for_status()
        
        # We'll return just the 'hits' to keep it clean for the agent
        return response.json().get('hits', 'No hits found.')
        
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Kibana/Elasticsearch API: {e}. Response: {response.text}"
