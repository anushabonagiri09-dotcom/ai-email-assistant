from pathlib import Path
import json
import re

BASE_DIR = Path(__file__).resolve().parent.parent

TOKENS_DIR = BASE_DIR / "tokens"
TOKENS_DIR.mkdir(exist_ok=True)


def safe_filename(email: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", email)


def token_path(email: str) -> Path:
    return TOKENS_DIR / f"{safe_filename(email)}.json"


def account_exists(email: str) -> bool:
    return token_path(email).exists()


def get_accounts() -> list[str]:
    if not TOKENS_DIR.exists():
        return []

    accounts = []

    for file in TOKENS_DIR.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            email = data.get("email")

            if email:
                accounts.append(email)

        except Exception:
            continue

    return sorted(accounts)


def save_account_token(email: str, token_data: dict):
    path = token_path(email)

    token_data["email"] = email

    with open(path, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=4)


def read_account_token(email: str):
    path = token_path(email)

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return None


def delete_account_token(email: str) -> bool:
    path = token_path(email)

    if path.exists():
        path.unlink()
        return True

    return False