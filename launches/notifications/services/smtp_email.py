"""Space Launch Notifications - SMTP Email Notification Service

Copyright ©️ 2025 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import base64
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from launches.errors import NotificationError

CONNECT_TIMEOUT = 30


class SMTPEmaiLNotificationService:
    """An email notification service which connects to
    a SMTP server with the credentials provided"""

    def __init__(self, *_args, **kwargs) -> None:
        self.server: str = kwargs["smtp_server"]
        self.port: int = kwargs["smtp_port"]
        self.use_tls: bool = kwargs["use_tls"]
        if "local_hostname" in kwargs:
            self.local_hostname: str | None = kwargs["local_hostname"]
        else:
            self.local_hostname = None
        if "smtp_username" in kwargs and "smtp_password" in kwargs:
            self.username: str | None = kwargs["smtp_username"]
            self.password: str | None = base64.b64decode(kwargs["smtp_password"]).decode("utf-8")
        else:
            self.username = None
            self.password = None
        self.sender: str = kwargs["sender"]
        self.recipients: list[str] | str = kwargs["recipients"]
        logger.info("Initialized {}", self)

    def get_msg(self, subject: str, body: str, html_body: str | None) -> MIMEMultipart | MIMEText:
        """build the message using MIMEText
        return the message as a str"""
        if html_body:
            msg: MIMEMultipart | MIMEText = MIMEMultipart("alternative")
        else:
            msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.sender
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

    def _create_smtp_connection(self):
        """Create and return an SMTP connection as a context manager"""
        logger.debug("Connecting to SMTP server: {}:{}", self.server, self.port)

        if self.use_tls:
            logger.debug("Connecting with SSL")
            connection = smtplib.SMTP_SSL(
                self.server, self.port, local_hostname=self.local_hostname, timeout=CONNECT_TIMEOUT
            )
        else:
            logger.debug("Connecting without SSL")
            connection = smtplib.SMTP(
                self.server, self.port, local_hostname=self.local_hostname, timeout=CONNECT_TIMEOUT
            )

        connection.ehlo()
        if self.username and self.password:
            logger.debug("Authenticating with username: {}", self.username)
            connection.login(self.username, self.password)

        return connection

    def send(self, subject: str, msg: str, formatted_msg: str | None) -> None:
        """Attempt to connect to SMTP server and send email
        will raise a NotificationError if there were any issues
        msg must be a valid email message"""

        logger.info("Attempting to send email notification")
        message = self.get_msg(subject, msg, formatted_msg)

        logger.debug("Email details - Subject: '{}', To: {}", subject, self.recipients)

        try:
            connection = self._create_smtp_connection()
            logger.debug("Sending email message")
            send_errs = connection.sendmail(self.sender, self.recipients, message.as_string())
            if send_errs is not None and len(send_errs):
                logger.error("SMTP Send Errors: {}", send_errs)
        except (smtplib.SMTPException, ssl.SSLError) as ex:
            logger.error("SMTP Exception: {}", ex)
            raise NotificationError(f"Unable to send email notification {ex}") from ex
        finally:
            connection.close()

        logger.info("Successfully sent email notification")

    def __repr__(self) -> str:
        return (
            f"EmailNotificationService(smtp_server='{self.server}',"
            f" smtp_port={self.port}, use_tls={self.use_tls})"
        )
