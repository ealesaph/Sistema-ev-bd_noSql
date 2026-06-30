import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import current_app
from app.config.database_config import db_sql
from app.models.sql_models import Usuario, Rol, Cliente, Direccion

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
        """
        Verifica si una contraseña coincide con su hash
        """
        return bcrypt.checkpw(contraseña_plana.encode('utf-8'), hash_almacenado.encode('utf-8'))
    
    @staticmethod
    def generar_token(usuario_id, rol_id):
        """
        Genera un JWT para un usuario autenticado
        """
        payload = {
            'usuario_id': usuario_id,
            'rol_id': rol_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        secret = current_app.config.get('SECRET_KEY', 'clave_secreta_por_defecto')
        return jwt.encode(payload, secret, algorithm='HS256')
    
    @staticmethod
    def verificar_token(token):
        """
        Verifica y decodifica un JWT
        """
        try:
            secret = current_app.config.get('SECRET_KEY', 'clave_secreta_por_defecto')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return {'exito': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'exito': False, 'mensaje': 'El token ha expirado'}
        except jwt.InvalidTokenError:
            return {'exito': False, 'mensaje': 'Token inválido'}
    
    @staticmethod
    def registrar_usuario(email, contraseña, nombre, apellido, id_rol):
        """
        Registra un nuevo usuario en el sistema
        Usa los campos reales del modelo Usuario:
        - email (único, usado para login)
        - nombre
        - apellido
        - contrasena_hash
        - activo (default True)
        """
        try:
            # Verificar si el email ya existe
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                return {'exito': False, 'mensaje': 'El email ya está registrado'}
            
            # Verificar que el rol existe
            rol = Rol.query.get(id_rol)
            if not rol:
                return {'exito': False, 'mensaje': 'El rol especificado no existe'}
            
            # Crear el nuevo usuario
            nuevo_usuario = Usuario(
                email=email,
                contrasena_hash=AuthService.hash_password(contraseña),
                nombre=nombre,
                apellido=apellido,
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
    def registrar_cliente_usuario(email, contraseña, nombre, apellido, rut, telefono=None, direccion_info=None):
        """
        Registra un usuario y un cliente de forma atómica.
        Crea también su dirección de envío si se proporciona.
        """
        try:
            # Verificar si el email ya existe en Usuario
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                return {'exito': False, 'mensaje': 'El email ya está registrado'}
                
            # Verificar si el email o rut ya existe en Cliente
            cliente_existente = Cliente.query.filter((Cliente.email == email) | (Cliente.rut == rut)).first()
            if cliente_existente:
                return {'exito': False, 'mensaje': 'El email o RUT ya está registrado como cliente'}
                
            # Buscar el rol de cliente (nombre = 'cliente')
            rol = Rol.query.filter_by(nombre='cliente').first()
            id_rol = rol.id_rol if rol else 2  # 2 es el ID por defecto si se insertaron secuencialmente
            
            # Crear Usuario
            nuevo_usuario = Usuario(
                email=email,
                contrasena_hash=AuthService.hash_password(contraseña),
                nombre=nombre,
                apellido=apellido,
                id_rol=id_rol,
                activo=True
            )
            db_sql.session.add(nuevo_usuario)
            
            # Crear Cliente
            nuevo_cliente = Cliente(
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                rut=rut,
                activo=True,
                fecha_registro=datetime.utcnow()
            )
            db_sql.session.add(nuevo_cliente)
            db_sql.session.flush()  # Para que nuevo_cliente obtenga su id_cliente autogenerado
            
            # Crear Dirección si está presente
            if direccion_info:
                nueva_direccion = Direccion(
                    id_cliente=nuevo_cliente.id_cliente,
                    calle=direccion_info.get('calle'),
                    numero=direccion_info.get('numero', ''),
                    comuna=direccion_info.get('comuna'),
                    ciudad=direccion_info.get('ciudad'),
                    region=direccion_info.get('region', ''),
                    pais=direccion_info.get('pais', 'Chile'),
                    codigo_postal=direccion_info.get('codigo_postal', ''),
                    tipo='ENVIO'
                )
                db_sql.session.add(nueva_direccion)
                
            db_sql.session.commit()
            
            return {
                'exito': True,
                'mensaje': 'Registro completado exitosamente',
                'usuario_id': nuevo_usuario.id_usuario,
                'cliente_id': nuevo_cliente.id_cliente
            }
            
        except Exception as e:
            db_sql.session.rollback()
            return {'exito': False, 'mensaje': f'Error al registrar cliente: {str(e)}'}
    
    @staticmethod
    def login_usuario(email, contraseña):
        """
        Autentica a un usuario por email y genera un token JWT
        """
        try:
            # Buscar el usuario por email
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario:
                return {'exito': False, 'mensaje': 'Email o contraseña incorrectos'}
            
            # Verificar la contraseña
            if not AuthService.verificar_password(contraseña, usuario.contrasena_hash):
                return {'exito': False, 'mensaje': 'Email o contraseña incorrectos'}
            
            # Verificar que el usuario esté activo
            if not usuario.activo:
                return {'exito': False, 'mensaje': 'La cuenta está desactivada'}
            
            # Generar token
            token = AuthService.generar_token(usuario.id_usuario, usuario.id_rol)
            
            # Obtener información del rol
            rol = usuario.rol
            
            # Obtener el cliente asociado por email
            cliente = Cliente.query.filter_by(email=usuario.email).first()
            id_cliente = cliente.id_cliente if cliente else None
            
            return {
                'exito': True,
                'mensaje': 'Login exitoso',
                'token': token,
                'usuario': {
                    'id_usuario': usuario.id_usuario,
                    'id_cliente': id_cliente,
                    'email': usuario.email,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'rol': rol.nombre,
                    'activo': usuario.activo
                }
            }
            
        except Exception as e:
            return {'exito': False, 'mensaje': f'Error en login: {str(e)}'}