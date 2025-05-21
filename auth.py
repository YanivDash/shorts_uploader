import os
import json
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

load_dotenv()  # Load from .env file

def get_youtube_client_from_env(env_var_name: str):
    """
    Load YouTube credentials from an environment variable containing JSON string.
    """
    token_data = os.getenv(env_var_name)
    if not token_data:
        raise EnvironmentError(f"Missing env variable: {env_var_name}")

    try:
        creds_data = json.loads(token_data)
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    except Exception as e:
        raise ValueError(f"Failed to load credentials from {env_var_name}: {e}")

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)
