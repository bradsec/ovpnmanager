#!/usr/bin/env python3

"""
Name:       vpnmanager.py
Modified:   03 November 2019
Author:     Mark Bradley (github.com/mtbradley)
License:    MIT License

Description:
IPVanish OpenVPN server manager and randomiser
- Fetch full IPVanish server list
- Select defined number of servers
- Rank servers based on ping latency
- Select new server from ranked results
- Randomise server selection
- Write OpenVPN configuration file
- Start/stop OpenVPN service
"""

import requests
import subprocess
import sys
import os
import random
from time import sleep
from operator import itemgetter
import urllib.request
import re


def complete_text():
    sys.stdout.write(" [COMPLETE]" + "\n")
    sys.stdout.flush

def error_text():
    sys.stdout.write(" [FAILED]" + "\n")
    sys.stdout.flush

def task(textoutput):
    sys.stdout.write(textoutput)
    sys.stdout.flush()

def info(textoutput):
    print()
    print(textoutput)
    print()

def heading(textoutput):
    dashes = ('-' * (len(textoutput)+2))
    print()
    print(dashes)
    print(" " + textoutput)
    print(dashes)
    print()

def run_command(cmdstr):
# Run a shell OS command
    try:
        sys.stdout.flush()
        proc = subprocess.check_output(cmdstr, shell=True)
        sleep(5)
        complete_text()
    except subprocess.CalledProcessError as e:
        error_text()
        print(e.output)

def openvpn_control(action):
    if action == "stop":
        task("Stopping OpenVPN service...")
        run_command("/etc/init.d/openvpn stop")
    elif action == "start":
        task("Starting OpenVPN service...")
        run_command("/etc/init.d/openvpn start")
    else:
        pass
    sleep(5)

def fetch_server_configs():
    task("Fetching ipvanish server configs...")
    config_url = "https://www.ipvanish.com/software/configs/"
    response = urllib.request.urlopen(config_url)
    url_data = response.read()
    url_text = url_data.decode('utf-8')
    complete_text()
    extracted_servers = []
    # currently filtering only US servers remove US for all
    extracted_servers = re.findall(r'ipvanish-US[\w\.-]+.ovpn', url_text)
    unique_servers = list(dict.fromkeys(extracted_servers))
    vpn_server_list = []
    for server in unique_servers:
        server_full = server[12:][:-5]
        server_location = server_full[:-8]
        server_id = server_full[-7:]
        vpn_server_list.append((server_location, server_id))
    return vpn_server_list

def vpn_server_ping():
    vpn_server_list = []
    vpn_server_list = fetch_server_configs()
    number_of_servers = 30
    random_server_list = random.sample(vpn_server_list, number_of_servers)
    heading("RANDOM {0} VPN SERVER PING RESPONSE TIMES".format(str(number_of_servers)))
    print("{0: <5} {1: <12} {2: <10} {3: <6} {4}".format("No.", "Location", "Server", "Ping", "Rating"))
    vpn_server_results = []
    count = 1
    for vpn_server in random_server_list:
        server_location = vpn_server[0]
        server_id = vpn_server[1]
        cmd = str("ping -c 1 -q -s 16 -w 1 -W 1 " + server_id + ".ipvanish.com 2> /dev/null | awk -F'/' '/avg/{print $5}'")
        try:
            ping_result = subprocess.check_output(cmd, shell=True)
            ping_result = ping_result.decode('utf8').rstrip('\n')
            if ping_result:
                ping_result = int(float(ping_result))
            if not ping_result:
                ping_rating = "NO RESPONSE"
                # Had to add 999 is no response or vpn rank sort does not work
                ping_result = 999
            elif ping_result < 200:
                ping_rating = "EXCELLENT"
            elif (ping_result >= 200) and (ping_result < 250):
                ping_rating = "GOOD"
            elif (ping_result >= 250) and (ping_result < 300):
                ping_rating = "AVERAGE"
            elif (ping_result >= 300):
                ping_rating = "POOR"
            sys.stdout.write("{0: <5} {1: <12} {2: <10} {3: <6} {4}".format(count, server_location, server_id, str(ping_result), ping_rating + "\n"))
            vpn_server_results.append((server_location, server_id, ping_result, ping_rating))
            count += 1
        except subprocess.CalledProcessError as e:
            error_text()
            print(e.output)
    return vpn_server_results

