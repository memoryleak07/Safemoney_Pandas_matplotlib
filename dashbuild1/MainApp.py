from genericpath import exists
from DashApp import DashApp
from SafemoneyAPI import SafemoneyAPI
import configparser
import os
import ipaddress
from datetime import datetime as dt


def readConfigFile():
    def validateIPAddress():
        while True:
            try:
                ip = ipaddress.ip_address(input('\n[>] Enter Safemoney IP address: '))
                return ip
            except ValueError:
                print("[*] Enter a valid IP address!")
                continue
    def validatePIN():
        while True:
            pin = input('\n[>] Enter Safemoney PIN: ')
            if pin.strip().isdigit():
                return pin 
            print("[*] Enter a valid numeric PIN!")
            
    config = configparser.ConfigParser()
    if not os.path.isfile("configfile.ini"):
        ip = validateIPAddress()
        pin = validatePIN()
        config.add_section('safemoney')
        config.set('safemoney', 'ip', str(ip))
        config.set('safemoney', 'port', '7409')
        config.set('safemoney', 'pin', str(pin))
        config.add_section('server')
        config.set('server', 'ip', '127.0.0.1')
        config.set('server', 'port', '8050')
        with open("configfile.ini", 'w') as configfile:
            config.write(configfile)
    config.read('configfile.ini')
    ip = config['safemoney']['ip']
    pin = config['safemoney']['pin']
    return(ip, pin)


if __name__ == '__main__':
    # safemoney = SafemoneyAPI()
    ip, pin = readConfigFile()
    start_date = dt.today()
    end_date = dt.today()
    rundashapp = DashApp(ip, pin, start_date, end_date)
    rundashapp.app.run_server(debug=True)

