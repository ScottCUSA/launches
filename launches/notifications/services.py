"""Space Launch Notifications - Notifications Services Module

Copyright ©️ 2023 Scott Cummings
License: GNU General Public License V3
         https://www.gnu.org/licenses/gpl-3.0.en.html

"""
import base64
import logging
import smtplib
import ssl
import sys
from email.mime.text import MIMEText
from typing import Any, Protocol


class NotificationError(Exception):
    """notification service error"""


class NotificationService(Protocol):
    """The protocol a notification service needs to follow"""

    def send(self, subject: str, body: str) -> None:
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
        if "username" in kwargs and "password" in kwargs:
            self.username: str = kwargs["username"]
            self.password: str = base64.b64decode(kwargs["password"]).decode("utf-8")
        self.sender: str = kwargs["sender"]
        self.recipients: list[str] | str = kwargs["recipients"]
        logging.info("Initialized %s", self)

    def get_msg(self, subject: str, body: str) -> str:
        """build the message using MIMEText
        return the message as a str"""
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.sender
        if isinstance(self.recipients, list):
            msg["To"] = ",".join(self.recipients)
        else:
            msg["To"] = self.recipients
        return msg.as_string()

    def send(self, subject: str, body: str) -> None:
        """Attempt to connect to SMTP server and send email
        will raise a NotificationError if there were any issues"""

        logging.info("Attempting to send email notification")

        # attempt to create a SSL context if we need to use TLS
        if self.use_tls:
            try:
                context = ssl.create_default_context()
            except ssl.SSLError as ex:
                raise NotificationError(
                    "Unable to make secure connection to SMTP server."
                ) from ex

        # attempt to connect to the SMTP server and send the email
        try:
            with smtplib.SMTP(self.server, self.port) as connection:
                # verify connection
                connection.ehlo()
                if self.use_tls:
                    connection.starttls(context=context)
                # if we've been passed credentials attempt to login
                if self.username and self.password:
                    connection.login(self.username, self.password)
                # actually attempt to send the email
                connection.sendmail(
                    self.sender, self.recipients, self.get_msg(subject, body)
                )
        except (smtplib.SMTPException, ssl.SSLError) as ex:
            raise NotificationError(f"Unable to send email notification {ex}") from ex

        logging.info("Successfully sent email notification")

    def __repr__(self) -> str:
        return (
            f"EmailNotificationService(smtp_server='{self.server}',"
            f" smtp_port={self.port}, use_tls={self.use_tls})"
        )


class StdOutNotificationService:
    """A "dummy" notification service which just prints to stdout"""

    def __init__(self, *args, **kwargs) -> None:
        logging.info("Initialized %s", self)

    def send(self, subject: str, body: str) -> None:
        """print notification to stdout"""
        logging.info("StdOut Notification:")
        print(subject)
        print(body)

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
        logging.error("Service config missing required fields")
        sys.exit(1)
    try:
        logging.info(
            "Attempting to load notification service: %s",
            service_config["service"],
        )
        match service_config["service"]:
            case "email":
                return EmailNotificationService(**service_config["parameters"])
            case "stdout":
                return StdOutNotificationService()
            case _:
                logging.error(
                    "Unknown notification service %s",
                    service_config["service"],
                )
                sys.exit(1)
    except (ValueError, TypeError, KeyError) as ex:
        logging.error("Unable to load notification service: %s", ex)
        sys.exit(1)
