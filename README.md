# AI Email Assistant

A local Streamlit AI email assistant using Gmail API + OAuth 2.0 + Gemini.

## Features

- Gmail OAuth authentication
- Inbox and Gmail query search
- Email list and full content
- Gemini email summaries
- Gemini email classification
- AI reply generation
- Editable AI replies
- Explicit confirmation before sending
- Mark email as read

## Project structure

ai-email-assistant/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── credentials.json        # you add this
├── token.json              # generated after OAuth
├── gmail/
│   ├── auth.py
│   └── service.py
├── ai/
│   └── gemini.py
└── utils/
    └── text_processing.py

## Windows setup

Use Python 3.11.9.

### 1. Create the project

Extract this ZIP and open the folder in VS Code.

### 2. Create a virtual environment

PowerShell:

py -3.11 -m venv .venv

Activate:

.\.venv\Scripts\Activate.ps1

If PowerShell blocks activation, use Command Prompt:

.venv\Scripts\activate.bat

Or run Python through the environment without activating it.

### 3. Install packages

python -m pip install --upgrade pip
pip install -r requirements.txt

### 4. Google Cloud / Gmail OAuth

Create a Google Cloud project and enable the Gmail API.

Configure Google Auth Platform / OAuth consent.

For a local test application, create an OAuth 2.0 Client ID with application type:
Desktop app

Download the JSON file and rename it:

credentials.json

Put it beside app.py.

Use a test Gmail account.

### 5. Gemini API key

Create a Gemini API key.

Copy `.env.example` to `.env`:

copy .env.example .env

Edit `.env`:

GEMINI_API_KEY=YOUR_REAL_KEY
GEMINI_MODEL=gemini-3.8-flash

Never commit `.env`.

### 6. Start the application

streamlit run app.py

The browser opens the Streamlit application.

Click:

Connect Gmail

A Google OAuth browser window opens.

Choose the test Gmail account and grant the requested Gmail permissions.

After successful authorization, token.json is generated locally.

### 7. Use the assistant

Click Load Emails.

Examples of Gmail search queries:

in:inbox
is:unread
from:example@gmail.com
subject:project
has:attachment

Select an email.

Available AI actions:

- Summarize
- Classify
- Generate Reply

Edit the generated reply if necessary.

Tick the confirmation checkbox.

Then click Send Reply.

## Important security rules

Do not upload or commit:

- credentials.json
- token.json
- .env

The `.gitignore` file already excludes them.

This project is intended for local/testing use. For production, use a proper web OAuth flow, secure token storage, HTTPS, user/session isolation, least-privilege scopes, and appropriate Google OAuth verification where required.

## Troubleshooting

### credentials.json not found

Place the downloaded OAuth Desktop client JSON in the project root and name it credentials.json.

### invalid_grant / OAuth errors

Delete token.json and authorize again.

If you changed Gmail scopes, delete token.json before rerunning.

### GEMINI_API_KEY missing

Check that `.env` exists and contains:

GEMINI_API_KEY=your_key

### PowerShell execution policy

Use Command Prompt instead of PowerShell, or activate the environment with the appropriate local execution-policy configuration for your machine.

### Gmail permission screen problems

Check the Google Cloud OAuth configuration, test-user configuration if applicable, and that Gmail API is enabled.

## AI safety

AI-generated summaries and replies can be wrong. Review generated content before sending. The UI intentionally requires an explicit confirmation before a reply is sent.
