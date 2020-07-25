#!/usr/bin/env python3

"""
Name:           debian_ipvanish_ovpnmanager.py
Modified:       25 July 2020
Author:         Mark Bradley (github.com/mtbradley)
Requirements:   Program uses built-in modules from Python 3.6+
                Requires a working IPVanish OpenVPN configuration
                                                                                                         
Description:

IPVanish OpenVPN server manager and randomizer
- Start/stop OpenVPN service
- Fetch and sort IPVanish server list
- Rank servers based on ping latency
- Select random server from top ranked list
- Updates OpenVPN configuration file
- Includes other network functions which can be customised
- Can be run via a cron job at scheduled intervals
"""

import subprocess
import random
import re
import sys
import shlex
import socket
import json
import os
from time import sleep
from operator import itemgetter
from urllib.request import urlopen


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
    CLEARSCREEN = '\x1b[2J'
    NEWLINE = '\n'
    SAMELINE = '\r'
    APPENDLINE = ''
    SHOWCURSOR = '\x1b[?25h'
    HIDECURSOR = '\x1b[?25l'


def show_header():
    """
    Used display spinner while function is running.
    """
    print(TermShow.CLEARSCREEN)
    print(__doc__)


def show_banner():
    print(f"""{TermShow.RED}
    ╔═══╗╔╗  ╔╗╔═══╗╔═╗ ╔╗╔═╗╔═╗╔═══╗╔═╗ ╔╗╔═══╗╔═══╗╔═══╗╔═══╗
    ║╔═╗║║╚╗╔╝║║╔═╗║║║╚╗║║║║╚╝║║║╔═╗║║║╚╗║║║╔═╗║║╔═╗║║╔══╝║╔═╗║
    ║║ ║║╚╗║║╔╝║╚═╝║║╔╗╚╝║║╔╗╔╗║║║ ║║║╔╗╚╝║║║ ║║║║ ╚╝║╚══╗║╚═╝║
    ║║ ║║ ║╚╝║ ║╔══╝║║╚╗║║║║║║║║║╚═╝║║║╚╗║║║╚═╝║║║╔═╗║╔══╝║╔╗╔╝
    ║╚═╝║ ╚╗╔╝ ║║   ║║ ║║║║║║║║║║╔═╗║║║ ║║║║╔═╗║║╚╩═║║╚══╗║║║╚╗
    ╚═══╝  ╚╝  ╚╝   ╚╝ ╚═╝╚╝╚╝╚╝╚╝ ╚╝╚╝ ╚═╝╚╝ ╚╝╚═══╝╚═══╝╚╝╚═╝
    FOR IPVANISH ON DEBIAN BASED OS INCLUDING RASPBERRY Pi OS
    {TermShow.RESET}""")
    sleep(3)


def check_user():
    """
    Check program is being run by a superuser or with sudo.
    """
    block_heading("Check User Permissions")
    task_start("Check program is being run by superuser")
    if not os.geteuid()==0:
        task_fail()
        sys.exit('\nThis program must be run as a superuser. Try using sudo.\n')
    task_pass()


def bold_message(text):
    """
    Print message in bold in nominated colour with newline top and bottom
    """
    print(f"\n{TermShow.CYAN}{TermShow.BOLD}{text}{TermShow.RESET}\n")


def block_heading(text):
    """
    Displays a block heading inside formatted box
    """
    header_text = text.upper()
    header_length = len(header_text)
    box_width = int(header_length)
    print(f'{TermShow.CYAN}')
    print(f"{'':=<{box_width+2}}")
    print(f"{'':<1}{header_text:^{box_width}}{'':>2}")
    print(f"{'':=<{box_width+2}}")
    print(f'{TermShow.RESET}')


def task_start(message):
    """
    Print the task to be run allow space for pass fail box
    """
    print(f'    {message}', end="")


def task_info(message):
    """
    Print the task to be run allow space for pass fail box
    """
    print(f'[{TermShow.CYAN}i{TermShow.RESET}] {message}', end="\n")


def task_error(message):
    """
    Print the task to be run allow space for pass fail box
    """
    print(f'[{TermShow.RED}{TermShow.CROSS}{TermShow.RESET}] {message}', end="\n")


