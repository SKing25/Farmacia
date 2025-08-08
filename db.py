import sqlite3

DB_NAME = 'farmacia.db'

def conectar():
    return sqlite3.connect(DB_NAME)

def crear_tabla_antibioticos():
    con = conectar()
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS antibiotico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre_comercial TEXT NOT NULL,
            nombre_generico TEXT NOT NULL,
            laboratorio TEXT NOT NULL,
            vencimiento TEXT NOT NULL,
            lote TEXT NOT NULL,
            presentacion TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            via_administracion TEXT NOT NULL
        )
    ''')
    con.commit()
    con.close()

def insertar_antibiotico(data: dict):
    con = conectar()
    cur = con.cursor()
    cur.execute('''
        INSERT INTO antibiotico (
            codigo, nombre_comercial, nombre_generico, laboratorio,
            vencimiento, lote, presentacion, precio, stock, via_administracion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['codigo'],
        data['nombre_comercial'],
        data['nombre_generico'],
        data['laboratorio'],
        data['vencimiento'],
        data['lote'],
        data['presentacion'],
        data['precio'],
        data['stock'],
        data['via_administracion']
    ))
    con.commit()
    con.close()

def obtener_todos_antibioticos():
    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM antibiotico')
    antibioticos = cur.fetchall()
    con.close()
    return antibioticos

def buscar_antibioticos_por_nombre(nombre):
    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM antibiotico WHERE nombre_comercial LIKE ?', (f'%{nombre}%',))
    resultados = cur.fetchall()
    con.close()
    return resultados
