from functools import wraps
from flask import request, jsonify
from App.services.auth_service import AuthService

def token_requerido(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener el token del header Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'exito': False,
                'mensaje': 'Token de autenticación requerido'
            }), 401
        
        # El formato debe ser "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'exito': False,
                'mensaje': 'Formato de token inválido. Use: Bearer <token>'
            }), 401
        
        token = parts[1]
        
        # Verificar el token
        resultado = AuthService.verificar_token(token)
        if not resultado['exito']:
            return jsonify({
                'exito': False,
                'mensaje': resultado['mensaje']
            }), 401
        
        # Agregar el payload del token a la solicitud para usarlo en la ruta
        request.usuario_payload = resultado['payload']
        
        return f(*args, **kwargs)
    
    return decorated_function

def rol_requerido(roles_permitidos):
    """
    NOTA: el modelo Rol real (sql_models.py) no tiene columna 'nivel_permiso',
    así que el control de acceso se hace por nombre de rol.
    Uso: @rol_requerido(['admin', 'vendedor'])
    """
    if isinstance(roles_permitidos, str):
        roles_permitidos = [roles_permitidos]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Primero verificar que el token es válido
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return jsonify({
                    'exito': False,
                    'mensaje': 'Token de autenticación requerido'
                }), 401

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({
                    'exito': False,
                    'mensaje': 'Formato de token inválido'
                }), 401

            token = parts[1]
            resultado = AuthService.verificar_token(token)

            if not resultado['exito']:
                return jsonify({
                    'exito': False,
                    'mensaje': resultado['mensaje']
                }), 401

            payload = resultado['payload']

            from App.models.sql_models import Rol

            rol = Rol.query.get(payload['rol_id'])
            if not rol:
                return jsonify({
                    'exito': False,
                    'mensaje': 'Rol no encontrado'
                }), 403

            if rol.nombre not in roles_permitidos:
                return jsonify({
                    'exito': False,
                    'mensaje': f'Permisos insuficientes. Se requiere uno de estos roles: {roles_permitidos}'
                }), 403

            request.usuario_payload = payload

            return f(*args, **kwargs)

        return decorated_function
    return decorator