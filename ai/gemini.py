import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


# =========================================================
# GEMINI CLIENT
# =========================================================

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing from .env"
        )

    return genai.Client(
        api_key=api_key
    )


# =========================================================
# GENERATE AI REPLY
# =========================================================

def generate_reply(
    sender=None,
    subject=None,
    email_body=None,
    instruction=None,
    email_subject=None
):
    client = get_gemini_client()

    # Support alternative subject parameter
    if subject is None:
        subject = email_subject

    model = "gemini-3.5-flash-lite"

    prompt = f"""
You are an AI email assistant.

Generate a professional and natural reply to the email below.

Sender:
{sender if sender else "Unknown"}

Email Subject:
{subject if subject else "No Subject"}

Email Body:
{email_body if email_body else "No email body"}

User's Reply Instruction:
{instruction if instruction else "Write a professional and helpful reply."}

Rules:
- Be polite and professional.
- Follow the user's reply instruction.
- Keep the reply concise and natural.
- Do not invent information.
- Do not make up dates, names, links, or commitments.
- Return only the email reply.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text.strip()


# =========================================================
# SUMMARIZE EMAIL
# =========================================================

def summarize_email(
    sender=None,
    subject=None,
    email_body=None,
    email_subject=None,
    body=None
):
    client = get_gemini_client()

    # Support alternative parameter names
    if subject is None:
        subject = email_subject

    if email_body is None:
        email_body = body

    model = "gemini-3.5-flash-lite"

    prompt = f"""
Summarize the following email clearly and briefly.

Sender:
{sender if sender else "Unknown"}

Email Subject:
{subject if subject else "No Subject"}

Email Body:
{email_body if email_body else "No email body"}

Give the summary in 2-4 concise bullet points.

Focus on:
- Main purpose of the email
- Important information
- Any request or action needed
- Important dates or deadlines

Do not invent information.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text.strip()