from flask import Flask, request, redirect, render_template, make_response
import jwt
from datetime import datetime
import time
import json
import os

app = Flask(__name__)

comentarios = list()

users = {
    "admin": "bsbGSVbhsgh7365sbnTSvgsbhd",
    "bob": "euiwidnxv2625e9d7c9=2623", # este estara en el FTP
    "alice": "jycbstygWTYW8262vn82636"
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/comments')
def comments():

    if check_jwt(request.cookies.get('JWT_token')) != False:
        return render_template('comentarios.html', comentarios = comentarios)
    return redirect('/login', 302)
    
@app.route('/sendit', methods = ['POST'])
def sendit():
    global comentarios
    comentarios.append((request.form['autor'], request.form['contenido']))
    #return "subido!", 200
    return redirect('/comments', 302)

@app.route('/delete')
def delete():
    if check_jwt(request.cookies.get('JWT_token')) != False:
        global comentarios
        comentarios = list()
        return "Comentarios eliminados!", 200
    return redirect('/login', 302)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
      
        if users[user] == password:

            now = int(time.time())
            expires = now + 3600

            payload_data = {
                'user': user,
                'iat': now,
                'exp': expires
            }

            encode_jwt = jwt.encode(payload = payload_data, key = "DSPWPCv2_lab_1", algorithm="HS256")

            #ans = make_response(render_template('comentarios.html', comentarios = comentarios))
            ans = redirect('/comments', 302)
            ans.set_cookie("JWT_token", encode_jwt)

            return ans
    return render_template('login.html')

def check_jwt(token):

    #token = request.cookies.get('JWT_token')

    try:
        decode = jwt.decode(token, key = "DSPWPCv2_lab_1", algorithms=['HS256', ]) # Realizaremos la verificacion del token

        return decode

    except:
        return False

@app.route('/administrative')
def administrative():
    token = request.cookies.get('JWT_token')
    if check_jwt(token) != False:
        decode = jwt.decode(token, key = "DSPWPCv2_lab_1", algorithms=['HS256', ])
        if decode['user'] == "admin":
            return render_template('administrative.html')
    return redirect('/login', 302)

@app.route('/ping', methods=['POST', 'GET'])
def ping():
    token = request.cookies.get('JWT_token')
    if check_jwt(token) != False:
        decode = jwt.decode(token, key = "DSPWPCv2_lab_1", algorithms=['HS256', ])
        if decode['user'] == "admin":
            ip = request.form['ip']
            return "<pre>{}</pre>".format(os.popen("ping -c 1 {}".format(ip)).read())
    return redirect('/login', 302)

app.run()