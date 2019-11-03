# raspberrypi
Raspberry Pi related scripts

# backuptoemail.py
Zip/tar backup system files and email as attachment to a
recipient using Gmail SMTP. Best for small backups like
system configuration files.

Tested with Python 3.7.3 on Raspberry Pi 3 running Raspbian Buster.

Prerequisites:
1. Requires a Gmail account with less secure app access enabled.
2. Set details in the backup() functions with email user password etc.
3. File back up paths can be set in backup() under file_path_list
