from datetime import datetime,timedelta
from flask import Flask, request, render_template
from abc import ABC, abstractmethod

from db import (
    crear_tabla_antibioticos,
    insertar_antibiotico,
    obtener_todos_antibioticos,
    buscar_antibioticos_por_nombre
)

app = Flask(__name__)

# crear la tabla de antibióticos si no existe
crear_tabla_antibioticos()

# interfaces principales
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

    @abstractmethod
    def get_principio_activo(self) -> str:
        pass


# la clase abstracta
class Medicamento(ABC):
    def __init__(self, codigo, nombre_comercial, nombre_generico, laboratorio, vencimiento, lote, presentacion, precio, stock):
        self.codigo = codigo
        self.nombre_comercial = nombre_comercial
        self.nombre_generico = nombre_generico
        self.laboratorio = laboratorio
        self.vencimiento = datetime.strptime(vencimiento, "%Y-%m-%d") if isinstance(vencimiento, str) else vencimiento
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


# Implementemos el antibiotico
class Antibiotico(Medicamento, Prescribible):
    def __init__(self, codigo, nombre_comercial, nombre_generico, laboratorio, vencimiento, lote, presentacion, precio, stock, via_administracion):
        super().__init__(codigo, nombre_comercial, nombre_generico, laboratorio, vencimiento, lote, presentacion, precio, stock)
        self.via_administracion = via_administracion

    def requiere_receta(self) -> bool:
        return True

    def validar_receta(self, receta: str) -> bool:
        return bool(receta and receta.strip())

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
            'nombre_generico': self.nombre_generico,
            'laboratorio': self.laboratorio,
            'vencimiento': self.vencimiento.strftime("%Y-%m-%d"),
            'lote': self.lote,
            'presentacion': self.presentacion,
            'precio': self.precio,
            'stock': self.stock,
            'via_administracion': self.via_administracion
        }


#intento de polimorfismo pa mostrar el inventario
def mostrar_inventario(medicamentos: list[Medicamento]):
    inventario = []
    for m in medicamentos:
        inventario.append(m.get_info_completa())
    return inventario

@app.route('/')
def index():
    registros = obtener_todos_antibioticos()
    antibioticos = [
        Antibiotico(
            r['codigo'], r['nombre_comercial'], r['nombre_generico'], r['laboratorio'],
            r['vencimiento'], r['lote'], r['presentacion'], r['precio'], r['stock'], r['via_administracion']
        ) for r in registros
    ]

    alerta_stock = [a for a in antibioticos if a.stock < 5]

    limite_vencimiento = datetime.now() + timedelta(days=30)
    alerta_vencimiento = [a for a in antibioticos if a.vencimiento < limite_vencimiento and a.verificar_vencimiento()]
    return render_template("index.html",
                           alertas_stock=alerta_stock,
                           alertas_vencimiento=alerta_vencimiento
                           )


@app.route('/antibiotico')
def listar_antibioticos():
    registros = obtener_todos_antibioticos()
    antibioticos = [
        Antibiotico(
            r['codigo'], r['nombre_comercial'], r['nombre_generico'], r['laboratorio'],
            r['vencimiento'], r['lote'], r['presentacion'], r['precio'], r['stock'], r['via_administracion']
        ) for r in registros
    ]
    return render_template('listar_antibioticos.html', antibioticos=mostrar_inventario(antibioticos))

@app.route('/antibiotico/nuevo', methods=['GET', 'POST'])
def nuevo_antibiotico():
    if request.method == 'POST':
        try:
            datos = {
                'codigo': request.form['codigo'],
                'nombre_comercial': request.form['nombre_comercial'],
                'nombre_generico': request.form['nombre_generico'],
                'laboratorio': request.form['laboratorio'],
                'vencimiento': request.form['vencimiento'],
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

@app.route('/antibioticos/buscar')
def buscar_antibioticos():
    nombre = request.args.get('nombre', '')
    registros = buscar_antibioticos_por_nombre(nombre)
    antibioticos = [
        Antibiotico(
            r['codigo'], r['nombre_comercial'], r['nombre_generico'], r['laboratorio'],
            r['vencimiento'], r['lote'], r['presentacion'], r['precio'], r['stock'], r['via_administracion']
        ) for r in registros
    ]
    return render_template('listar_antibioticos.html', antibioticos=mostrar_inventario(antibioticos))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') #el perro host pa q sirva en render
