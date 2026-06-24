from app.config.database_config import db_sql
from sqlalchemy import CheckConstraint
# La idea es permitir definir tablas y hacer consultas
from datetime import datetime
#Este es para poner la fecha de registro automáticamente

#Modulo Clientes
#Revisar Forma normal Apellido -> A.Paterno, A.Materno
class Cliente(db_sql.Model):
    #Heredar el modelo de db_sql.Model
    #Este comando es parte del FLASK-SQLAlchemy
    __tablename__ = 'cliente' 
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
    __tablename__ = 'direccion'
    #Columnas
    id_direccion = db_sql.Column(db_sql.Integer, primary_key = True)
    calle = db_sql.Column(db_sql.String(200), nullable = False)
    numero = db_sql.Column(db_sql.String(20))
    ciudad = db_sql.Column(db_sql.String(100), nullable = False)
    region = db_sql.Column(db_sql.String(100))
    pais = db_sql.Column(db_sql.String(100), server_default = 'Chile', nullable = False)
    codigo_postal = db_sql.Column(db_sql.String(20))
    tipo = db_sql.Column(db_sql.String(20), default = 'ENVIO')
    #Relaciones
    #No hay relaciones :))
    #Constraints
    #Acá ponemos las restricciones (Checks, etc..)
    __table_args__ = (
        CheckConstraint("tipo IN ('ENVIO', 'FACTURACION', 'PRINCIPAL')", name='check_estado_valido'),
        )

#Modulo Proveedores
class Proveedor(db_sql.Model):
    #Nombre Tabla
    __tablename__ = 'proveedor'
    #Columnas
    id_proveedor = db_sql.Column(db_sql.Integer, primary_key = True)
    nombre = db_sql.Column(db_sql.String(150), nullable = False)
    rut = db_sql.Column(db_sql.String(20), unique=True)
    email = db_sql.Column(db_sql.String(150))
    telefono = db_sql.Column(db_sql.String(150))
    activo = db_sql.Column(db_sql.Bool, default = True, nullable=False)
    fecha_registro = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
    
    
    #Relaciones
    direccion = db_sql.relationship('Direccion', backref='proveedor', lazy=True)
    
    #Constraints
    #No hay
    
class PagoProveedor(db_sql.Model):
    #Nombre Tabla
    __tablename__ = 'PagoProveedor'
    #Columnas
    id_pago = db_sql.Column(db_sql.Integer, primary_key=True)
    monto = db_sql.Column(db_sql.Numeric(precision=12, scale=2), nullable = False)
    metodo_pago = db_sql.Column(db_sql.String(50), nullable=False)
    estado = db_sql.Column(db_sql.String(20), default ='PENDIENTE', nullable=False)
    referencia = db_sql.Column(db_sql.String(100))
    fecha_pago = db_sql.Coumn(db_sql.Date)
    fecha_creacion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
    #Relaciones
    proveedor = db_sql.relationship('Proveedor', backref='PagoProveedor', lazy=True)
    #Constraints
    __table_args__ = (
        CheckConstraint("monto > 10", name='chequear_precio_positivo'),
        CheckConstraint("estado IN ('PENDIENTE', 'PAGADO', 'ANULADO')",name='check_estado_proveedor'),
    )
    
#Modulo Inventario
class Producto(db_sql.Model):
#Nombre Tabla
    __tablename__= 'Producto'
#Columnas
    id_producto = db_sql.Column(db_sql.Integer, primary_key=True)
    
#Relaciones
    provee
#Constraints

#Modulo Pedidos y Facturacion

#Modulo Seguridad
class Usuario(db_sql.Model):
    __tablename__ = 'usuario'
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

