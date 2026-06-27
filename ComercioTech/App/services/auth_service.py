import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from App.config.database_config import db_sql
from App.models.sql_models import Usuario, Rol


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
    def registrar_usuario(nombre, apellido, email, contraseña, id_rol):
        """
        NOTA: el modelo Usuario real (sql_models.py) usa nombre/apellido/email/
        contrasena_hash/activo. No existen columnas nombre_usuario, hash_password,
        id_cliente ni estado, por eso esta versión usa los nombres reales.
        El email funciona como identificador único de login.
        """
        try:
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                return {'exito': False, 'mensaje': 'El email ya está registrado'}

            rol = Rol.query.get(id_rol)
            if not rol:
                return {'exito': False, 'mensaje': 'El rol especificado no existe'}

            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                contrasena_hash=AuthService.hash_password(contraseña),
                id_rol=id_rol,
                activo=True
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
    def login_usuario(email, contraseña):
        try:
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario:
                return {'exito': False, 'mensaje': 'Usuario o contraseña incorrectos'}

            if not AuthService.verificar_password(contraseña, usuario.contrasena_hash):
                return {'exito': False, 'mensaje': 'Usuario o contraseña incorrectos'}

            if not usuario.activo:
                return {'exito': False, 'mensaje': 'La cuenta está inactiva'}

            usuario.ultimo_login = datetime.utcnow()
            db_sql.session.commit()

            token = AuthService.generar_token(usuario.id_usuario, usuario.id_rol)
            rol = usuario.rol

            return {
                'exito': True,
                'mensaje': 'Login exitoso',
                'token': token,
                'usuario': {
                    'id_usuario': usuario.id_usuario,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'email': usuario.email,
                    'rol': rol.nombre
                }
            }

        except Exception as e:
            return {'exito': False, 'mensaje': f'Error en login: {str(e)}'}
