import base64
import html
from email.mime.text import MIMEText

from googleapiclient.discovery import build


def get_gmail_service(credentials):
    """
    Create Gmail API service.
    """

    return build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False
    )


def get_profile(service):
    """
    Get Gmail account information.
    """

    return (
        service.users()
        .getProfile(userId="me")
        .execute()
    )


def get_account_email(service):
    """
    Return the Gmail address of the authenticated user.
    """

    profile = get_profile(service)

    return profile.get("emailAddress")


def list_messages(service, max_results=20):
    """
    Get recent Gmail messages.
    """

    result = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results
        )
        .execute()
    )

    return result.get("messages", [])


def get_message(service, message_id):
    """
    Get a complete Gmail message.
    """

    return (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full"
        )
        .execute()
    )


def decode_body(data):
    """
    Decode Gmail base64url body.
    """

    if not data:
        return ""

    try:

        decoded = base64.urlsafe_b64decode(
            data.encode("UTF-8")
        )

        return decoded.decode(
            "utf-8",
            errors="replace"
        )

    except Exception:

        return ""


def extract_headers(message):
    """
    Extract useful email headers.
    """

    headers = {}

    payload = message.get("payload", {})

    for header in payload.get("headers", []):

        name = header.get("name", "").lower()

        value = header.get("value", "")

        headers[name] = value

    return headers


def get_email_body(message):
    """
    Extract readable email text from Gmail message.
    """

    payload = message.get("payload", {})

    # Simple email
    body = payload.get("body", {})

    if body.get("data"):

        return decode_body(body["data"])

    # Multipart email
    parts = payload.get("parts", [])

    plain_text = ""
    html_text = ""

    for part in parts:

        mime_type = part.get("mimeType", "")

        part_body = part.get("body", {})

        data = part_body.get("data")

        if not data:
            continue

        decoded = decode_body(data)

        if mime_type == "text/plain":

            plain_text += decoded

        elif mime_type == "text/html":

            html_text += decoded

    if plain_text.strip():

        return plain_text.strip()

    if html_text.strip():

        # Basic HTML cleanup
        cleaned = html.unescape(html_text)

        cleaned = (
            cleaned
            .replace("<br>", "\n")
            .replace("<br/>", "\n")
            .replace("<br />", "\n")
        )

        return cleaned

    return ""


def format_message(message):
    """
    Convert a Gmail API message into an easier dictionary.
    """

    headers = extract_headers(message)

    body = get_email_body(message)

    return {
        "id": message.get("id"),
        "threadId": message.get("threadId"),
        "subject": headers.get("subject", "(No Subject)"),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "date": headers.get("date", ""),
        "message_id": headers.get("message-id", ""),
        "body": body,
    }


def send_email(
    service,
    to,
    subject,
    body,
    thread_id=None,
    in_reply_to=None,
):
    """
    Send a Gmail email.

    If thread_id is supplied, Gmail keeps it in the same thread.
    """

    message = MIMEText(body, "plain", "utf-8")

    message["to"] = to
    message["subject"] = subject

    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
        message["References"] = in_reply_to

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    email_body = {
        "raw": encoded_message
    }

    if thread_id:
        email_body["threadId"] = thread_id

    result = (
        service.users()
        .messages()
        .send(
            userId="me",
            body=email_body
        )
        .execute()
    )

    return result