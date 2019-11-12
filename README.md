## Python scripts
Assist with task automation, system administration etc.

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
1. `/etc/openvpn` default openvpn installation path
2. `/etc/openvpn/client.conf` is the default openvpn configuration file
3. `/etc/openvpn/auth.txt` contains IPVanish VPN username and password
4. `/etc/defaults/openvpn` contains line `AUTOSTART="client"`

# backuptoemail.py
(Tested with Python 3.7.3 on Raspberry Pi 3 running Raspbian Buster)

Zip/tar backup system files and email as attachment to a
recipient using Gmail SMTP. Best for small backups like
system configuration files.

Prerequisites:
1. Requires a Gmail account with less secure app access enabled.
2. Set account details in the `backup()` function.
3. File backup paths can be set in `backup()` function under `file_path_list`
