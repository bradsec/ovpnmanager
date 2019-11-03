# raspberrypi
Raspberry Pi related shell and python scripts.

Assist with automation, system administration etc.

# vpnmanager.py
(Tested with Python 3.7.3 on Raspberry Pi 3 running Raspbian Buster)

IPVanish OpenVPN server manager and randomiser
- Fetch full IPVanish server list
- Select defined number of servers
- Rank servers based on ping latency
- Select new server from ranked results
- Randomise server selection
- Write OpenVPN configuration file
- Start/stop OpenVPN service

Prerequisites:
1. Default /etc/openvpn installation path
2. Using client.conf as startup openvpn configuration file
3. IPVanish username and password stored in /etc/openvpn/auth.txt file.

# backuptoemail.py
(Tested with Python 3.7.3 on Raspberry Pi 3 running Raspbian Buster)

Zip/tar backup system files and email as attachment to a
recipient using Gmail SMTP. Best for small backups like
system configuration files.

Prerequisites:
1. Requires a Gmail account with less secure app access enabled.
2. Set account details in the backup() function.
3. File backup paths can be set in backup() function under file_path_list
