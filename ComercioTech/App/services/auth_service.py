import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from app.config.database_config import db_sql
from app.models.sql_models import Usuario, Rol

class AuthService:
    
    @staticmethod
    def hash_password(contraseña_plana):
        """
        Encripta una contraseña usando bcrypt
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contraseña_plana.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verificar_password(contraseña_plana, hash_almacenado):

        return bcrypt.checkpw(contraseña_plana.encode('utf-8'), hash_almacenado.encode('utf-8'))
    
    @staticmethod
    def generar_token(usuario_id, rol_id):

        payload = {
            'usuario_id': usuario_id,
            'rol_id': rol_id,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expira en 24 horas
            'iat': datetime.utcnow()
        }
        secret = current_app.config.get('SECRET_KEY', 'clave_secreta_por_defecto')
        return jwt.encode(payload, secret, algorithm='HS256')
    
    @staticmethod
    def verificar_token(token):

        try:
            secret = current_app.config.get('SECRET_KEY', 'clave_secreta_por_defecto')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return {'exito': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'exito': False, 'mensaje': 'El token ha expirado'}
        except jwt.InvalidTokenError:
            return {'exito': False, 'mensaje': 'Token inválido'}
    
    @staticmethod
    def registrar_usuario(nombre_usuario, contraseña, id_rol, id_cliente=None):

        try:
            # Verificar si el nombre de usuario ya existe
            usuario_existente = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            if usuario_existente:
                return {'exito': False, 'mensaje': 'El nombre de usuario ya está en uso'}
            
            # Verificar que el rol existe
            rol = Rol.query.get(id_rol)
            if not rol:
                return {'exito': False, 'mensaje': 'El rol especificado no existe'}
            
            # Crear el nuevo usuario
            nuevo_usuario = Usuario(
                nombre_usuario=nombre_usuario,
                hash_password=AuthService.hash_password(contraseña),
                id_rol=id_rol,
                id_cliente=id_cliente,
                estado='activo'
            )
            
            db_sql.session.add(nuevo_usuario)
            db_sql.session.commit()
            
            return {
                'exito': True,
                'mensaje': 'Usuario registrado exitosamente',
                'usuario_id': nuevo_usuario.id_usuario
            }
            
        except Exception as e:
            db_sql.session.rollback()
            return {'exito': False, 'mensaje': f'Error al registrar usuario: {str(e)}'}
    
    @staticmethod
    def login_usuario(nombre_usuario, contraseña):

        try:
            # Buscar el usuario
            usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
            if not usuario:
                return {'exito': False, 'mensaje': 'Usuario o contraseña incorrectos'}
            
            # Verificar la contraseña
            if not AuthService.verificar_password(contraseña, usuario.hash_password):
                return {'exito': False, 'mensaje': 'Usuario o contraseña incorrectos'}
            
            # Verificar que el usuario esté activo
            if usuario.estado != 'activo':
                return {'exito': False, 'mensaje': f'La cuenta está {usuario.estado}'}
            
            # Generar token
            token = AuthService.generar_token(usuario.id_usuario, usuario.id_rol)
            
            # Obtener información del rol
            rol = usuario.rol
            
            return {
                'exito': True,
                'mensaje': 'Login exitoso',
                'token': token,
                'usuario': {
                    'id_usuario': usuario.id_usuario,
                    'nombre_usuario': usuario.nombre_usuario,
                    'rol': rol.nombre_rol,
                    'nivel_permiso': rol.nivel_permiso,
                    'id_cliente': usuario.id_cliente
                }
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': f'Error en login: {str(e)}'}