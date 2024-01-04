import socket
import sqlite3
import subprocess

server_socket = socket.socket()

server_socket.bind(('0.0.0.0', 4040))

server_socket.listen(5)

while True:
    conn, address = server_socket.accept()

    try:

        conn.send("User: ".encode())

        username = conn.recv(1024).decode("UTF-8").strip()

        conn.send("Password: ".encode())

        password = conn.recv(1024).decode("UTF-8").strip()

        db_conn = sqlite3.connect('database.db')
        cursor = db_conn.cursor()

        cursor.execute(f"SELECT * FROM User WHERE username = '{username}' AND password = '{password}'")

        if cursor.fetchall() != list():
            conn.send("Entraste!\n".encode())

            conn.send("Ingresa una IP para hacer ping: ".encode())

            ip_address = conn.recv(1024).decode("UTF-8").strip()

            resultado = subprocess.run(f"ping -c 1 {ip_address}", shell=True, capture_output=True, text=True)

            conn.send(resultado.stdout.encode())

        else:
            conn.send("No entraste\n".encode())
    except:
        pass
