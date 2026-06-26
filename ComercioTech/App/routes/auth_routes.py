from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import token_requerido, rol_requerido

auth_bp = Blueprint('auth', __name__)

# URL: /api/auth/register
@auth_bp.route('/register', methods=['POST'])
def registrar_usuario():

    try:
        datos = request.get_json()
        
        campos_requeridos = ['nombre_usuario', 'contraseña', 'id_rol']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    'exito': False,
                    'mensaje': f'El campo {campo} es obligatorio'
                }), 400
        
        resultado = AuthService.registrar_usuario(
            nombre_usuario=datos['nombre_usuario'],
            contraseña=datos['contraseña'],
            id_rol=datos['id_rol'],
            id_cliente=datos.get('id_cliente')
        )
        
        if resultado['exito']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al registrar usuario: {str(e)}'
        }), 500

# URL: /api/auth/login
@auth_bp.route('/login', methods=['POST'])
def login_usuario():

    try:
        datos = request.get_json()
        
        if 'nombre_usuario' not in datos or 'contraseña' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere nombre_usuario y contraseña'
            }), 400
        
        resultado = AuthService.login_usuario(
            nombre_usuario=datos['nombre_usuario'],
            contraseña=datos['contraseña']
        )
        
        if resultado['exito']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 401
            
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error en login: {str(e)}'
        }), 500

# URL: /api/auth/verify
@auth_bp.route('/verify', methods=['GET'])
@token_requerido
def verificar_token():

    payload = request.usuario_payload
    return jsonify({
        'exito': True,
        'mensaje': 'Token válido',
        'usuario_id': payload['usuario_id'],
        'rol_id': payload['rol_id']
    }), 200

# URL: /api/auth/me
@auth_bp.route('/me', methods=['GET'])
@token_requerido
def obtener_info_usuario():

    try:
        from app.config.database_config import db_sql
        from app.models.sql_models import Usuario
        
        payload = request.usuario_payload
        usuario = Usuario.query.get(payload['usuario_id'])
        
        if not usuario:
            return jsonify({
                'exito': False,
                'mensaje': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'exito': True,
            'usuario': {
                'id_usuario': usuario.id_usuario,
                'nombre_usuario': usuario.nombre_usuario,
                'rol': usuario.rol.nombre_rol,
                'nivel_permiso': usuario.rol.nivel_permiso,
                'estado': usuario.estado,
                'id_cliente': usuario.id_cliente
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener información: {str(e)}'
        }), 500