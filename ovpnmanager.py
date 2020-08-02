#!/usr/bin/env python3

"""
Name:           ovpnmanager.py
Modified:       03 AUG 2020
Author:         Mark Bradley (github.com/mtbradley)
Requirements:   Program uses built-in modules from Python 3.6+
                Requires a working IPVanish OpenVPN configuration
License:        MIT (https://opensource.org/licenses/MIT)
"""

import subprocess
import random
import re
import sys
import shlex
import socket
import time
import argparse
import json
import os
from operator import itemgetter
from urllib.request import urlopen


class TermShow:
    """
    Used to set console ANSI escape code for color and other formatting
    """
    RED = '\033[31m'
    BRRED = '\033[91m'
    GREEN = '\033[32m'
    BRGREEN = '\033[92m'
    YELLOW = '\033[33m'
    BRYELLOW = '\033[93m'
    BLUE = '\033[34m'
    BLUE = '\033[94m'
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
    Display program header information
    """
    print(TermShow.CLEARSCREEN)
    print(__doc__)


def show_banner():
    print(f'''{TermShow.RED}                                            
  .d8888b. dP   .dP 88d888b. 88d888b.                              
  88'  `88 88   d8' 88'  `88 88'  `88                              
  88.  .88 88 .88'  88.  .88 88    88                              
  `88888P' 8888P'   88Y888P' dP    dP                              
                    88                                                                     
88d8b.d8b. .d8888b. 88d888b. .d8888b. .d8888b. .d8888b. 88d888b. 
88'`88'`88 88'  `88 88'  `88 88'  `88 88'  `88 88ooood8 88'  `88 
88  88  88 88.  .88 88    88 88.  .88 88.  .88 88.  ... 88       
dP  dP  dP `88888P8 dP    dP `88888P8 `8888P88 `88888P' dP       
                                           .88                   
                                       d8888P                    
{TermShow.RESET}''')


def get_date():
    """
    Return date and (24)hour and minutes
    Current result example: 29JUL2020_2222
    """
    getNow = (time.strftime("%d%b%Y_%H%M"))
    return str(getNow)


def check_user():
    """
    Check program is being run by a superuser or with sudo.
    """
    task_start("Check program is being run by superuser")
    if not os.geteuid() == 0:
        task_fail()
        task_error('This program must be run as a superuser. Try using sudo.')
        sys.exit(1)
    task_pass()
    print()


def bold_message(text):
    """
    Print message in bold in nominated colour with newline top and bottom
    """
    print(f'\n{TermShow.CYAN}{TermShow.BOLD}{text}{TermShow.RESET}\n')


def block_heading(text):
    """
    Displays a block heading inside formatted box
    """
    header_text = text.upper()
    header_length = len(header_text)
    box_width = int(header_length)
    print(f'')
    print(f'{"+":-<{box_width+5}}+')
    print(f'{"|":<3}{header_text:^{box_width}}{"|":>3}')
    print(f'{"+":=<{box_width+5}}+')
    print(f'')


def task_start(message):
    """
    Print the task to be run allow space for pass fail box
    """
    print(f'\r[-] {message}', end="", flush=True)


def task_error(message):
    """
    Print the task to be run allow space for pass fail box
    """
    print(f'[{TermShow.RED}{TermShow.CROSS}{TermShow.RESET}]{TermShow.RED} \
{message}{TermShow.RESET}\n', end="\n", flush=True)


def task_info(message):
    """
    Print the task to be run allow space for pass fail box
    """
    print(f'[{TermShow.CYAN}{TermShow.BOLD}i{TermShow.RESET}] \
{message}', end="\n", flush=True)


def task_fail():
    """
    Used when a task or functions fails to display a red FAILED. Used after task_message()
    """
    print(
        f'\r[{TermShow.RED}{TermShow.BOLD}{TermShow.CROSS}{TermShow.RESET}]', end="\n", flush=True)


def task_pass():
    """
    Used when a task or functions passes to display a green OK. Used after task_message()
    """
    print(
        f'\r[{TermShow.BRGREEN}{TermShow.BOLD}{TermShow.TICK}{TermShow.RESET}]', end="\n", flush=True)


def get_arguments():
    """
    Get command line arguments for use in program functions.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--servers", "-s", dest="servers", type=int, default=30,
                        help="Set number of servers to test for ping latency response. Default is 30")
    parser.add_argument("--filter", "-f", dest="filter", type=str, default=None,
                        help="Set server country code for VPN server location such as US. Default is None")
    args = parser.parse_args()
    if args:
        if args.servers:
            task_info(f"Server list count set to {args.servers}")
        if args.filter:
            if len(args.filter) > 2:
                task_error(
                    f"The specified -f filter country code {args.filter} is invalid.")
                task_info("Resetting country filter to None")
                args.filter = None
            else:
                task_info(f"Server country filter set to {args.filter}")
        print()
    return args


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
        output = subprocess.run(cmd, stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE, universal_newlines=True, check=True)
        task_pass()
        return output.stdout
    except Exception as e:
        task_fail()
        task_error(e)
        return e


