from flask import Flask, request, jsonify, abort
import base64
import pickle
import jwt
from hashlib import pbkdf2_hmac
from functools import wraps
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_secreto'  # Cambia esto a una clave secreta segura en producción

DB_FILE = 'database.db'

@app.route('/restart')
def restart():
	import os
	os.system("rm database.db")
	os.system("cp original_database.db database.db")
	return jsonify({"Status": "Restart"})

@app.route('/', methods=['GET'])
def index():
    help_data = {
        'message': 'Bienvenido a la API de la aplicación.',
        'endpoints': [
            {'endpoint': '/api/register', 'method': 'POST', 'description': 'Registrar un nuevo usuario'},
            {'endpoint': '/api/login', 'method': 'POST', 'description': 'Iniciar sesión'},
            {'endpoint': '/api/list_users', 'method': 'GET', 'description': 'Obtener la lista de usuarios'},
            {'endpoint': '/api/products/<name>', 'method': 'POST', 'description': 'Agregar un nuevo producto'},
            {'endpoint': '/api/products', 'method': 'GET', 'description': 'Obtener la lista de todos los productos'}
            # Agrega más endpoints según sea necesario
        ]
    }
    return jsonify(help_data)

def create_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except Error as e:
        print(e)
    return None

def execute_query(query, params=()):
    conn = create_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid
        except Error as e:
            print(e)
        finally:
            conn.close()
    return None

def fetch_query(query, params=()):
    conn = create_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            return rows
        except Error as e:
            print(e)
        finally:
            conn.close()
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401)

        try:
            token = auth_header.split()[1]
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token['user_id']
            is_admin = decoded_token['is_admin']
            user = fetch_query("SELECT * FROM users WHERE id=? AND is_admin=?", (user_id, is_admin))
            if not user:
                abort(401)
        except Exception as e:
            print(e)
            abort(401)

        return f(*args, **kwargs)

    return decorated_function

def generate_token(user_id, is_admin):
    token_data = {'user_id': user_id, 'is_admin': is_admin}
    return jwt.encode(token_data, app.config['SECRET_KEY'], algorithm='HS256')

def get_user_data_from_token(request):
    auth_header = request.headers.get('Authorization')
    token = auth_header.split()[1]
    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    return decoded_token['user_id'], decoded_token['is_admin']


@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin')

    hashed_password = pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000).hex()

    if is_admin == None:
        is_admin = "0"
    user_id = execute_query("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, hashed_password, is_admin))

    token = generate_token(user_id, is_admin)

    return jsonify({'message': 'User registered successfully', 'token': token}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = fetch_query("SELECT * FROM users WHERE username=?", (username,))

    if user and pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000).hex() == user[0][2]:
        token = generate_token(user[0][0], str(user[0][3]))
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/list_users', methods=['GET'])
def list_users():
    users_data = [{'id': user[0], 'username': user[1], 'is_admin': user[3]} for user in fetch_query("SELECT * FROM users")]
    return jsonify(users_data)

@app.route('/api/products/<name>', methods=['POST'])
def products(name):
    if request.method == 'POST':
        data = request.json

        user_id, is_admin = get_user_data_from_token(request)
        print("Es admin: ",is_admin)
        if is_admin != '1':
            abort(403)  # 403 Forbidden

        if data['proveedor'] and data['stock'] and name:
            # Convertir a pickle y luego a base64
            pickled_product = pickle.dumps({'name': name, 'data': data})
            base64_pickled_product = base64.b64encode(pickled_product).decode('utf-8')

            # Redirigir a /api/products/upload/<base64_pickled_product>
            return jsonify({'redirect': f'/api/products/upload/{base64_pickled_product}'}), 302
        return jsonify({"Error": "Falta proveedor y stock o el name"})

def deserialize_product(pickle_base64):

    pickled_data = base64.urlsafe_b64decode(pickle_base64)
    deserialized_data = pickle.loads(pickled_data)
    return deserialized_data


def get_all_products():
    products = fetch_query("SELECT * FROM products")
    print(products)
    result = []
    for product in products:
        pickle_base64 = product[1]

        deserialized_data = deserialize_product(pickle_base64)

        result.append(deserialized_data)

    return result

@app.route('/api/products', methods=['GET'])
def get_all_products_route():
    all_products = get_all_products()
    return jsonify(all_products)

@app.route('/api/products/upload/<base64_pickled_product>', methods=['GET'])
def upload_product(base64_pickled_product):
    try:
        #pickled_product = base64.b64decode(base64_pickled_product)
        #product_data = pickle.loads(pickled_product)

        user_id, is_admin = get_user_data_from_token(request)
        if is_admin != '1':
            abort(403)  # 403 Forbidden
        # Aquí realizar el INSERT con los datos recuperados de product_data
        execute_query("INSERT INTO products (pickle_base64_object) VALUES (?)", (base64_pickled_product,))


        return jsonify({'message': 'Product uploaded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)