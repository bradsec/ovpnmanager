# vpnmanager.py
(Tested with Python 3.7.3 on Raspberry Pi 3/4 running Raspbian Buster)

IPVanish OpenVPN Manager and VPN Server Randomizer
- Start/stop OpenVPN service
- Fetch and sort IPVanish server list
- Rank servers based on ping latency
- Select random server from top ranked list
- Write OpenVPN configuration file

Prerequisites:
1. `/etc/openvpn` default openvpn installation path
2. `/etc/openvpn/client.conf` is the default openvpn configuration file
3. `/etc/openvpn/auth.txt` contains IPVanish VPN username and password
4. `/etc/defaults/openvpn` contains line `AUTOSTART="client"`
