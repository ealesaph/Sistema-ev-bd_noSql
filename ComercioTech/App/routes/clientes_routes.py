from flask import Blueprint, jsonify, request
#Blueprint = Modulo de rutas que utilizaremos en la APP principal
#Request = Permite acceder a los datos enviados por el cliente
#jsonify = Convierte diccionarios de Python a JSON para la respuesta HTTP
from app.config.database_config import db_sql
#la idea es que el objeto maneje la conexión al Postre, con esto hacemos consultas
from app.models.sql_models import Cliente,Direccion
from datetime import datetime

#Blueprints!
#Primero Creamos el BP clientes
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

#Luego le aplicamos su Getter a los clientes
@clientes_bp.route('/', methods=['GET'])
def obtener_clientes():
    try:
        clientes = Cliente.query.filter_by(activo=True).all
        #en SQL sería SELECT * FROM cliente WHERE activo = True;
        resultado = []
        for cliente in clientes:
            resultado.append({
                'id_cliente': cliente.id_cliente,
                'nombre': cliente.nombre,
                'apellido': cliente.apellid,
                'email': cliente.email,
                'telefono': cliente.telefono,
                'rut': cliente.rut,
                'fecha_registro': cliente.fecha_registro.strftime('%Y-%m-%d $H:%M:%S')
            })
        return jsonify({
            'exito': True,
            'clientes': resultado,
            'total': len(resultado)
        })
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener clientes: {str(e)}'
        })
        
#Obtener Cliente por ID
#GETTER
@clientes_bp.route('/<int:id_cliente>', methods=['GET'])
def obtener_cliente(id_cliente):
    #Realizar la consulta primero
    try:
        cliente = Cliente.query.get(id_cliente)
        #Verificamos si existe :D
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': f'Cliente con ID {id_cliente} no encontrado'
            }), 404
        # Obtener las direcciones del cliente
        direcciones = []
        for direccion in cliente.direcciones:
            direcciones.append({
                'id_direccion': direccion.id_direccion,
                'calle': direccion.calle,
                'numero': direccion.numero,
                'ciudad': direccion.ciudad,
                'region': direccion.region,
                'tipo': direccion.tipo
            })    
        return jsonify({
            'exito': True,
            'cliente': {
                'id_cliente': cliente.id_cliente,
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'email': cliente.email,
                'telefono': cliente.telefono,
                'rut': cliente.rut,
                'fecha_registro': cliente.fecha_registro.strftime('%Y-%m-%d %H:%M:%S'),
                'direcciones': direcciones
            }
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener cliente: {str(e)}'
        }), 500
        
#CREAR UN NUEVO CLIENTE
@clientes_bp.route('/', methods=['POST'])
def crear_cliente():