def table_decorator(column_widths, seperator="+", spacer=""):
    """
    Print table decorator with spacer and seperator symbols
    """
    for i, width in enumerate(column_widths):
        if i < len(column_widths)-1:
            print(f"{seperator}{'':{spacer}<{width+2}}", end="", flush=True)
        else:
            print(f"{seperator}{'':{spacer}<{width+2}}{seperator}", end="\n", flush=True)


def table_row_data(column_widths, row_data, color=""):
    """
    Print table row data with column seperator symbol
    """
    seperator = "|"
    if len(column_widths) != len(row_data):
        print("The amount of columns are not equal to the column data values.")
    else:
        for i, (width, data) in enumerate(zip(column_widths, row_data)):
            data = str(data[:width])
            if i == 0:
                print(
                    f"{seperator} {color}{data: <{width}}{TermShow.RESET}", end="", flush=True)
            elif i < len(column_widths)-1:
                print(
                    f" {seperator} {color}{data: <{width}}{TermShow.RESET}", end="", flush=True)
            else:
                print(
                    f" {seperator} {color}{data: <{width}}{TermShow.RESET} {seperator}", end="\n", flush=True)


def fetch_server_configs(server_filter):
    """
    Fetch IPVanish server config file and extract server names
    """
    config_url = "https://www.ipvanish.com/software/configs/"
    task_start(f"Fetching IPVanish server locations")
    try:
        response = urlopen(config_url)
        url_data = response.read()
        url_text = url_data.decode('utf-8')
        task_pass()
    except Exception as e:
        task_fail()
        task_error(e)
        task_error("Failed to fetch server configs.")
        sys.exit(1)

    if server_filter:
        task_info(f"Filtering server list for {server_filter} based servers")
    try:
        extracted_servers = []
        # currently filtering only US servers remove US for all
        if server_filter:
            extracted_servers = re.findall(
                r'ipvanish-{0}[\w\.-]+.ovpn'.format(server_filter), url_text, re.IGNORECASE)
        else:
            extracted_servers = re.findall(r'ipvanish-[\w\.-]+.ovpn', url_text)
        unique_servers = list(dict.fromkeys(extracted_servers))
        if not unique_servers:
            task_error(
                "No servers found. An invalid country filter may have been applied.")
            sys.exit(1)
        vpn_server_list = []
        for server in unique_servers:
            server_full = server[12:][:-5]
            server_location = server_full[:-8]
            server_id = server_full[-7:]
            vpn_server_list.append((server_location, server_id))
        return vpn_server_list
    except Exception as e:
        task_fail()
        task_error(e)


def check_os():
    task_info(f'Checking for debian or pfsense based OS')
    o_s = None
    if os.path.isfile("/etc/debian_version"):
        o_s = "debian"
        task_start(f"Detected {o_s} based OS")
        task_pass()
    check_output = str(run_command_shell('cat /etc/platform')).lower()
    if "pfsense" in check_output:
        o_s = "pfsense"
        task_start(f"Detected {o_s} Firewall")
        task_pass()
    if o_s:
        return o_s
    else:
        task_error("No compatible OS found")


