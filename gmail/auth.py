from pathlib import Path

import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from utils.account_manager import (
    token_path,
    save_account_token,
    delete_account_token,
)


BASE_DIR = Path(__file__).resolve().parent.parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def validate_credentials_file():
    """
    Check whether credentials.json exists.
    """

    if not CREDENTIALS_FILE.exists():

        raise FileNotFoundError(
            "credentials.json not found. "
            "Download your Google Desktop OAuth client and "
            "place credentials.json in the project root."
        )


def load_credentials(email: str):
    """
    Load OAuth credentials for a specific Gmail account.

    If the access token expired, refresh it automatically.
    """

    path = token_path(email)

    if not path.exists():
        return None

    try:

        credentials = Credentials.from_authorized_user_file(
            str(path),
            SCOPES
        )

        if credentials.expired and credentials.refresh_token:

            credentials.refresh(Request())

            save_credentials(email, credentials)

        return credentials

    except Exception:

        return None


def save_credentials(email: str, credentials):
    """
    Save OAuth credentials for a Gmail account.
    """

    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "email": email,
    }

    save_account_token(email, token_data)


def connect_gmail():
    """
    Start the Google OAuth flow.

    A browser window opens and the user selects the Gmail account.
    """

    validate_credentials_file()

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="select_account"
    )

    return credentials


def revoke_google_access(email: str):
    """
    Revoke the OAuth authorization from Google.

    After this, the application can no longer use
    the OAuth token for that account.
    """

    path = token_path(email)

    if not path.exists():
        return False, "No local token found."

    try:

        credentials = Credentials.from_authorized_user_file(
            str(path),
            SCOPES
        )

        if not credentials.token:
            delete_account_token(email)

            return True, "Local account removed."

        response = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={
                "token": credentials.token
            },
            timeout=15
        )

        if response.status_code == 200:

            delete_account_token(email)

            return True, "Google authorization revoked and local token deleted."

        # Sometimes the access token may already be invalid.
        # Delete the local token anyway.
        delete_account_token(email)

        return True, (
            "Local token deleted. "
            "Google authorization may already have been invalid."
        )

    except Exception as e:

        return False, f"Could not revoke authorization: {e}"


def remove_local_account(email: str):
    """
    Remove only the local token.

    This does NOT revoke Google's authorization.
    """

    delete_account_token(email)