def task_fail():
    """
    Used when a task or functions fails to display a red cross in square brackets. Used after task_message()
    """
    print(f"\r[{TermShow.RED}{TermShow.CROSS}{TermShow.RESET}]", end="\n")


def task_pass():
    """
    Used when a task or functions passes to display a green tick in square brackets. Used after task_message()
    """
    print(f"\r[{TermShow.GREEN}{TermShow.TICK}{TermShow.RESET}]", end="\n")


def run_command_shell(cmd):
    """
    Run an OS based command and return the output.
    """
    output = subprocess.run(cmd, shell=True, capture_output=True)
    return str(output.stdout, 'utf-8').rstrip()


def run_command(cmd):
    """
    Run an OS based command and display if the command ran successfully or failed.
    """
    task_start(f"{cmd}")
    try:
        cmd = shlex.split(cmd)
        output = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, check=True)
        task_pass()
        return output.stdout
    except Exception as e:
        task_fail()
        task_error(e)
        return e


def fetch_server_configs():
    """
    Fetch IPVanish server config file and extract server names
    """
    block_heading("OpenVPN Configuration Files")  
    config_url = "https://www.ipvanish.com/software/configs/"
    task_info(f'Config URL is {config_url}')
    task_start(f"Fetching ipvanish server configs...")
    try:
        response = urlopen(config_url)
        url_data = response.read()
        url_text = url_data.decode('utf-8')
        task_pass()
    except Exception as e:
        task_fail()
        print(e)
        sys.exit('\nFailed to fetch server configs.\n')
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
    Called by vpn_server_rank()
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
        #cmd = str("ping -c 1 -q -s 16 -w 1 -W 1 " + server_id + ".ipvanish.com 2> /dev/null | awk -F'/' '/avg/{print $5}'")
        cmd = str("ping -c 1 -q -s 16 -W 1 " + server_id + ".ipvanish.com 2> /dev/null | awk -F'/' '/avg/{print $5}'")
        try:
            ping_result = run_command_shell(cmd)
            #ping_result = ping_result.decode('utf8').rstrip('\n')
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
            print(f"{count: <5} {server_location: <12} {server_id: <10} {str(ping_result) + 'ms': <6} {ping_rating}")
            vpn_server_results.append((server_location, server_id, ping_result, ping_rating))
            count += 1
        except Exception as e:
            task_error(e)
    return vpn_server_results


def vpn_server_rank():
    """
    Sort IPVanish service list based on latency and narrow down list to top 5 and write to file
    Calls vpn_server_ping()
    """
    vpn_server_results = []
    vpn_server_results = vpn_server_ping()
    top_server_count = 5
    block_heading(f"Top {top_server_count} rated servers based on latency")
    #This sorts list by latency time
    servers_ranked = sorted(vpn_server_results, key=itemgetter(2))
    #Write top 10 vpn servers to txt file and display
    vpn_server_file = open('ranked_vpn_server_list.txt', 'w')
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
    vpn_server_file.close()


def vpn_server_random():
    """
    Read top 5 server list file and select random server called by update_openvpn_config()
    """
    vpn_server_file = open('ranked_vpn_server_list.txt', 'r')
    ranked_vpn_server_list = vpn_server_file.read().splitlines()
    vpn_server_file.close()
    task_start("Selecting random server from ranked list...")
    random_vpn_server = random.choice(ranked_vpn_server_list)
    task_pass()
    task_info(f"The selected server is {TermShow.GREEN}{random_vpn_server}{TermShow.RESET}")
    return random_vpn_server


