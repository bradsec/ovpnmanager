## Python Code Snippets and Scripts

**Clean special characters and filter words from a filename or filepath string**  
**Using Python 3 and regular expression (regex) re module**
```
import re

filter_words = ["nerd", "geek"]

# Clean filepath preserving some formatting appearance using underscores
def clean_re(str_in):
    str_out = str(str_in.lower())
    # Replace any whitespace with underscore
    while " " in str_out:
        str_out = re.sub(r'\s+', '_', str_out)
    # Remove all special characters other than underscore or period
    str_out = re.sub('[^A-Za-z0-9_./]+', '', str_out)
    # Replace all but last period (file extension) with underscores
    str_out = re.sub(r'\.(?=[^.]*\.)', '_', str_out)
    # Replace any double underscores with single
    while "__" in str_out:
            str_out = re.sub(r'\__', '_', str_out)
    # Remove words in string if they match one of the filter_words
    for word in filter_words:
        str_out = re.sub(word, '', str_out, flags=re.IGNORECASE)
    return str_out


dirty_filepath = "Thi$$S---%$@/%@$%iS....A*^%^%#/NErD_____ P-Y-T-H-O-N {GEEK}/file....path  \\\\.__- CleAnEr...&$@.txt"
clean_filepath = clean_re(dirty_filepath)

print("\nPYTHON 3 RE STRING CLEANER FUNCTION FOR FILEPATHS\n")
print("INPUT\ndirty_filepath:\n{}\n".format(dirty_filepath))
print("OUTPUT\nclean_filepath:\n{}\n".format(clean_filepath))
```
Result
```
INPUT
dirty_filepath:
Thi$$S---%$@/%@$%iS....A*^%^%#/NErD_____ P-Y-T-H-O-N {GEEK}/file....path  \\.__- CleAnEr...&$@.txt

OUTPUT
clean_filepath:
this/is_a/_python_/file_path_cleaner_.txt
```
**Random sleep time delay with milliseconds and display counter**  
**Using Python 3 and time.sleep, numpy and random modules**
```
import time
import numpy
import random

def random_time_delay(min_seconds,max_seconds):
    # Use Numpy to get random time between min and max with milliseconds
    random_time = round(numpy.random.uniform(min_seconds,max_seconds),2)
    for x in numpy.arange(0,random_time,0.01):
        print("- Random delay is {} seconds: {}".format(random_time, round(x,2)), end='\r')
        time.sleep(0.01)

print("\nPYTHON 3 RANDOM TIME DELAY")
print("Modules: time.sleep, numpy and random\n")
# set min / max time in seconds
random_time_delay(180,360)
```
Result example:
```
- Random delay is 211.24 seconds: 3.39
```


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
