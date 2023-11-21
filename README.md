# Space Launch Notifications
## Description:
A tool which checks for upcoming space launches using the space launch library 2 (LL2) API and can send notifications if upcoming launches are found.

The tool has two modes:
 - The normal mode performs a check for upcoming launches within a 24 hour window, and outputs any upcoming space launches on the command line.
 - The service mode performs a check for upcoming launches repeatedly, at a user configured repeat rate, until the user presses `Ctrl+C`. </br>
   In this mode a notification will be sent via the configured notification services if upcoming launches are found. More on this later.

The tool is configurable using command-line arguments. Notification service configurations are loaded from disk from a JSON formated file.

The command line usage of the tool is as follows:
```
$ python project.py --help
usage: project.py [-h] [-w WINDOW] [--normal-mode-notif] [-d] [--service-mode] [-r REPEAT] [--config CONFIG]

A tool which checks for upcoming space launches using the free tier of the space launch library 2 API. More information about the API can be found here: https://thespacedevs.com/llapi

options:
  -h, --help           show this help message and exit
  -d                   enable debug logging
  -w WINDOW            find launches within WINDOW hours
  --normal-mode-notif  send a notification if upcoming launches within WINDOW in normal mode
  --service-mode       repeatedly check for upcoming launches until user exits with `Ctrl+C`
  -r REPEAT            repeat checks ever REPEAT hours (service mode only)
  --config CONFIG      notification service config path default=`config.json`
```

### Example Output:

If no upcoming launches are found:

```
$ python project.py
No upcoming launches found within 24 hour window
```

If an upcoming launch is found:

```
$ python project.py -w 48
Notification for 1 Upcoming Space Launch(es)
Upcoming Space Launches:

Launch 1:
    Name: Falcon 9 Block 5 | Starlink Group 6-29
    Status: To Be Confirmed

    Launch Window:
        Start:
            2023-11-21 22:00:00 CST
            2023-11-22 04:00:00 UTC
        End:
            2023-11-22 02:00:00 CST
            2023-11-22 08:00:00 UTC

    Launch Service Provider:
        Name: SpaceX
        Type: Commercial

    Rocket:
        Name: Falcon 9 Block 5

    Mission:
        Name: Starlink Group 6-29
        Description: A batch of satellites for the Starlink mega-constellation - SpaceX's project for space-based Internet communication system.
        Orbit: Low Earth Orbit
        Agencies:
            Name: SpaceX
            Type: Commercial
            Country: USA
    Launch Pad:
        Name: Space Launch Complex 40
        Location: Cape Canaveral, FL, USA

```

## Notification Handlers Config:

This applications loads it's notification handler configuration from a JSON file on disk. From `./config.json` by default. This was done to ease configuration of the tool and to avoid storing sensitive information in the code.

Notification Handlers are made up of a notifiation render, a notification service and it's parameters. There's more information on each in the following sections.

__Note: An exception will be thrown at startup if there are issues loading or validating the configuration file and notifications are enabled.__

Multiple handlers can be configured using the following pseudo-json-schema:
```json
{
    "notification_handlers": [
        {
            "service": "",
            "render": "",    // optional
            "parameters": {}
        },
        {
            "service":"",
            "render": "",    // optional
            "parameters":{}
        }
    ]
}
```

 _By default in "normal mode" a `plaintext` render is used with the `stdout` (dummy) service to output upcoming launches to the command line._

 _The tool can be configured to load and process notifications using the notification handlers from the config file using the `--normal-mode-notif` flag._

### Notification Services
The tool supports customizable notification services. At this time the only notification services implemented are a `stdout` service (essentially a dummy service), and an `email` service. Additional notification services could be added in the future. The tool is designed to make doing so require very refactoring.

_Implementation detail: To add a new notification service. Create a new service class which follows the NotificationService protocol and add a case statement for it to the get_notification_service function in notification_services.py_

#### Notification Renders
The tool supports customizable notification renderers on a per-service basis. At this time only a `plaintext` render is currently implemented. Additional renderers may be added in the future. The tool is designed to make doing so require little refactoring.

If no render is configured `plaintext` will be used.

_Implementation detail: To add a new notification renderer. Create a new renderer class which follows the NotificationRenderer protocol and add a case statement for it to the get_notification_render function in notification_renderers.py_

#### StdOut Notification Service Configuration
There are no configurable parameters for this service.

```json
{
    "notification_handlers": [
        {
            "service": "stdout",
            "renderer": "plaintext", // optional
            "parameters": {}
        }
    ]
}
```

#### Email Notification Service Configuration
The following describes the parameters for the email notification service. All parameters are required unless otherwise noted.
 - `"smtp_server"`: The network hostname of a SMTP server which can be used to send emails
 - `"smtp_port"`: The network port of the SMTP server
 - `"use_tls"`: Set to `true` if the SMTP server requires TLS authentication, `false` if not
 - `"smtp_username"`: Login username for SMTP server, if required (optional)
 - `"smtp_password"`: base64 encoded password for SMTP server, if required (optional)
 - `"email_sender"`: Sending email address. Used in the "From:" field of emails.
 - `"email_recipients"`: A single or list of recipient email addesses. Used in the "To:" field of emails.

```json
{
    "notification_handlers": [
        {
            "service": "email",
            "renderer": "plaintext", // optional
            "parameters": {
                "smtp_server": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "use_tls": true,
                "smtp_username": "username@outlook.com",  // optional
                "smtp_password": "password",              // optional
                "email_sender": "username@outlook.com",
                "email_recipients": ["username@outlook.com"]
            }
        }
    ]
}
```

## Space Launch Library 2 (LL2) API:
This tool makes use of the free-tier of the Space Launch Libary 2 rest API.
It is a database and API which is kept up to date with current and future launches.

> __Important Note!__ </br>
> The free-tier of the API is rate-limited to 15 calls per hour, per IP address. </br>
> You can get an API key if you need to make more requests by supporting TheSpaceDevs on their Patreon.

This is the swagger documentation for the specific REST endpoint this tool uses:
 - https://ll.thespacedevs.com/docs/#/launch/launch_upcoming_list

I made use of the tutorials for the APIs provided here:
 - https://github.com/TheSpaceDevs/Tutorials/

More information the LL2 API, and about The Space Devs is here:
 - https://thespacedevs.com/llapi
 - https://thespacedevs.com/
 - https://www.patreon.com/TheSpaceDevs

## License:
> Copyright ©️ 2023 Scott Cummings </br>
> Apache-2.0 OR MIT