def update_openvpn_config(filename):
    """
    Update the specified openvpn configuration file with new server information.
    """
    block_heading("Updating openvpn VPN client configuration")
    task_info(f"Configuration file: {filename}")
    new_server = vpn_server_random()
    server_find = "ipvanish.com"
    with open(filename) as config_file:
        config_data = config_file.read()
        try:
            old_server = re.findall(r'[\w\.-]+{0}'.format(server_find), config_data)[0]
            task_info(f'Found old server: {TermShow.YELLOW}{old_server}{TermShow.RESET}')
            task_info(f'Replacing with server: {TermShow.GREEN}{new_server}{TermShow.RESET}')
            task_start(f'Updating config file: {filename}')
            if old_server and old_server != new_server: 
                new_config_data = config_data.replace(old_server, new_server)
                with open(filename, "w") as new_config_file:
                    new_config_file.write(new_config_data)
                    task_pass()
            elif old_server == new_server:
                task_pass()
                task_info(f'The new server is the same as the old server. No changes required.')
        except Exception as e:
            task_fail()
            task_error(f'No match for text "*{server_find}" in {filename}')
            task_error(e)


def debian_service_manager(service, action):
    """
    Start or stop Debian based OS service
    """
    block_heading("OpenVPN Service Manager")
    task_info(f"Running command to {action} {service} service")
    run_command(f'systemctl {action} {service}')


def debian_service_status(service):
    """
    Check if service is active or inactive
    """
    block_heading("Service Status")
    status = run_command_shell(f'systemctl is-active {service}')
    if status:
        task_info(f'The {service} service status is: {status}')
    else:
        task_error(f'Unable to get status of {service} service')
    return status


def check_connection(host, port):
    """
    Check connection to hosts and ports using socket module. Used by check_internet()
    """
    try:
        task_start(f"Testing connection to {host} on port: {port}")
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        task_pass()
        return True
    except socket.error as e:
        task_fail()
        task_error(e)
        return False


def check_internet():
    """
    Use check_connection() to determine Internet connectity. Exit program if check fails.
    """
    block_heading("Testing Internet Connectivity")
    if check_connection("1.1.1.1", 53) and check_connection("google.com", 80):
        task_start("Internet connection test passed")
        task_pass()
        ip_info = get_ip_info()
        return ip_info
    else:
        task_start("Internet connection test failed")
        task_fail()
        sys.exit('\nYou cannot continue without a Internet connection.\n')


def get_ip_info(address=None):
    """
    Get public IP address using ipinfo.io and sockets module to resolve hostname
    An signup api access code may be required depending on usage.
    """
    block_heading("Public IP Address Information")
    task_start("Fetching IP info from ipinfo.io")
    try:
        if address:
            ip_info = json.load(urlopen(f'http://ipinfo.io/{address}/json'))
        else:
            ip_info = json.load(urlopen(f'http://ipinfo.io/json'))
        ip_address = ip_info['ip']
        ip_city = ip_info['city']
        ip_country = ip_info['country']
        task_pass()
        task_info(f'IP: {TermShow.GREEN}{ip_address}{TermShow.RESET} CITY: {ip_city} COUNTRY: {ip_country}')
        return ip_address
    except Exception as e:
        task_fail()
        task_error(e)
        return e


def get_interface_ip(interface):
    """
    Get an interface IP address
    """
    block_heading("Find Interface IP Address")
    task_start(f"Finding IP address of {interface} using ifconfig")
    ip_address = run_command_shell(f'ifconfig {interface} | grep \'inet\' | awk \'$1 == "inet" {{ print $2 }}\'').rstrip()
    if ip_address:
        task_pass()
        task_info(f"IP address for {interface} is: {ip_address}")
        return ip_address
    else:
        task_fail()
        task_error(f"No IP address details found for {interface}")


def check_config_exists(filename):
    if not os.path.isfile(filename):
        sys.exit(f'\nThe openvpn configuration file specified {filename} does not exist.\n')


def main():
    """
    Main function to run program.
    """
    show_header()
    show_banner()
    check_user()
    #ovpn_config_file = "testconfig.conf"
    ovpn_config_file = "/etc/openvpn/client.conf"
    check_config_exists(ovpn_config_file)
    get_ip_info()
    debian_service_manager("openvpn", "stop")
    vpn_server_rank()
    update_openvpn_config(ovpn_config_file)
    debian_service_manager("openvpn", "start")
    task_info(f'Waiting for 10 seconds for VPN tunnel to be established...')
    sleep(10)
    get_ip_info()
    debian_service_status("openvpn")
    check_internet()
    print()


if __name__ == "__main__":
    main()