def vpn_server_ping(server_count, server_filter):
    """
    Ping IPVanish servers and rate based on ping latency
    Called by vpn_server_rank()
    """
    print()
    vpn_server_list = []
    vpn_server_list = fetch_server_configs(server_filter)
    number_of_servers = server_count
    task_info(f"Total servers found: {len(vpn_server_list)}")
    random_server_list = random.sample(vpn_server_list, number_of_servers)
    print(f"\nRandom {number_of_servers} VPN server ping response times...")
    column_widths = [4, 14, 8, 6, 10]
    column_labels = ["No.", "LOCATION", "SERVER", "PING", "RATING"]
    table_decorator(column_widths, "+", "-")
    table_row_data(column_widths, column_labels)
    table_decorator(column_widths, "+", "=")
    vpn_server_results = []
    count = 1
    for vpn_server in random_server_list:
        server_location = vpn_server[0]
        server_id = vpn_server[1]
        cmd = str("ping -c 1 -q -s 16 -W 1 " + server_id +
                  ".ipvanish.com 2> /dev/null | awk -F'/' '/avg/{print $5}'")
        try:
            ping_result = run_command_shell(cmd)
            if ping_result:
                ping_result = int(float(ping_result))
            if not ping_result:
                ping_rating = "NO RESPONSE"
                # Add 999 if no response to prevent problems with sort.
                ping_result = 999
            elif ping_result <= 150:
                ping_rating = 'EXCELLENT'
                result_color = TermShow.BRGREEN
            elif 151 <= ping_result <= 200:
                ping_rating = 'GOOD'
                result_color = TermShow.GREEN
            elif 201 <= ping_result <= 250:
                ping_rating = 'AVERAGE'
                result_color = TermShow.YELLOW
            elif ping_result >= 251:
                ping_rating = 'POOR'
                result_color = TermShow.BRRED
            result_data = [str(count), str(server_location).upper(), server_id, str(ping_result) + "ms", ping_rating]
            table_row_data(column_widths, result_data, result_color)
            vpn_server_results.append(
                (server_location, server_id, ping_result, ping_rating))
            count += 1
        except Exception as e:
            task_error(e)
    table_decorator(column_widths, "+", "-")
    print()
    return vpn_server_results


def vpn_server_rank(server_count, server_filter):
    """
    Sort IPVanish service list based on latency and narrow down list to top 5 and write to file
    Calls vpn_server_ping()
    """
    vpn_server_results = []
    vpn_server_results = vpn_server_ping(server_count, server_filter)
    top_server_count = 5
    print(f"Top {top_server_count} rated servers based on latency")
    # This sorts list by latency time
    servers_ranked = sorted(vpn_server_results, key=itemgetter(2))
    # Write top 10 vpn servers to txt file and display
    vpn_server_file = open('ranked_vpn_server_list.txt', 'w')
    count = 1
    column_widths = [4, 14, 8, 6, 10]
    column_labels = ["RANK", "LOCATION", "SERVER", "PING", "RATING"]
    table_decorator(column_widths, "+", "-")
    table_row_data(column_widths, column_labels)
    table_decorator(column_widths, "+", "=")
    for server in servers_ranked[:top_server_count]:
        server_location = server[0]
        server_id = server[1]
        server_ping = server[2]
        server_rating = server[3]
        result_data = [str(count), str(server_location).upper(), server_id, str(server_ping) + "ms", server_rating]
        table_row_data(column_widths, result_data)
        full_server_name = server[1] + ".ipvanish.com"
        vpn_server_file.write(full_server_name + "\n")
        count += 1
    table_decorator(column_widths, "+", "-")
    vpn_server_file.close()
    print()


def vpn_server_random():
    """
    Read top 5 server list file and select random server called by update_openvpn_config()
    """
    vpn_server_file = open('ranked_vpn_server_list.txt', 'r')
    ranked_vpn_server_list = vpn_server_file.read().splitlines()
    vpn_server_file.close()
    random_vpn_server = random.choice(ranked_vpn_server_list)
    task_info(f"Random new server: {random_vpn_server}")
    return random_vpn_server


def update_openvpn_config(filename, new_server):
    """
    Update the specified openvpn configuration file with new server information.
    """
    server_find = "ipvanish.com"
    with open(filename) as config_file:
        config_data = config_file.read()
        try:
            old_server = re.findall(
                r'[\w\.-]+{0}'.format(server_find), config_data)[0]
            task_info(f'Found old server: {old_server}')
            task_start(f'Updating new server in config file: {filename}')
            if old_server and old_server != new_server:
                new_config_data = config_data.replace(old_server, new_server)
                with open(filename, "w") as new_config_file:
                    new_config_file.write(new_config_data)
                    task_pass()
            elif old_server == new_server:
                task_pass()
                task_info(
                    f'The new server is the same as the old server. No changes required.')
        except Exception as e:
            task_fail()
            task_error(f'No match for text "*{server_find}" in {filename}')
            task_error(e)
    config_file.close()


