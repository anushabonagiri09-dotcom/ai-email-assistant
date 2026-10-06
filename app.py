import streamlit as st

from gmail.auth import (
    connect_gmail,
    load_credentials,
    revoke_google_access,
    remove_local_account,
)

from gmail.service import (
    get_gmail_service,
    get_account_email,
    list_messages,
    get_message,
    format_message,
    send_email,
)

from ai.gemini import (
    generate_reply,
    summarize_email,
)

from utils.account_manager import (
    get_accounts,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide",
)


# =========================================================
# SESSION STATE
# =========================================================

if "selected_account" not in st.session_state:
    st.session_state.selected_account = None

if "selected_message" not in st.session_state:
    st.session_state.selected_message = None

if "generated_reply" not in st.session_state:
    st.session_state.generated_reply = ""

if "email_summary" not in st.session_state:
    st.session_state.email_summary = ""


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def refresh_accounts():

    accounts = get_accounts()

    if (
        st.session_state.selected_account
        and st.session_state.selected_account not in accounts
    ):
        st.session_state.selected_account = (
            accounts[0] if accounts else None
        )

    return accounts


def get_current_credentials():

    email = st.session_state.selected_account

    if not email:
        return None

    return load_credentials(email)


def get_current_service():

    credentials = get_current_credentials()

    if not credentials:
        return None

    try:
        return get_gmail_service(credentials)

    except Exception:
        return None


def connect_new_account():

    try:

        with st.spinner("Opening Google sign-in..."):

            credentials = connect_gmail()

        service = get_gmail_service(credentials)

        email = get_account_email(service)

        if not email:

            st.error(
                "Could not determine the Gmail address."
            )

            return

        # Save credentials using Gmail address
        from gmail.auth import save_credentials

        save_credentials(
            email,
            credentials
        )

        st.session_state.selected_account = email
        st.session_state.selected_message = None
        st.session_state.generated_reply = ""
        st.session_state.email_summary = ""

        st.success(
            f"Connected: {email}"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Gmail connection failed: {e}"
        )


# =========================================================
# HEADER
# =========================================================

st.title("📧 AI Email Assistant")

st.caption(
    "Gmail + Gemini + Streamlit | Multiple Gmail Accounts"
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🔐 Gmail Accounts")

    accounts = refresh_accounts()

    # -----------------------------------------------------
    # CONNECT ACCOUNT
    # -----------------------------------------------------

    if st.button(
        "➕ Connect Gmail Account",
        use_container_width=True
    ):

        connect_new_account()

    st.divider()

    # -----------------------------------------------------
    # ACCOUNT SELECTOR
    # -----------------------------------------------------

    if accounts:

        current_index = 0

        if (
            st.session_state.selected_account
            and st.session_state.selected_account in accounts
        ):

            current_index = accounts.index(
                st.session_state.selected_account
            )

        selected = st.selectbox(
            "Current Gmail Account",
            accounts,
            index=current_index,
            key="account_selector"
        )

        if selected != st.session_state.selected_account:

            st.session_state.selected_account = selected
            st.session_state.selected_message = None
            st.session_state.generated_reply = ""
            st.session_state.email_summary = ""

            st.rerun()

    else:

        st.info(
            "No Gmail account connected."
        )

    st.divider()

    # -----------------------------------------------------
    # ACCOUNT MANAGEMENT
    # -----------------------------------------------------

    if st.session_state.selected_account:

        current_email = st.session_state.selected_account

        st.subheader("Account")

        st.write(
            f"**{current_email}**"
        )

        # -------------------------------------------------
        # DISCONNECT
        # -------------------------------------------------

        if st.button(
            "🔌 Disconnect",
            use_container_width=True
        ):

            remove_local_account(
                current_email
            )

            st.session_state.selected_account = None
            st.session_state.selected_message = None
            st.session_state.generated_reply = ""
            st.session_state.email_summary = ""

            st.success(
                "Account removed from this app."
            )

            st.rerun()

        # -------------------------------------------------
        # REVOKE
        # -------------------------------------------------

        if st.button(
            "🔐 Revoke Google Authorization",
            use_container_width=True
        ):

            success, message = revoke_google_access(
                current_email
            )

            if success:

                st.session_state.selected_account = None
                st.session_state.selected_message = None
                st.session_state.generated_reply = ""
                st.session_state.email_summary = ""

                st.success(message)

                st.rerun()

            else:

                st.error(message)

        st.caption(
            "Disconnect removes the local token. "
            "Revoke also removes this app's Google authorization."
        )

    st.divider()

    st.warning(
        "Review AI-generated replies before sending."
    )


# =========================================================
# NO ACCOUNT
# =========================================================

if not st.session_state.selected_account:

    st.info(
        "Connect a Gmail account from the sidebar to begin."
    )

    st.markdown(
        """
        ### Features

        - 🔗 Connect multiple Gmail accounts
        - 🔄 Switch accounts
        - 📥 Read inbox messages
        - 📝 Summarize emails
        - 🤖 Generate AI replies
        - ✉️ Send replies
        - 🔌 Disconnect accounts
        - 🔐 Revoke Google authorization
        - 🗑️ Remove local OAuth tokens
        """
    )

    st.stop()


# =========================================================
# CURRENT ACCOUNT
# =========================================================

current_email = st.session_state.selected_account

credentials = get_current_credentials()

if not credentials:

    st.error(
        "OAuth credentials could not be loaded."
    )

    if st.button("Reconnect Account"):

        connect_new_account()

    st.stop()


service = get_current_service()

if not service:

    st.error(
        "Could not connect to Gmail."
    )

    st.stop()


# =========================================================
# ACCOUNT HEADER
# =========================================================

st.success(
    f"Connected Gmail: {current_email}"
)


# =========================================================
# LOAD EMAILS
# =========================================================

try:

    messages = list_messages(
        service,
        max_results=20
    )

except Exception as e:

    st.error(
        f"Could not load Gmail messages: {e}"
    )

    st.stop()


# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns(
    [1, 2]
)


