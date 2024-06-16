"""Space Launch Notifications - Notifications Services Module

Copyright ©️ 2023 Scott Cummings
SPDX-License-Identifier: MIT OR Apache-2.0
"""

import base64
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from typing import Any, Protocol

from loguru import logger


class NotificationError(Exception):
    """notification service error"""


class NotificationService(Protocol):
    """The protocol a notification service needs to follow"""

    def send(self, subject: str, msg: str, formatted_msg: str | None) -> None:
        """send notification"""
        raise NotImplementedError()

    def __repr__(self) -> str:
        raise NotImplementedError()


class EmailNotificationService:
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

    def get_msg(self, subject: str, body: str, html_body: str | None) -> str:
        """build the message using MIMEText
        return the message as a str"""
        if html_body:
            msg = MIMEMultipart("alternative")
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
        return msg.as_string()

    def send(self, subject: str, msg: str, formatted_msg: str | None) -> None:
        """Attempt to connect to SMTP server and send email
        will raise a NotificationError if there were any issues
        msg must be a valid email message"""

        logger.info("Attempting to send email notification")

        # attempt to create a SSL context if we need to use TLS
        if self.use_tls:
            try:
                context = ssl.create_default_context()
            except ssl.SSLError as ex:
                raise NotificationError("Unable to make secure connection to SMTP server.") from ex

        # attempt to connect to the SMTP server and send the email
        try:
            with smtplib.SMTP(
                self.server, self.port, local_hostname=self.local_hostname
            ) as connection:
                # send the EHLO command
                connection.ehlo()
                if self.use_tls:
                    connection.starttls(context=context)
                # if we've been passed credentials attempt to login
                if self.username and self.password:
                    connection.login(self.username, self.password)
                # actually attempt to send the email
                send_errs = connection.sendmail(
                    self.sender, self.recipients, self.get_msg(subject, msg, formatted_msg)
                )
                logger.debug("Send Errors: {}", send_errs)
        except (smtplib.SMTPException, ssl.SSLError) as ex:
            raise NotificationError(f"Unable to send email notification {ex}") from ex

        logger.info("Successfully sent email notification")

    def __repr__(self) -> str:
        return (
            f"EmailNotificationService(smtp_server='{self.server}',"
            f" smtp_port={self.port}, use_tls={self.use_tls})"
        )


class StdOutNotificationService:
    """A "dummy" notification service which just prints to stdout"""

    def __init__(self, *_args, **_kwargs) -> None:
        logger.info("Initialized {}", self)

    def send(self, subject: str, msg: str, formatted_msg: str | None) -> None:
        """print notification to stdout"""
        logger.info("StdOut Notification:")
        print(subject)
        print(msg)

    def __repr__(self) -> str:
        return "StdOutNotificationService()"


def get_notification_service(
    service_config: dict[str, Any],
) -> NotificationService:
    """This function returns a notification service built from
    the service configuration

    Expected Format:
    {
        "service": "stdout",
        "renderer":"text",   // ignored
        "parameters": {}
    }

    This function will exit the tool if an error is encountered loading
    the service, or required configuration parameters are missing.
    """
    if "service" not in service_config or "parameters" not in service_config:
        logger.error("Service config missing required fields")
        sys.exit(1)
    try:
        logger.info(
            "Attempting to load notification service: {}",
            service_config["service"],
        )
        match service_config["service"]:
            case "email":
                return EmailNotificationService(**service_config["parameters"])
            case "stdout":
                return StdOutNotificationService()
            case _:
                logger.error(
                    "Unknown notification service {}",
                    service_config["service"],
                )
                sys.exit(1)
    except (ValueError, TypeError, KeyError) as ex:
        logger.error("Unable to load notification service: {}", ex)
        sys.exit(1)
