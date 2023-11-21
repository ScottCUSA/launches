# Space Launch Notifications
# Description:
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

## Notifications Config:

This applications loads notification configurations from `./config.json` by default. The reason the configuration options are loaded from disk is to easy configuration of the tool, and to avoid storing any sensitive information inside of the project's code. In a production environment it may be preferred to use environment variables, or some other secrets vault of some kind, to store credentials rather than a file on disk.

An exception will be thrown at startup if notifications are expected but there issues loading or validating the configuration file.

Multiple services can be configured using the following pseudo-schema:
```json
{
    "notification_services": [
        {
            "service": "",
            "parameters": {}
        },
        {
            "service": "",
            "parameters": {}
        }
    ]
}
```

### Notification Renders
The tool supports customizable notification renderers on a per-service basis. At this time only a `plaintext` render is currently implemented.
Other renderers could be added with little modifiation, such as an `html` render, but they are outside the scope of the project.


### Notification Services
The only notification services currently provided are `stdout` (a dummy service), and `email`.
Others could be added, with little modification, such as an X (Twitter) service, or a Telegram service, but they are outside the scope of the project.

#### StdOut Service Configuration
There are no configurable parameters for this service.

Example config:
```json
{
    "notification_services": [
        {
            "service": "stdout",
            "renderer": "plaintext", // optional
            "parameters": {}
        }
    ]
}
```

#### Email Service Configuration
The following describes the parameters for the service. The parameters are required unless otherwise noted.
 - `"smtp_server"`: The network hostname of a SMTP server which can be used to send emails
 - `"smtp_port"`: The network port of the SMTP server
 - `"use_tls"`: Set to `true` if the SMTP server requires TLS authentication, `false` if not
 - `"smtp_username"`: Login username for SMTP server, if required (optional)
 - `"smtp_password"`: Login password for SMTP server, if required (optional)
 - `"email_sender"`: Sending email address. Used in the "From:" field of emails.
 - `"email_recipients"`: A single or list of recipient email addesses. Used in the "To:" field of emails.

Example Config:
```json
{
    "notification_services": [
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

## Design Notes:



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
> GNU General Public License V3 </br>
> https://www.gnu.org/licenses/gpl-3.0.en.html