def vpn_server_rank():
    vpn_server_results = []
    vpn_server_results = vpn_server_ping()
    top_server_count = 5
    heading("TOP {} RATED SERVERS BASED ON LATENCY".format(top_server_count))
    #This sorts list by latency time
    servers_ranked = sorted(vpn_server_results, key=itemgetter(2))
    #Write top 10 vpn servers to txt file and display
    vpn_server_file = open('/etc/openvpn/ranked_vpn_server_list.txt', 'w')
    count = 1
    print("{0: <5} {1: <12} {2: <10} {3: <6} {4}".format("Rank", "Location", "Server", "Ping", "Rating"))
    for server in servers_ranked[:top_server_count]:
        server_location = server[0]
        server_id = server[1]
        server_ping = server[2]
        server_rating = server[3]
        print("{0: <5} {1: <12} {2: <10} {3: <6} {4}".format(count, server_location, server_id, str(server_ping) + "ms", server_rating))
        full_server_name = server[1] + ".ipvanish.com"
        vpn_server_file.write(full_server_name + "\n")
        count += 1
    print()
    vpn_server_file.close()

def write_ovpn_config_file():
    vpn_server_file = open('/etc/openvpn/ranked_vpn_server_list.txt', 'r')
    ranked_vpn_server_list = vpn_server_file.read().splitlines()
    vpn_server_file.close()
    task("Selecting random server from top rated list...")
    random_vpn_server = random.choice(ranked_vpn_server_list)
    complete_text()
    info("The selected server is {0}".format(random_vpn_server))
    #Build OpenVPN configuration File
    task("Writing OpenVPN configuration file...")
    ovpn_config_file = open('/etc/openvpn/client.conf', 'w')
    ovpn_config_file.write("client\n")
    ovpn_config_file.write("dev tun\n")
    ovpn_config_file.write("proto udp\n")
    ovpn_config_file.write("remote {0} 443\n".format(random_vpn_server))
    ovpn_config_file.write("resolv-retry infinite\n")
    ovpn_config_file.write("nobind\n")
    ovpn_config_file.write("persist-key\n")
    ovpn_config_file.write("persist-tun\n")
    ovpn_config_file.write("persist-remote-ip\n")
    ovpn_config_file.write("ca ca.ipvanish.com.crt\n")
    ovpn_config_file.write("verify-x509-name {0} name\n".format(random_vpn_server))
    ovpn_config_file.write("comp-lzo\n")
    ovpn_config_file.write("verb 3\n")
    ovpn_config_file.write("auth SHA256\n")
    ovpn_config_file.write("cipher AES-256-CBC\n")
    ovpn_config_file.write("keysize 256\n")
    ovpn_config_file.write("tls-cipher TLS-DHE-RSA-WITH-AES-256-CBC-SHA:TLS-DHE-DSS-WITH-AES-256-CBC-SHA:TLS-RSA-WITH-AES-256-CBC-SHA\n")
    ovpn_config_file.write("auth-user-pass auth.txt\n")
    ovpn_config_file.write("script-security 2\n")
    ovpn_config_file.write("up /etc/openvpn/up.sh\n")
    ovpn_config_file.close()
    complete_text()

def main():
    heading("IPVANISH OPENVPN SERVER MANAGER AND RANDOMISER")
    openvpn_control("stop")
    vpn_server_rank()
    write_ovpn_config_file()
    openvpn_control("start")
    print()

if __name__ == "__main__":
    main()