# =========================================================
# EMAIL LIST
# =========================================================

with left:

    st.subheader("📥 Inbox")

    if not messages:

        st.info(
            "No messages found."
        )

    else:

        for item in messages:

            message_id = item["id"]

            try:

                raw_message = get_message(
                    service,
                    message_id
                )

                email = format_message(
                    raw_message
                )

                subject = email["subject"]

                sender = email["from"]

                button_label = (
                    f"✉️ {subject[:35]}"
                )

                if st.button(
                    button_label,
                    key=f"email_{message_id}",
                    use_container_width=True
                ):

                    st.session_state.selected_message = email
                    st.session_state.generated_reply = ""
                    st.session_state.email_summary = ""

                    st.rerun()

                st.caption(
                    sender[:45]
                )

            except Exception:

                continue


# =========================================================
# EMAIL VIEW
# =========================================================

with right:

    selected_email = (
        st.session_state.selected_message
    )

    if not selected_email:

        st.info(
            "Select an email from the inbox."
        )

    else:

        # -------------------------------------------------
        # EMAIL HEADER
        # -------------------------------------------------

        st.subheader(
            selected_email["subject"]
        )

        st.write(
            f"**From:** {selected_email['from']}"
        )

        st.write(
            f"**To:** {selected_email['to']}"
        )

        st.write(
            f"**Date:** {selected_email['date']}"
        )

        st.divider()

        # -------------------------------------------------
        # EMAIL CONTENT
        # -------------------------------------------------

        st.markdown("### 📧 Email")

        st.text_area(
            "Email content",
            selected_email["body"],
            height=300,
            disabled=True,
            key="email_content"
        )

        st.divider()

        # =================================================
        # AI FEATURES
        # =================================================

        st.subheader("🤖 AI Assistant")

        # -------------------------------------------------
        # REPLY INSTRUCTION
        # -------------------------------------------------

        reply_instruction = st.text_area(
            "Reply instruction",
            "Write a professional and helpful reply.",
            key="reply_instruction"
        )

        # -------------------------------------------------
        # AI BUTTONS
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        # =================================================
        # GENERATE REPLY
        # =================================================

        with col1:

            if st.button(
                "✨ Generate Reply",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Generating AI reply..."
                    ):

                        reply = generate_reply(
                            sender=selected_email["from"],
                            subject=selected_email["subject"],
                            email_body=selected_email["body"],
                            instruction=reply_instruction
                        )

                        st.session_state.generated_reply = reply

                    st.success(
                        "AI reply generated."
                    )

                except Exception as e:

                    st.error(
                        f"Gemini error: {e}"
                    )

        # =================================================
        # SUMMARIZE EMAIL
        # =================================================

        with col2:

            if st.button(
                "📝 Summarize Email",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Summarizing email..."
                    ):

                        summary = summarize_email(
                            sender=selected_email["from"],
                            subject=selected_email["subject"],
                            email_body=selected_email["body"]
                        )

                        st.session_state.email_summary = summary

                    st.success(
                        "Email summarized."
                    )

                except Exception as e:

                    st.error(
                        f"Gemini error: {e}"
                    )

        # =================================================
        # SUMMARY DISPLAY
        # =================================================

        if st.session_state.email_summary:

            st.divider()

            st.markdown(
                "### 📝 Email Summary"
            )

            st.markdown(
                st.session_state.email_summary
            )

        # =================================================
        # REPLY EDITOR
        # =================================================

        if st.session_state.generated_reply:

            st.divider()

            st.markdown(
                "### ✉️ Generated Reply"
            )

            reply_text = st.text_area(
                "Edit your reply before sending:",
                value=st.session_state.generated_reply,
                height=250,
                key="reply_editor"
            )

            # Keep latest edited reply
            st.session_state.generated_reply = reply_text

            # =================================================
            # SEND REPLY
            # =================================================

            if st.button(
                "📤 Send Reply",
                type="primary",
                use_container_width=True
            ):

                if not reply_text.strip():

                    st.warning(
                        "Please generate or write a reply first."
                    )

                else:

                    try:

                        with st.spinner(
                            "Sending email..."
                        ):

                            reply_subject = (
                                selected_email["subject"]
                                if selected_email["subject"]
                                .lower()
                                .startswith("re:")
                                else
                                "Re: " + selected_email["subject"]
                            )

                            send_email(
                                service=service,
                                to=selected_email["from"],
                                subject=reply_subject,
                                body=reply_text,
                                thread_id=selected_email["threadId"],
                                in_reply_to=selected_email.get(
                                    "message_id"
                                ),
                            )

                        st.success(
                            "Reply sent successfully."
                        )

                        st.session_state.generated_reply = ""

                    except Exception as e:

                        st.error(
                            f"Failed to send reply: {e}"
                        )