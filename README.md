# raspberrypi
Raspberry Pi related scripts

# backuptoemail.py
Zip/tar backup system files and email as attachment to a
recipient using Gmail SMTP. Best for small backups like
system configuration files.

Tested with Python 3.7.3 on Raspberry Pi 3 running Raspbian Buster.

Prerequisites:
1. Requires a Gmail account with less secure app access enabled.
2. Set account details in the backup() function.
3. File backup paths can be set in backup() function under file_path_list
