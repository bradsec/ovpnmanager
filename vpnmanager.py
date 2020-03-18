#!/usr/bin/env python3

"""
Name:           vpnmanager.py
Modified:       17 March 2020
Author:         Mark Bradley (github.com/mtbradley)
License:        MIT License
Requirements:   Python 3.6+, IPVanish account and working OpenVPN configuration

Description:
IPVanish OpenVPN server manager and randomizer
- Start/stop OpenVPN service
- Fetch and sort IPVanish server list
- Rank servers based on ping latency
- Select random server from top ranked list
- Write OpenVPN configuration file
"""

import subprocess
import random
from time import sleep
from operator import itemgetter
import urllib.request
import re

def show_header():
    """
    Displays information about this program
    """
    print()
    print(__doc__)
    print()


class TermShow:
    """
    Used to set console ANSI escape code for color and other formatting
    """
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    TICK = '\033[0m\033[32m\u2714\033[0m'
    CROSS = '\033[0m\033[31m\u2718\033[0m'
    REPLACELINE = '\x1b[2K\r'
    NEWLINE = '\n'
    SAMELINE = '\r'
    APPENDLINE = ''


def term_message(message, color=TermShow.RESET, style=TermShow.RESET, line=TermShow.APPENDLINE):
    """
    Outputs a terminal message with set color, style and line position
    """
    if color:
        colors = {
            "red": TermShow.RED,
            "green": TermShow.GREEN,
            "yellow": TermShow.YELLOW,
            "blue": TermShow.BLUE,
            "magenta": TermShow.MAGENTA,
            "cyan": TermShow.CYAN
        }
        set_color = colors.get(color.lower())
    else:
        set_color = TermShow.RESET

    if style:
        styles = {
            "normal": TermShow.RESET,
            "bold": TermShow.BOLD,
            "underline": TermShow.UNDERLINE
        }
        set_style = styles.get(style.lower())
    else:
        set_style = TermShow.RESET

    if line:
        lines = {
            "nl": TermShow.NEWLINE,
            "al": TermShow.APPENDLINE,
            "sl": TermShow.SAMELINE
        }
        set_line = lines.get(line.lower())
    else:
        set_line = TermShow.APPENDLINE

    print(f"{set_style}{set_color}{message}{TermShow.RESET}", end=set_line, flush=True)


def block_heading(text):
    """
    Displays a block heading inside formatted box
    """
    header_text = text.upper()
    header_length = len(header_text)
    box_width = int(header_length)
    print()
    print(f"{'':=<{box_width+2}}")
    print(f"{'':<1}{header_text:^{box_width}}{'':>2}")
    print(f"{'':=<{box_width+2}}")
    print()


def task_start(message):
    """
    Displays a start task message for use with task_pass() and task_fail()
    """
    print(f"[ ] {message}", end='', flush=True)


def task_pass():
    """
    Should follow a start_task() message and task display green tick
    """
    print(f"{TermShow.SAMELINE}[{TermShow.TICK}]", end='\n', flush=True)


def task_fail():
    """
    Should follow a start_task() message and task display red cross
    """
    print(f"{TermShow.SAMELINE}[{TermShow.CROSS}]", end='\n', flush=True)


def run_command(cmdstr):
    """
    Use to run an OS based command
    """
    try:
        proc = subprocess.check_output(cmdstr, shell=True)
        sleep(5)
        task_pass()
    except subprocess.CalledProcessError as e:
        task_fail()
        print(e.output)


def openvpn_control(action):
    """
    Use stop and stop the OpenVPN service
    """
    if action == "stop":
        task_start("Stopping OpenVPN service...")
        run_command("/etc/init.d/openvpn stop")
    elif action == "start":
        task_start("Starting OpenVPN service...")
        run_command("/etc/init.d/openvpn start")
    else:
        pass
    sleep(5)


def fetch_server_configs():
    """
    Fetch IPVanish server config file and extract server names
    """
    task_start("Fetching ipvanish server configs...")
    config_url = "https://www.ipvanish.com/software/configs/"
    try:
        response = urllib.request.urlopen(config_url)
        url_data = response.read()
        url_text = url_data.decode('utf-8')
        task_pass()
    except response.CalledProcessError as e:
        task_fail()
        print(e)
    task_start("Extracting servers...")
    try:
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
        task_pass()
        return vpn_server_list
    except Exception as e:
        task_fail()
        print(e)


