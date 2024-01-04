from flask import Flask, request, redirect, render_template, make_response, send_from_directory, jsonify, render_template_string
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

nombres = {
    "admin": "Ricardo Gomez",
    "bob": "Bob Martinez",
    "alice": "Alicia Lopez"
}

KEY = "DSPWPCv3_examen"

perfil_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editar Perfil</title>
</head>
<body>
    <h1>Editar Perfil</h1>
    {{ username }}
    <form method="POST" action="{{ url_for('edit_perfil') }}">
        <label for="nombre">Nuevo Nombre:</label>
        <input type="text" id="nombre" name="nombre" required>

        <button type="submit">Guardar</button>
    </form>
</body>
</html>
"""

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
    global comentarios
    global nombres
    comentarios = list()
    nombres = {
        "admin": "Ricardo Gomez",
        "bob": "Bob Martinez",
        "alice": "Alicia Lopez"
    }
    return "Limpieza", 200

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

            encode_jwt = jwt.encode(payload = payload_data, key = KEY, algorithm="HS256")

            #ans = make_response(render_template('comentarios.html', comentarios = comentarios))
            ans = redirect('/comments', 302)
            ans.set_cookie("JWT_token", encode_jwt)

            return ans
    return render_template('login.html')

def check_jwt(token):

    #token = request.cookies.get('JWT_token')

    try:
        decode = jwt.decode(token, key = KEY, algorithms=['HS256', ]) # Realizaremos la verificacion del token

        return decode

    except:
        return False

@app.route('/administrative')
def administrative():
    token = request.cookies.get('JWT_token')
    if check_jwt(token) != False:
        decode = jwt.decode(token, key = KEY, algorithms=['HS256', ])
        if decode['user'] == "admin":
            return render_template('administrative.html')
    return redirect('/login', 302)

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/cr3d3nt14ls')
def cr3d3nt14ls():
    return "Las credenciales de alice son: jycbstygWTYW8262vn82636"

@app.route('/edit_perfil', methods=['GET', 'POST'])
def edit_perfil():
    token = request.cookies.get('JWT_token')
    if check_jwt(token) != False:
        decode = jwt.decode(token, key = KEY, algorithms=['HS256', ])
        if decode['user'] == "admin":
            if request.method == 'GET':
                #return render_template_string(perfil_template, username=nombres[decode['user']])
                return render_template_string("""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Editar Perfil</title>
                    </head>
                    <body>
                        <h1>Editar Perfil</h1>
                        """ + nombres[decode['user']]  + """
                        <form method="POST" action="{{ url_for('edit_perfil') }}">
                            <label for="nombre">Nuevo Nombre:</label>
                            <input type="text" id="nombre" name="nombre" required>

                            <button type="submit">Guardar</button>
                        </form>
                    </body>
                    </html>
                    """)
            elif request.method == 'POST':
                new_nombre = request.form.get('nombre')
                if new_nombre:
                    nombres[decode['user']] = new_nombre
                    return jsonify({'message': f'Nombre de {decode["user"]} actualizado correctamente', 'nuevo_nombre': new_nombre})
                else:
                    return jsonify({'error': 'Se requiere el parámetro "nombre"'})
    return "No tienes privilegios para editar el perfil"