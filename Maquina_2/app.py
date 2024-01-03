from flask import Flask, render_template, request
import sqlite3
import subprocess

app = Flask(__name__)

# Configuración de la base de datos
DATABASE = 'database.db'

def ejecutar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True, text=True)
        return resultado.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Filtrar por ID
        filtro_id = request.form.get('filtro_id')
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = f'SELECT * FROM comandos WHERE id = {filtro_id}'
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()

        # Agregar resultados de ejecución
        resultados_ejecucion = []
        for resultado in resultados:
            ejecucion = ejecutar_comando(resultado[1])
            resultados_ejecucion.append((resultado[0], resultado[1], ejecucion))
        
        return render_template('index.html', resultados=resultados_ejecucion, filtro_id=filtro_id)

    # Mostrar todos los elementos de la tabla
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM comandos')
    resultados = cursor.fetchall()
    conn.close()

    # Agregar resultados de ejecución
    resultados_ejecucion = [(resultado[0], resultado[1], ejecutar_comando(resultado[1])) for resultado in resultados]

    return render_template('index.html', resultados=resultados_ejecucion, filtro_id=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)