def vpn_server_ping():
    """
    Ping IPVanish servers and rate based on ping latency
    """
    vpn_server_list = []
    vpn_server_list = fetch_server_configs()
    number_of_servers = 30
    random_server_list = random.sample(vpn_server_list, number_of_servers)
    block_heading(f"Random {number_of_servers} VPN server ping response times")
    print(f"{'No.': <5} {'Location': <12} {'Server': <10} {'Ping': <6} {'Rating'}")
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
            elif ping_result <= 200:
                ping_rating = TermShow.GREEN + "EXCELLENT" + TermShow.RESET
            elif 201 <= ping_result <= 250:
                ping_rating = TermShow.CYAN + "GOOD" + TermShow.RESET
            elif 251 <= ping_result <= 300:
                ping_rating = TermShow.YELLOW + "AVERAGE" + TermShow.RESET
            elif ping_result >= 301:
                ping_rating = TermShow.RED + "POOR" + TermShow.RESET
            print(f"{count: <5} {server_location: <12} {server_id: <10} {str(ping_result): <6} {ping_rating}")
            vpn_server_results.append((server_location, server_id, ping_result, ping_rating))
            count += 1
        except subprocess.CalledProcessError as e:
            print(e.output)
    return vpn_server_results


def vpn_server_rank():
    """
    Sort IPVanish service list based on latency and narrow down list to top 5 and write to file
    """
    vpn_server_results = []
    vpn_server_results = vpn_server_ping()
    top_server_count = 5
    block_heading(f"Top {top_server_count} rated servers based on latency")
    #This sorts list by latency time
    servers_ranked = sorted(vpn_server_results, key=itemgetter(2))
    #Write top 10 vpn servers to txt file and display
    vpn_server_file = open('/etc/openvpn/ranked_vpn_server_list.txt', 'w')
    count = 1
    print(f"{'Rank': <5} {'Location': <12} {'Server': <10} {'Ping': <6} {'Rating'}")
    for server in servers_ranked[:top_server_count]:
        server_location = server[0]
        server_id = server[1]
        server_ping = server[2]
        server_rating = server[3]
        print(f"{count: <5} {server_location: <12} {server_id: <10} {str(server_ping) + 'ms': <6} {server_rating}")
        full_server_name = server[1] + ".ipvanish.com"
        vpn_server_file.write(full_server_name + "\n")
        count += 1
    print()
    vpn_server_file.close()


def write_ovpn_config_file():
    """
    Read top 5 server list file and select random server and write
    OpenVPN configuration file
    """
    vpn_server_file = open('/etc/openvpn/ranked_vpn_server_list.txt', 'r')
    ranked_vpn_server_list = vpn_server_file.read().splitlines()
    vpn_server_file.close()
    task_start("Selecting random server from top rated list...")
    random_vpn_server = random.choice(ranked_vpn_server_list)
    task_pass()
    term_message(f"The selected server is {random_vpn_server}", "cyan", "bold", "nl")
    #Build OpenVPN configuration File
    task_start("Writing OpenVPN configuration file...")
    try:
        ovpn_config_file = open('/etc/openvpn/client.conf', 'w')
        ovpn_config_file.write("client\n")
        ovpn_config_file.write("dev tun\n")
        ovpn_config_file.write("proto udp\n")
        ovpn_config_file.write(f"remote {random_vpn_server} 443\n")
        ovpn_config_file.write("resolv-retry infinite\n")
        ovpn_config_file.write("nobind\n")
        ovpn_config_file.write("persist-key\n")
        ovpn_config_file.write("persist-tun\n")
        ovpn_config_file.write("persist-remote-ip\n")
        ovpn_config_file.write("ca ca.ipvanish.com.crt\n")
        ovpn_config_file.write(f"verify-x509-name {random_vpn_server} name\n")
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
        task_pass()
    except ovpn_config_file.CalledProcessError as e:
        task_fail()
        print(e)


def main():
    """
    Main function
    """
    show_header()
    block_heading("IPVanish OpenVPN Manager and VPN Server Randomizer")
    openvpn_control("stop")
    vpn_server_rank()
    write_ovpn_config_file()
    openvpn_control("start")
    print()

if __name__ == "__main__":
    main()
