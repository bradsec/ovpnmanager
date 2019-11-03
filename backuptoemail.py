#!/usr/bin/env python3

"""
Name:       backuptoemail.py
Modified:   03 November 2019
Author:     Mark Bradley (github.com/mtbradley)
License:    MIT License

Description:
Zip/tar backup system files and email as attachment to a
recipient using Gmail SMTP.
"""

import os
import time
import subprocess
import sys
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders

def get_date():
    getNow = (time.strftime("%d%m%y_%H%M"))
    return str(getNow)

def info(output):
    sys.stdout.write(output)
    sys.stdout.flush()

def complete_text():
    sys.stdout.write("[COMPLETE]" + "\n")
    sys.stdout.flush

def error_text():
    sys.stdout.write("[FAILED]" + "\n")
    sys.stdout.flush

def heading(textoutput):
    dashes = ('-' * (len(textoutput)+2))
    print()
    print(dashes)
    print(" " + textoutput)
    print(dashes)
    print()

def run_command(cmdstr, verbose):
    cmd = str(cmdstr).split(" ")
    if verbose is True:
        sys.stdout.flush()
    try:
        sys.stdout.flush()
        proc = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        if verbose is True:
            complete_text()
        return str(proc), True
    except (subprocess.CalledProcessError, Exception) as e:
        if verbose is True:
            error_text()
            print (e.output)
        return False

def backup():
    # Set these top three values to your gmail account details
    to_email_address = "YOUR_RECIPIENT_EMAIL"
    from_email_address = "YOUR_GMAIL_EMAIL"
    from_email_password = "YOUR_GMAIL_PASSWORD"
    backup_date = get_date()
    hostname = os.uname()[1]
    # Set file paths to backup
    file_path_list = ["/home","/etc","/usr/local/sbin"]
    file_paths = ' '.join(file_path_list)
    backup_file_name = "backup_{}_{}.tar.gz".format(hostname, backup_date)
    # Format OS command strings to pass to run_command function later on
    tar_backup_command = ("tar --exclude-ignore='{}' -cpzf {} --absolute-names {}".format(backup_file_name, backup_file_name, file_paths))
    rm_backup_command = ("rm {}".format(backup_file_name))

    heading("PYTHON BACKUP TO EMAIL USING GMAIL")
    info("Backup file name...........: {}\n".format(backup_file_name))
    info("Backup paths...............: {}\n".format(file_paths))
    info("Creating backup archive....: ")
    run_command(tar_backup_command, True)
    backup_size = int(os.path.getsize(backup_file_name)/1024)
    info("Backup archive size........: {}KB\n".format(backup_size))
    info("Backup email recipient.....: {}\n".format(to_email_address))
    info("Emailing backup archive....: ")
    # Set max email file attachment size in KB
    max_size = 5000
    if backup_size > max_size:
        error_text()
        print("File attachment exceeds {}MB".format(max_size/1000))
        return
    mailer(to_email_address, from_email_address, from_email_password, "Backup sent from {} device".format(hostname), "Backup file {} attached.".format(backup_file_name), backup_file_name)
    info("Removing backup archive....: ")
    run_command(rm_backup_command, True)

def mailer(to_email_address, from_email_address, from_email_password, subject, body, attachment):
    msg = MIMEMultipart() 
    msg['From'] = from_email_address  
    msg['To'] = to_email_address 
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain')) 
    attachment_path = open(attachment, "rb")
    attachment_name = os.path.basename(attachment) 
    p = MIMEBase('application', 'octet-stream') 
    p.set_payload((attachment_path).read()) 
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename={}".format(attachment_name))
    msg.attach(p) 
    smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        smtp_session.starttls() 
        smtp_session.login(from_email_address, from_email_password) 
        smtp_session.sendmail(from_email_address, to_email_address, msg.as_string())
    except smtplib.SMTPException as e:
        error_text()
        print(e)
    finally:
        smtp_session.quit()
        complete_text()

def main():
    backup()
    print()

if __name__ == '__main__':
    main()