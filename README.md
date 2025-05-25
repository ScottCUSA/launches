# Space Launch Notifications
## Description:
A tool which checks for upcoming space launches using the space launch library 2 (LL2) API and can send notifications if upcoming launches are found.

The tool has two modes:
 - The normal mode performs a check for upcoming launches within a 24 hour window, and outputs any upcoming space launches on the command line.
 - The service mode performs a check for upcoming launches repeatedly, at a configurable schedule, until the user presses `Ctrl+C`. </br>
   In this mode a notification will be sent via the configured notification services if upcoming launches are found. More on this later.

The service mode supports two scheduling methods:
 - Daily Scheduling (default): Checks for upcoming launches at specific times each day (e.g., "07:00", "19:00")
 - Periodic Scheduling: Checks for upcoming launches at fixed time intervals (e.g., every 24 hours)

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

## Launches Config JSON:

This applications loads it's configuration from a JSON file on disk. From `./config.json` by default. This was done to ease configuration of the tool and to avoid storing sensitive information in the code.

Notification Handlers are made up of a notifiation render, a notification service and it's parameters. There's more information on each in the following sections.

__Note: An exception will be thrown at startup if there are issues loading or validating the configuration file.__

```json
{
    "periodic": false,
    "search_window_hours": 48,
    "search_repeat_hours": 24,
    "time_zone": "America/Chicago",
    "daily_check_times": [
        "07:00",
        "19:00"
    ],
    "cache_enabled": true,
    "cache_directory": "./.launches_cache",
    "notification_handlers": [
        {
            "service": "",
            "render": "",
            "parameters": {}
        },
        {
            "service":"",
            "render": "",
            "parameters":{}
        }
    ]
}
```

### Scheduling Configuration:

The tool now defaults to using daily scheduling instead of periodic scheduling. The scheduling behavior can be configured with these parameters:

- `"periodic"`: Boolean flag to choose between periodic (true) or daily (false) scheduling. Defaults to `false` (daily scheduling).
- `"search_window_hours"`: How far ahead in the future to search for launches, in hours. Defaults to 24 hours.
- `"search_repeat_hours"`: For periodic scheduling, how often to repeat the checks, in hours. Defaults to 24 hours.
- `"time_zone"`: IANA timezone string (e.g., "America/Chicago") used for the daily check times. Defaults to "America/Chicago".
- `"daily_check_times"`: Array of times (in 24-hour "HH:MM" format) to check for launches each day. Defaults to ["07:00", "19:00"].

### Cache Configuration:

The tool implements a caching mechanism to avoid sending duplicate notifications for launches that haven't changed since the last check. This is particularly useful in service mode, where checks are performed repeatedly. The cache stores information about previously seen launches and only triggers notifications when new launches are detected or existing launches have significant changes.

A launch is considered to have "significantly changed" if any of the following occurs:
- The launch status changes (e.g., from "To Be Confirmed" to "Go for Launch")
- The launch window start time changes
- New information URLs are added
- New video URLs are added
- The "No Earlier Than" (NET) date changes

Cache configuration parameters:

- `"cache_enabled"`: Boolean flag to enable or disable the caching mechanism. Defaults to `true`.
- `"cache_directory"`: The directory where the cache file will be stored. Defaults to "./.launches_cache".

### Notification Services
The tool supports customizable notification services. At this time the notification services implemented are a `stdout` service, an `email` service, and a `gmail` service. 

_Implementation detail: To add a new notification service. Create a new service class which follows the NotificationService protocol and add a case statement for it to the get_notification_service function in notification_services.py_

#### Notification Renders
The tool supports customizable notification renderers on a per-service basis. At this time the renderers implemented include `plaintext` and `html`. Additional renderers may be added in the future.

If no render is configured `plaintext` will be used.

_Implementation detail: To add a new notification renderer. Create a new renderer class which follows the NotificationRenderer protocol and add a case statement for it to the get_notification_render function in notification_renderers.py_

#### StdOut Notification Service Configuration
There are no configurable parameters for this service.

```json
{
    "notification_handlers": [
        {
            "service": "stdout",
            "renderer": "plaintext",
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
 - `"sender"`: Sending email address. Used in the "From:" field of emails.
 - `"recipients"`: A single or list of recipient email addesses. Used in the "To:" field of emails.

```json
{
    "notification_handlers": [
        {
            "service": "email",
            "renderer": "plaintext",
            "parameters": {
                "smtp_server": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "use_tls": true,
                "smtp_username": "email@outlook.com",  
                "smtp_password": "base64encodedpassword",
                "sender": "email@outlook.com",
                "recipients": ["email@outlook.com"]
            }
        }
    ]
}
```

#### Gmail Notification Service Configuration

> **Important Note!**
> The Gmail notification service requires Google API Client credentials that are not provided with this tool. Also, this notification service will ONLY work in a desktop environment as it requires the ability for users to log into their Google account through a browser to obtain a refresh token.

The Gmail notification service uses the Google Gmail API to send emails through a Gmail account. It requires OAuth2 authentication, which is handled by the Google API Client libraries. The first time you run the tool with Gmail notification enabled, it will open a browser window and ask you to authenticate with your Google account.

The following describes the parameters for the Gmail notification service. All parameters are required.
 - `"credentials_file"`: Path to the Google API credentials file (JSON format) obtained from the Google Cloud Console
 - `"token_file"`: Path where the OAuth2 refresh token will be stored after authentication
 - `"recipients"`: A single or list of recipient email addresses. Used in the "To:" field of emails.

```json
{
    "notification_handlers": [
        {
            "service": "gmail",
            "renderer": "html",
            "parameters": {
                "credentials_file": "credentials.json",
                "token_file": "token.json",
                "recipients": ["email@example.com"]
            }
        }
    ]
}
```

To use the Gmail notification service, you must:
1. Create a Google Cloud Platform project
2. Enable the Gmail API
3. Create OAuth2 credentials (Desktop client)
4. Download the credentials as a JSON file and save it as specified in your config

The first time the service runs, it will prompt you to authorize the application by opening a browser window.

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
> Copyright ©️ 2024 Scott Cummings </br>
> Apache-2.0 OR MIT
