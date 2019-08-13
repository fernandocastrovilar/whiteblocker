# White Blocker

White Blocker is a software which provides an automatic blocking of IPs which tries to scan or penetrate into the system and graphic administration for block incoming ip traffic.

## Installation
In order to run WhiteBlocker and install all its dependencies, it will be necessary to have pipenv installed.
```bash
apt-get install pipenv
```
Then, clone repo and install dependencies:
```bash
git clone https://github.com/fernandocastrovilar/whiteblocker.git && cd whiteblocker/
pipenv install
```

## Configuration
The only configuration needed is to set the correct parameters for having notifications working.

To get email notifications, just write on "credentials.txt" the gmail account which is going to be used to send the emails:
```bash
echo "username:password" > credentials.txt
```
The other parameter is the account where you like to have the emails sent. This can be set editing "whitheblocker_api.py" on line 10, under parameter "recipient" variable.

## Roadmap
- Create the agent who listen on a unused system port and notify of a TCP handshake.
- Wake up the web interface for administrate the blocked IPs by the automatic process and add the option to manual block/unblock ips.
- Setup the notification service for the automatic process which block IPs to notify when an IP is started to be blocked or someone is trying to scan/break into the system. - Telegram Bot and Desktop notifications-
- To adapt software to be compatible with Windows environments.
- Documentation and installation guide.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0)
