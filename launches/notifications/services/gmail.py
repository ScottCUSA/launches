"""Space Launch Notifications - Gmail Notification Service

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import ClassVar

import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger


class GmailNotificationService:
    """Concrete implementation using Google Gmail API"""

    SCOPES: ClassVar = ["https://www.googleapis.com/auth/gmail.send"]

    def __init__(self, **kwargs):
        self.credentials_file = kwargs.get("credentials_file", "")
        self.token_file = kwargs.get("token_file", "")
        self.recipients = kwargs.get("recipients", [])
        self.creds = self._authenticate()
        logger.info("Initialized {}", self)

    def _authenticate(self):
        """Handles authentication and OAuth2 flow if necessary"""
        creds = None

        logger.debug(
            "Attempting to authenticate GmailNotificationService. "
            f"Token file: {self.token_file}, Credentials file: {self.credentials_file}"
        )

        if os.path.exists(self.token_file):
            logger.debug("Token file exists. Attempting to load credentials from token file.")
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        else:
            logger.debug("Token file does not exist.")

        if not creds or not creds.valid:
            logger.info("No valid credentials found. Starting OAuth2 flow.")
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
            creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
            logger.info("Saved new credentials to token file.")

        logger.info("Gmail authentication complete. Credentials valid: {}", creds and creds.valid)
        return creds

    def get_msg(self, subject: str, body: str, html_body: str | None) -> MIMEMultipart | MIMEText:
        """build the message using MIMEText
        return the message as a str"""
        if html_body:
            msg: MIMEMultipart | MIMEText = MIMEMultipart("alternative")
        else:
            msg = MIMEText(body)
        msg["Subject"] = subject
        if isinstance(self.recipients, list):
            msg["To"] = ", ".join(self.recipients)
        else:
            msg["To"] = self.recipients
        if html_body:
            text = MIMEText(body, "text")
            html = MIMEText(html_body, "html")
            msg.attach(text)
            msg.attach(html)
        return msg

    def send(self, subject: str, msg: str, formatted_msg: str | None = None) -> None:
        """Sends email notification"""
        logger.info("Preparing to send Gmail notification. Subject: {}", subject)
        service = build("gmail", "v1", credentials=self.creds)

        message = self.get_msg(subject, msg, formatted_msg)
        logger.debug(
            "Constructed MIMEText message for Gmail. To: {}, Subject: {}",
            message["to"],
            message["subject"],
        )
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {"raw": raw_message}

        try:
            logger.debug("Sending message via Gmail API...")
            service.users().messages().send(userId="me", body=body).execute()
            logger.info("Gmail notification sent successfully.")
        except googleapiclient.errors.Error as ex:
            logger.error("Failed to send Gmail notification: {}", ex)
            raise

    def __repr__(self) -> str:
        return f"GmailNotificationService(authenticated={bool(self.creds)})"
