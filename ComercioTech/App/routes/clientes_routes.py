from flask import Blueprint, jsonify, request
#Blueprint = Modulo de rutas que utilizaremos en la APP principal
#Request = Permite acceder a los datos enviados por el cliente
#jsonify = Convierte diccionarios de Python a JSON para la respuesta HTTP
from app.config.database_config import db_sql
#la idea es que el objeto maneje la conexión al Postre, con esto hacemos consultas
from app.models.sql_models import Cliente, Direccion, SolicitudEliminacion, Auditoria, Usuario, Pedido
from datetime import datetime
import secrets
from app.middleware.auth_middleware import token_requerido, rol_requerido


clientes_bp = Blueprint('clientes', __name__)

#Luego le aplicamos su Getter a los clientes
@clientes_bp.route('/', methods=['GET'])
def obtener_clientes():
    try:
        clientes = Cliente.query.filter_by(activo=True).all()
        #en SQL sería SELECT * FROM cliente WHERE activo = True;
        resultado = []
        for cliente in clientes:
            resultado.append({
                'id_cliente': cliente.id_cliente,
                'nombre': cliente.nombre,
                'email': cliente.email,
                'telefono': cliente.telefono,
                'rut': cliente.rut,
                'fecha_registro': cliente.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
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
                'comuna': direccion.comuna,
                'codigo_postal': direccion.codigo_postal,
                'ciudad': direccion.ciudad,
                'region': direccion.region,
                'tipo': direccion.tipo
            })    
        return jsonify({
            'exito': True,
            'cliente': {
                'id_cliente': cliente.id_cliente,
                'nombre': cliente.nombre,
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
        campos_requeridos = ['nombre', 'apellido', 'email', 'rut']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    'exito': False,
                    'mensaje': f'El campo {campo} es obligatorio'
                }), 400 #error 400 = Peticion Incorrecta
                
        nuevo_cliente = Cliente(
            nombre = datos['nombre'],
            apellido = datos['apellido'],
            email = datos['email'],
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
@token_requerido
@rol_requerido(['Administrador'])
#URL: /api/clientes/<id>
def eliminar_cliente(id_cliente):
    try:
        cliente = Cliente.query.get(id_cliente)
        
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': f'Cliente con ID {id_cliente} no encontrado'
            }), 404
            
        # Verificar integridad referencial: si posee pedidos históricos
        pedidos_count = Pedido.query.filter_by(id_cliente=id_cliente).count()
        if pedidos_count > 0:
            return jsonify({
                'exito': False,
                'mensaje': 'No es posible eliminar físicamente al cliente porque posee pedidos históricos en ComercioTech. Utilice la Anonimización (Derecho al Olvido) para borrar sus datos sensibles.'
            }), 400
            
        usuario = Usuario.query.filter_by(email=cliente.email).first()
        if usuario:
            db_sql.session.delete(usuario)
            
        db_sql.session.delete(cliente)
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Cliente y usuario asociado eliminados exitosamente'
        }), 200
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al eliminar cliente: {str(e)}'
        }), 500 # 500 = Error del servidor
        
# URL: /api/clientes/<int:id_cliente>/solicitar-eliminacion
@clientes_bp.route('/<int:id_cliente>/solicitar-eliminacion', methods=['POST'])
def solicitar_eliminacion(id_cliente):
    """
    Paso 1: Cliente solicita eliminación de datos personales
    """
    try:
        cliente = Cliente.query.get(id_cliente)
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': 'Cliente no encontrado'
            }), 404
        
        # Verificar si ya hay una solicitud pendiente
        solicitud_existente = SolicitudEliminacion.query.filter_by(
            id_cliente=id_cliente,
            estado='pendiente'
        ).first()
        
        if solicitud_existente:
            return jsonify({
                'exito': False,
                'mensaje': 'Ya existe una solicitud pendiente para este cliente'
            }), 400
        
        # Crear la solicitud
        token_verificacion = secrets.token_urlsafe(32)
        nueva_solicitud = SolicitudEliminacion(
            id_cliente=id_cliente,
            estado='pendiente',
            token_verificacion=token_verificacion
        )
        
        db_sql.session.add(nueva_solicitud)
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Solicitud de eliminación creada exitosamente',
            'token': token_verificacion,  # En producción se envía por email
            'id_solicitud': nueva_solicitud.id_solicitud
        }), 201
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al crear solicitud: {str(e)}'
        }), 500

# URL: /api/clientes/<int:id_cliente>/aprobar-eliminacion/<int:id_solicitud>
@clientes_bp.route('/<int:id_cliente>/aprobar-eliminacion/<int:id_solicitud>', methods=['POST'])
@token_requerido
@rol_requerido(['Administrador'])
def aprobar_eliminacion(id_cliente, id_solicitud):

    try:
        # Obtener la solicitud
        solicitud = SolicitudEliminacion.query.get(id_solicitud)
        
        if not solicitud:
            return jsonify({
                'exito': False,
                'mensaje': 'Solicitud no encontrada'
            }), 404
        
        if solicitud.id_cliente != id_cliente:
            return jsonify({
                'exito': False,
                'mensaje': 'La solicitud no corresponde al cliente'
            }), 400
        
        if solicitud.estado != 'pendiente':
            return jsonify({
                'exito': False,
                'mensaje': f'La solicitud ya fue {solicitud.estado}'
            }), 400
        
        # Verificar token de verificación (en producción, esto se hace por email)
        datos = request.get_json()
        if not datos or datos.get('token') != solicitud.token_verificacion:
            return jsonify({
                'exito': False,
                'mensaje': 'Token de verificación inválido'
            }), 401
        
        # Paso 3: Anonimizar los datos del cliente
        cliente = Cliente.query.get(id_cliente)
        cliente.nombre = f'ELIMINADO_{cliente.id_cliente}'
        cliente.apellido = 'USUARIO_ELIMINADO'
        cliente.email = f'anon_{cliente.id_cliente}@eliminado.com'
        cliente.telefono = None
        cliente.rut = f'00.000.000-{cliente.id_cliente:02d}'  # RUT no válido
        cliente.activo = False
        
        # Actualizar la solicitud
        solicitud.estado = 'completada'
        solicitud.fecha_procesamiento = datetime.utcnow()
        
        # Registrar en auditoría
        from app.models.sql_models import Auditoria
        auditoria = Auditoria(
            id_usuario=request.usuario_payload['usuario_id'],
            tabla_afectada='cliente',
            registro_id=cliente.id_cliente,
            accion='DELETE',
            detalle={'motivo': 'Derecho al olvido', 'solicitud_id': id_solicitud}
        )
        db_sql.session.add(auditoria)
        
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Datos del cliente anonimizados exitosamente',
            'id_cliente': cliente.id_cliente
        }), 200
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al procesar eliminación: {str(e)}'
        }), 500

