import json
import re
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN_DIR = BASE_DIR / "tokens"

TOKEN_DIR.mkdir(exist_ok=True)


def safe_filename(email: str) -> str:
    """
    Convert an email address into a safe filename.
    """

    return re.sub(r"[^a-zA-Z0-9_.-]", "_", email)


def token_path(email: str) -> Path:
    """
    Return the token path for a Gmail account.
    """

    return TOKEN_DIR / f"{safe_filename(email)}.json"


def account_exists(email: str) -> bool:
    """
    Check whether a Gmail account has a stored OAuth token.
    """

    return token_path(email).exists()


def get_accounts():
    """
    Return all locally stored Gmail accounts.

    Reads the email address from each OAuth token.
    """

    accounts = []

    for file in TOKEN_DIR.glob("*.json"):

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            email = data.get("email")

            if email:
                accounts.append(email)

        except Exception:
            continue

    return sorted(set(accounts), key=str.lower)


def save_account_token(email: str, token_data: dict):
    """
    Save OAuth token data for a Gmail account.
    """

    path = token_path(email)

    token_data["email"] = email

    with open(path, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)


def delete_account_token(email: str):
    """
    Delete the local OAuth token for an account.
    """

    path = token_path(email)

    if path.exists():
        path.unlink()


def read_account_token(email: str) -> Optional[dict]:
    """
    Read the OAuth token data for an account.
    """

    path = token_path(email)

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return None