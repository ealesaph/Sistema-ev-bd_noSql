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
#URL: /api/clientes/<id>
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
#URL: /api/clientes
def crear_cliente():
    try:
        datos = request.get_json()
        campos_requeridos = ['nombre', 'email', 'rut']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    'exito': False,
                    'mensaje': f'El campo {campo} es obligatorio'
                }), 400 #error 400 = Peticion Incorrecta
                
        nuevo_cliente = Cliente(
            nombre = datos['nombre'],
            email = ['email'],
            telefono = datos.get('telefono'),
            rut = datos['rut'],
            fecha_registro = datetime.utcnow()
        )
        
        db_sql.session.add(nuevo_cliente)
        
        if 'direcciones' in datos and datos['direcciones']:
            for dir_data in datos['direcciones']:
                nueva_direccion = Direccion(
                    id_cliente = nuevo_cliente.id_cliente,
                    calle=dir_data['calle'],
                    ciudad=dir_data['ciudad'],
                    comuna=dir_data['comuna'],
                    region=dir_data.get('region'),
                    codigo_postal=dir_data.get('codigo_postal'),
                    tipo=dir_data['tipo']
                )
                db_sql.session.add(nueva_direccion)
        
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Cliente creado exitosamente',
            'id_cliente': nuevo_cliente.id_cliente
        }), 201  # 201 = Creado exitosamente
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al crear cliente: {str(e)}'
        }), 500 # 500 = Error del servidor
        
@clientes_bp.route('/<int:id_cliente>', methods=['PUT'])
#URL: /api/clientes/<id>
def actualizar_cliente(id_cliente):
    try:
        cliente = Cliente.query.get(id_cliente)
        
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': f'Cliente con ID {id_cliente} no encontrado'
            }), 404
            
        datos = request.get_json()
        
        if 'nombre' in datos:
            cliente.nombre = datos['nombre']
        if 'email' in datos:
            cliente.email = datos['email']
        if 'telefono' in datos:
            cliente.telefono = datos['telefono']
        if 'rut' in datos:
            cliente.rut = datos['rut']
        
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Cliente actualizado exitosamente'
        }), 200
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al actualizar cliente: {str(e)}'
        }), 500 # 500 = Error del servidor

@clientes_bp.route('/<int:id_cliente>', methods=['DELETE'])
#URL: /api/clientes/<id>
def eliminar_cliente(id_cliente):
    try:
        cliente = Cliente.query.get(id_cliente)
        
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': f'Cliente con ID {id_cliente} no encontrado'
            }), 404
            
            db_sql.session.delete(cliente)
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Cliente eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al eliminar cliente: {str(e)}'
        }), 500 # 500 = Error del servidor