@clientes_bp.route('/admin-list', methods=['GET'])
@token_requerido
@rol_requerido(['Administrador'])
def listar_clientes_admin():
    try:
        clientes = Cliente.query.all()
        resultado = []
        for cliente in clientes:
            usuario = Usuario.query.filter_by(email=cliente.email).first()
            usuario_activo = usuario.activo if usuario else True
            usuario_id = usuario.id_usuario if usuario else None
            
            resultado.append({
                'id_cliente': cliente.id_cliente,
                'id_usuario': usuario_id,
                'nombre': f"{cliente.nombre} {cliente.apellido}" if hasattr(cliente, 'apellido') else cliente.nombre,
                'email': cliente.email,
                'telefono': cliente.telefono,
                'rut': cliente.rut,
                'activo_usuario': usuario_activo,
                'fecha_registro': cliente.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({
            'exito': True,
            'clientes': resultado,
            'total': len(resultado)
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener listado: {str(e)}'
        }), 500

@clientes_bp.route('/<int:id_cliente>/desactivar', methods=['POST'])
@token_requerido
@rol_requerido(['Administrador'])
def desactivar_usuario_cliente(id_cliente):
    try:
        cliente = Cliente.query.get(id_cliente)
        if not cliente:
            return jsonify({'exito': False, 'mensaje': 'Cliente no encontrado'}), 404
            
        usuario = Usuario.query.filter_by(email=cliente.email).first()
        if not usuario:
            return jsonify({'exito': False, 'mensaje': 'Usuario asociado no encontrado'}), 404
            
        # Bloquear/Desbloquear
        usuario.activo = not usuario.activo
        db_sql.session.commit()
        
        estado_str = "activado" if usuario.activo else "desactivado"
        return jsonify({
            'exito': True,
            'mensaje': f'Usuario {estado_str} exitosamente',
            'activo_usuario': usuario.activo
        }), 200
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({'exito': False, 'mensaje': f'Error al cambiar estado: {str(e)}'}), 500

@clientes_bp.route('/direcciones', methods=['POST'])
@token_requerido
def crear_direccion():
    try:
        payload = request.usuario_payload
        usuario_id = payload['usuario_id']
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'exito': False, 'mensaje': 'Usuario no encontrado'}), 404
            
        cliente = Cliente.query.filter_by(email=usuario.email).first()
        if not cliente:
            return jsonify({'exito': False, 'mensaje': 'Cliente no encontrado'}), 404
            
        datos = request.get_json()
        campos_requeridos = ['calle', 'comuna', 'ciudad', 'tipo']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({'exito': False, 'mensaje': f'El campo {campo} es obligatorio'}), 400
                
        nueva_direccion = Direccion(
            id_cliente=cliente.id_cliente,
            calle=datos['calle'],
            numero=datos.get('numero'),
            comuna=datos['comuna'],
            ciudad=datos['ciudad'],
            region=datos.get('region'),
            codigo_postal=datos.get('codigo_postal'),
            tipo=datos['tipo']
        )
        
        db_sql.session.add(nueva_direccion)
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Dirección creada exitosamente',
            'direccion': {
                'id_direccion': nueva_direccion.id_direccion,
                'calle': nueva_direccion.calle,
                'comuna': nueva_direccion.comuna,
                'ciudad': nueva_direccion.ciudad,
                'tipo': nueva_direccion.tipo
            }
        }), 201
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({'exito': False, 'mensaje': f'Error al guardar dirección: {str(e)}'}), 500

@clientes_bp.route('/direcciones/<int:id_direccion>', methods=['DELETE'])
@token_requerido
def eliminar_direccion(id_direccion):
    try:
        payload = request.usuario_payload
        usuario_id = payload['usuario_id']
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'exito': False, 'mensaje': 'Usuario no encontrado'}), 404
            
        cliente = Cliente.query.filter_by(email=usuario.email).first()
        if not cliente:
            return jsonify({'exito': False, 'mensaje': 'Cliente no encontrado'}), 404
            
        direccion = Direccion.query.filter_by(id_direccion=id_direccion, id_cliente=cliente.id_cliente).first()
        if not direccion:
            return jsonify({'exito': False, 'mensaje': 'Dirección no encontrada o no pertenece al usuario'}), 404
            
        db_sql.session.delete(direccion)
        db_sql.session.commit()
        
        return jsonify({'exito': True, 'mensaje': 'Dirección eliminada correctamente'}), 200
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({'exito': False, 'mensaje': f'Error al eliminar dirección: {str(e)}'}), 500