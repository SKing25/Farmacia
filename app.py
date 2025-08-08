from datetime import datetime
from flask import Flask, request, render_template
from abc import ABC, abstractmethod

from db import (
    crear_tabla_antibioticos,
    insertar_antibiotico,
    obtener_todos_antibioticos,
    buscar_antibioticos_por_nombre
)

"""
E-commerce farmacéutico con catálogo de medicamentos, validación de recetas, control de stock, 
alertas de vencimiento e interacciones medicamentosas.
"""

app = Flask(__name__)

crear_tabla_antibioticos()

# Para implementar mas adelante ;)
class Prescribible(ABC):
    @abstractmethod
    def requiere_receta(self) -> bool:
        pass

    @abstractmethod
    def validar_receta(self, receta: str) -> bool:
        pass


class Controlado(ABC):
    @abstractmethod
    def get_nivel_control(self) -> int:
        pass

    @abstractmethod
    def registrar_venta(self, cantidad: int) -> bool:
        pass


class Refrigerable(ABC):
    @abstractmethod
    def get_temperatura_almacenamiento(self) -> float:
        pass

    @abstractmethod
    def verificar_cadena_frio(self) -> bool:
        pass


class Generico(ABC):
    @abstractmethod
    def get_bioequivalencia(self) -> str:
        pass
    # VOy a hacer drogaaaaaa
    @abstractmethod
    def get_principio_activo(self) -> str:
        pass

#Clase abstract para medicamento
class Medicamento(ABC):
    def __init__(self, codigo, nombre_comercial, nombre_generico, laboratorio, vencimiento, lote, presentacion, precio, stock):
        self.codigo = codigo
        self.nombre_comercial = nombre_comercial
        self.nombre_generico = nombre_generico
        self.laboratorio = laboratorio
        self.vencimiento = vencimiento
        self.lote = lote
        self.presentacion = presentacion
        self.precio = precio
        self.stock = stock

    @abstractmethod
    def actualizar_stock(self, cantidad: int) -> bool:
        pass

    @abstractmethod
    def verificar_vencimiento(self) -> bool:
        pass

    @abstractmethod
    def get_info_completa(self) -> dict:
        pass

# probemos primero con los antibioticos
class Antibiotico(Medicamento, Prescribible):
    def __init__(self, codigo, nombre_comercial, nombre_generico, laboratorio, vencimiento, lote, presentacion, precio, stock, via_administracion):
        super().__init__(codigo, nombre_comercial, nombre_generico, laboratorio, vencimiento, lote, presentacion, precio, stock)
        self.via_administracion = via_administracion

    def requiere_receta(self) -> bool:
        return True

    def validar_receta(self, receta: str) -> bool:
        return len(receta) > 0

    def actualizar_stock(self, cantidad: int) -> bool:
        nuevo_stock = self.stock + cantidad
        if nuevo_stock >= 0:
            self.stock = nuevo_stock
            return True
        return False

    def verificar_vencimiento(self) -> bool:
        return datetime.now() < self.vencimiento

    def get_info_completa(self) -> dict:
        return {
            'tipo': 'Antibiótico',
            'codigo': self.codigo,
            'nombre_comercial': self.nombre_comercial,
            'via_administracion': self.via_administracion
        }

#cambiar mas adelante
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/antibiotico')
def listar_antibioticos():
    antibioticos = obtener_todos_antibioticos()
    return render_template('listar_antibioticos.html', antibioticos=antibioticos)

@app.route('/antibiotico/nuevo', methods=['GET', 'POST'])
def nuevo_antibiotico():
    if request.method == 'POST':
        try:
            datos = {
                'codigo': request.form['codigo'],
                'nombre_comercial': request.form['nombre_comercial'],
                'nombre_generico': request.form['nombre_generico'],
                'laboratorio': request.form['laboratorio'],
                'vencimiento': request.form['vencimiento'],  # Formato: 'YYYY-MM-DD'
                'lote': request.form['lote'],
                'presentacion': request.form['presentacion'],
                'precio': float(request.form['precio']),
                'stock': int(request.form['stock']),
                'via_administracion': request.form['via_administracion']
            }
            insertar_antibiotico(datos)
            return "Antibiótico guardado exitosamente"
        except Exception as e:
            return f"Error al guardar: {str(e)}", 400

    return render_template('nuevo_antibiotico.html')

# Tampoco lo he usado pero ahi esta
@app.route('/antibioticos/buscar')
def buscar_antibioticos():
    nombre = request.args.get('nombre', '')
    antibioticos = buscar_antibioticos_por_nombre(nombre)
    return render_template('listar_antibioticos.html', antibioticos=antibioticos)

if __name__ == '__main__':
    app.run()
