from App.config.database_config import db_sql
from sqlalchemy import CheckConstraint
# La idea es permitir definir tablas y hacer consultas
from datetime import datetime
#Este es para poner la fecha de registro automáticamente

#Modulo Clientes
#Revisar Forma normal Apellido -> A.Paterno, A.Materno
class Cliente(db_sql.Model):
    #Heredar el modelo de db_sql.Model
    #Este comando es parte del FLASK-SQLAlchemy
    __tablename__ = 'clientes' 
    #Esto es para que SQLAlchemy sepa como se llama la tabla en el Postre
    
    #Luego inserto las tablas :)
    #Cliente
    id_cliente = db_sql.Column(db_sql.Integer, primary_key = True)
    nombre = db_sql.Column(db_sql.String(100), nullable=False)
    apellido = db_sql.Column(db_sql.String(100), nullable=False, unique=True)
    #El nullable es para que sea Obligatorio
    email = db_sql.Column(db_sql.String(150), nullable=False, unique=True)
    telefono = db_sql.Column(db_sql.String(20))
    rut = db_sql.Column(db_sql.String(12), nullable=False, unique=True)
    activo = db_sql.Column(db_sql.Bool, default = True, nullable = False)
    fecha_registro = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
    
    # RELACIONES sin crear tablas, solo crean relaciones lógicas
    
    direcciones = db_sql.relationship('Direccion', backref='cliente', lazy=True)
    pedidos = db_sql.relationship('Pedido', backref='cliente', lazy=True)
    #backref crea un atributo cliente en la clase Direccion
    # lazy=True Carga perezosa (Solo carga las direcciones cuando las necesites)

    def __repr__(self):
        # Este metodo sirve para definir como se forma un String de un objeto, como lo "representa"
        # Nos sirve para depuracion
        return f'<Cliente {self.nombre}>'

#Revisar Forma normal en BD
#Direccion_id no me hace sentido
class Direccion(db_sql.Model):
    #Nombre Tabla
    __tablename__ = 'direcciones'
    #Columnas
    id_direccion = db_sql.Column(db_sql.Integer, primary_key = True)
    calle = db_sql.Column(db_sql.String(200), nullable = False)
    numero = db_sql.Column(db_sql.String(20))
    ciudad = db_sql.Column(db_sql.String(100), nullable = False)
    region = db_sql.Column(db_sql.String(100))
    pais = db_sql.Column(db_sql.String(100), default = 'Chile', nullable = False)
    codigo_postal = db_sql.Column(db_sql.String(20))
    tipo = db_sql.Column(db_sql.String(20), default = 'Envio')
    #Relaciones
    #No hay relaciones :))
    #Constraints
    #Acá ponemos las restricciones (Checks, etc..)
    __table_args__ = (
        CheckConstraint("tipo IN ('ENVIO', 'FACTURACION', 'PRINCIPAL')", name='check_estado_valido'),
        )

#Modulo Seguridad
class Usuario(db_sql.Model):
    __tablename__ = 'usuarios'
    #Tablas
    id_usuario = db_sql.Column(db_sql.Integer, primary_key = True)
    nombre = db_sql.Column(db_sql.String(100), nullable = False)
    apellido = db_sql.Column(db_sql.String(100), nullable = False)
    email = db_sql.Column(db_sql.String(150), nullable = False, unique=True)
    contrasena_hash = db_sql.Column(db_sql.String(255), nullable = False)
    activo = db_sql.Column(db_sql.Bool, default = True, nullable = False)
    fecha_creacion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable = False)
    ultimo_login = db_sql.Column(db_sql.DateTime)
    
    #Relaciones
    rol = db_sql.relationship('Rol', backref='usuarios', lazy=True)

