# vpnmanager.py
(Tested with Python 3.7.3 on Raspberry Pi 3/4 running Raspbian Buster)

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