def debian_service_manager(service, action):
    """
    Start or stop Debian based OS service
    """
    print()
    task_info(f"Running command to {action} {service} service...")
    run_command(f'systemctl {action} {service}')


def pfsense_service_manager(client_number, action):
    """
    Restart openvpn on pfsense server
    """
    print()
    task_info(f"Running command to {action} pfsense openvpn service...")
    run_command(
        f'/usr/local/sbin/pfSsh.php playback svc {action} openvpn client {client_number}')


def debian_service_status(service):
    """
    Check if service is active or inactive
    """
    print()
    task_info("Checking OpenVPN service status")
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
    task_info("Testing Internet connectivity...")
    if check_connection("1.1.1.1", 53) and check_connection("google.com", 80):
        ip_info = get_ip_info()
        return ip_info
    else:
        task_error('You cannot continue without a Internet connection.')
        sys.exit(1)


def get_ip_info(address=None):
    """
    Get public IP address using ipinfo.io and sockets module to resolve hostname
    An signup api access code may be required depending on usage.
    Will only show VPN IP if the OpenVPN interface is the default route of all traffic
    Otherwise your normal service provider WAN IP will be displayed.
    """
    print()
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
        task_info(
            f'IP Address: {TermShow.UNDERLINE}{ip_address}{TermShow.RESET} - City: {ip_city} - Country: {ip_country}')
        return ip_address
    except Exception as e:
        task_fail()
        task_error(e)
        return e


def get_interface_ip(interface):
    """
    Get an interface IP address
    """
    print()
    task_start(f"Finding IP address of {interface} using ifconfig")
    ip_address = run_command_shell(
        f'ifconfig {interface} | grep \'inet\' | awk \'$1 == "inet" {{ print $2 }}\'').rstrip()
    if ip_address:
        task_pass()
        task_info(f"IP address for {interface} is: {ip_address}")
        return ip_address
    else:
        task_fail()
        task_error(f"No IP address details found for {interface}")


def check_config_exists(filename):
    print()
    task_start(f'Checking for config file: {filename}')
    if not os.path.isfile(filename):
        task_fail()
        task_error(f'\nConfig file {filename} does not exist.\n')
        sys.exit(1)
    else:
        task_pass()


def wait_for(seconds):
    """
    Wait for number of seconds.
    """
    width = 10
    bar_movement = width / (seconds*10)
    x = bar_movement
    second_count = 0
    for i in range(0, seconds*10):
        x += bar_movement
        if i % 10 == 0:
       	    second_count += 1
        wait = seconds - (second_count) + 1
        bar_full = "-" * (width - int(x))
        bar_part = "#" * int(x)
        task_start(f"Waiting for {wait} seconds [{bar_part}{bar_full}]")
        time.sleep(0.1)
        print(f"\r{' '*40}", end="")
    print("\r[+] The wait is over", end="")
    task_pass()


def main():
    """
    Main function to run program.
    """
    show_header()
    show_banner()
    block_heading(f"IPVANISH OVPNMANGER STARTING {get_date()}")
    options = get_arguments()
    check_user()
    server_os = check_os()
    server_count = options.servers
    server_filter = options.filter
    if server_os == "debian":
        # Config filename may need to be changed depending on setup
        #ovpn_config_file = "testconfig.conf"
        ovpn_config_file = "/etc/openvpn/client.conf"
        check_config_exists(ovpn_config_file)
        check_internet()
        debian_service_manager("openvpn", "stop")
        wait_for(5)
        vpn_server_rank(server_count, server_filter)
        new_server = vpn_server_random()
        update_openvpn_config(ovpn_config_file, new_server)
        debian_service_manager("openvpn", "start")
        wait_for(10)
        check_internet()
    elif server_os == "pfsense":
        pfsense_config_file = "/cf/conf/config.xml"
        check_config_exists(pfsense_config_file)
        check_internet()
        vpn_server_rank(server_count, server_filter)
        new_server = vpn_server_random()
        update_openvpn_config(pfsense_config_file, new_server)
        # Workaround until issue with old server caching can be fixed.
        # Number before restart will need to be changed depending on config file name
        # in /var/etc/openvpn/clientx.conf
        pfsense_service_manager("2", "restart")
        wait_for(5)
        pfsense_service_manager("2", "restart")
        wait_for(5)
        pfsense_service_manager("2", "restart")

    block_heading(f"OVPNMANGER HAS FINISHED {get_date()}")


if __name__ == "__main__":
    main()
