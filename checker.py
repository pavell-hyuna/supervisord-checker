import configparser
import requests
import subprocess
import smtplib
import os
from time import sleep


def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.abspath(os.getcwd())), 'conf', 'config.ini'))
    if not config.sections():
    	raise Exception("Empty or missing config file")
    os.system('clear')
    request = requests.get(config['checker']['url'])
    status_code = int(request.status_code)
    invalid_status_code = int(config['checker']['invalid_status_code'])
    print("Performing get request...")
    sleep(0.5)
    print("Got status {}".format(status_code))
    sleep(0.5)
    
    if status_code == invalid_status_code:
        # Run a callback
        if 'callback' in config['checker']:
        	print("Found callback parameter. Trying to run it.")
        	subprocess.call(config['checker']['callback'], shell=True)
        	sleep(0.5)
        print("Restarting all supervisorctl tasks")
        command = 'supervisorctl restart all'
        if 'venv' in config['checker']:
        	command = 'source {};'.format(config['checker']['venv']) + command
        subprocess.call([command], shell=True)
        sleep(0.5)
        request = requests.get(config['checker']['url'])
        status_code = request.status_code
        # if it's again 502 - send an email
        if status_code == invalid_status_code:
            print("Again got invalid status code. Trying to send an email")
            sleep(0.5)
            server = smtplib.SMTP(config['email']['url'], config['email']['port'])
            server.starttls()
            server.login(config['email']['login'], config['email']['password'])

            msg = config['checker']['msg']
            server.sendmail(config['email']['login'], config['checker']['report_email'], msg)
            server.quit()

if __name__ == '__main__':
    main()