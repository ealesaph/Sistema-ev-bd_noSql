from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import token_requerido

auth_bp = Blueprint('auth', __name__)

# URL: /api/auth/register
@auth_bp.route('/register', methods=['POST'])
def registrar_usuario():
    try:
        datos = request.get_json()
        
        campos_requeridos = ['email', 'contraseña', 'nombre', 'apellido', 'id_rol']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({
                    'exito': False,
                    'mensaje': f'El campo {campo} es obligatorio'
                }), 400
        
        resultado = AuthService.registrar_usuario(
            email=datos['email'],
            contraseña=datos['contraseña'],
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            id_rol=datos['id_rol']
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
        
        if 'email' not in datos or 'contraseña' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere email y contraseña'
            }), 400
        
        resultado = AuthService.login_usuario(
            email=datos['email'],
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
                'email': usuario.email,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'rol': usuario.rol.nombre,
                'activo': usuario.activo
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener información: {str(e)}'
        }), 500