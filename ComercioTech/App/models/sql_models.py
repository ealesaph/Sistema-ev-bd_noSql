from app.config.database_config import db_sql
from sqlalchemy import CheckConstraint
# La idea es permitir definir tablas y hacer consultas
from datetime import datetime
#Este es para poner la fecha de registro automáticamente
#Modulo Seguridad
class Rol(db_sql.Model):
    __tablename__ = 'rol'
    #Tablas
    id_rol = db_sql.Column(db_sql.Integer, primary_key = True)
    nombre = db_sql.Column(db_sql.String(50), nullable = False, unique=True)
    descripcion = db_sql.Column(db_sql.String(200))
    activo = db_sql.Column(db_sql.Bool, default = True, nullable = False)
    fecha_creacion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable = False)   
    
class Usuario(db_sql.Model):
    __tablename__ = 'usuario'
    #Tablas
    id_usuario = db_sql.Column(db_sql.Integer, primary_key = True)
    id_rol = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('rol.id_rol'), nullable = False)
    nombre = db_sql.Column(db_sql.String(100), nullable = False)
    apellido = db_sql.Column(db_sql.String(100), nullable = False)
    email = db_sql.Column(db_sql.String(150), nullable = False, unique=True)
    contrasena_hash = db_sql.Column(db_sql.String(255), nullable = False)
    activo = db_sql.Column(db_sql.Bool, default = True, nullable = False)
    fecha_creacion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable = False)
    ultimo_login = db_sql.Column(db_sql.DateTime)
    
    #Relaciones
    rol = db_sql.relationship('Rol', backref='usuarios', lazy=True)
    
class Auditoria(db_sql.Model):
    __tablename__ = 'auditoria'
    #Tablas
    id_auditoria = db_sql.Column(db_sql.Integer, primary_key = True)
    id_usuario = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('usuario.id_usuario'), nullable = False)
    tabla_afectada = db_sql.Column(db_sql.String(100), nullable = False)
    operacion = db_sql.Column(db_sql.String(10), nullable = False)
    datos_anteriores = db_sql.Column(db_sql.JSONB)
    datos_nuevos = db_sql.Column(db_sql.JSONB)
    ip_origen = db_sql.Column(db_sql.INET)
    fecha_accion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable = False)
    
    #Relaciones
    usuario = db_sql.relationship('Usuario', backref='auditorias', lazy=True)
    
    #Constraints
    __table_args__ = (
        CheckConstraint("operacion IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT')", name='check_operacion_valida'),
    )
    
class LogAuditoriaSeguridad(db_sql.Model):
    __tablename__ = 'log_auditoria_seguridad'
    #Tablas
    id_log = db_sql.Column(db_sql.Integer, primary_key = True)
    id_usuario = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('usuario.id_usuario'),nullable = True)
    evento = db_sql.Column(db_sql.String(100), nullable = False)
    descripcion = db_sql.Column(db_sql.Text)
    ip_origen = db_sql.Column(db_sql.INET)
    exitoso = db_sql.Column(db_sql.Boolean, default = False, nullable = False)
    fecha_accion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable = False)
    
    #Relaciones
    Usuario = db_sql.relationship('Usuario', backref='logs_seguridad', lazy=True)

    
class SolicitudEliminacion(db_sql.Model):
    __tablename__ = 'solicitud_eliminacion'
    #Tablas
    id_solicitud = db_sql.Column(db_sql.Integer, primary_key = True)
    id_usuario = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('usuario.id_usuario'), nullable = False)
    tabla_usuario = db_sql.Column(db_sql.String(100), nullable = False)
    id_aprobador= db_sql.Column(db_sql.Integer, db_sql.ForeignKey('usuario.id_usuario'),nullable = True)
    motivo = db_sql.Column(db_sql.Text, nullable = False)
    estado = db_sql.Column(db_sql.String(20), default='PENDIENTE', nullable = False)
    fecha_solicitud = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable = False)
    fecha_resolucion = db_sql.Column(db_sql.DateTime)
    
    #Relaciones
    usuario_solicitante = db_sql.relationship('Usuario', backref='solicitudes_eliminacion', lazy=True)
    usuario_aprobador = db_sql.relationship('Usuario', backref='solicitudes_eliminacion_aprobadas', lazy=True)

    #Constraints
    __table_args__ = (
        CheckConstraint("estado IN ('PENDIENTE', 'APROBADA', 'RECHAZADA')", name='check_estado_solicitud'),
    )



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
    apellido = db_sql.Column(db_sql.String(100), nullable=False)
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
    id_cliente = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('cliente.id_cliente'), nullable = False)
    id_proveedor = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('proveedor.id_proveedor'), nullable = True)
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
    direccion = db_sql.relationship('Direccion', backref='proveedores', lazy=True)
    
    #Constraints
    #No hay
    
class PagoProveedor(db_sql.Model):
    #Nombre Tabla
    __tablename__ = 'pago_proveedor'
    #Columnas
    id_pago = db_sql.Column(db_sql.Integer, primary_key=True)
    id_proveedor = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('proveedor.id_proveedor'), nullable=False)
    monto = db_sql.Column(db_sql.Numeric(precision=12, scale=2), nullable = False)
    metodo_pago = db_sql.Column(db_sql.String(50), nullable=False)
    estado = db_sql.Column(db_sql.String(20), default ='PENDIENTE', nullable=False)
    referencia = db_sql.Column(db_sql.String(100))
    fecha_pago = db_sql.Column(db_sql.Date)
    fecha_creacion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
    #Relaciones
    proveedor = db_sql.relationship('Proveedor', backref='pago_proveedor', lazy=True)
    #Constraints
    __table_args__ = (
        CheckConstraint("monto > 0", name='chequear_precio_positivo'),
        CheckConstraint("estado IN ('PENDIENTE', 'PAGADO', 'ANULADO')",name='check_estado_proveedor'),
    )
    
#Modulo Inventario
class Producto(db_sql.Model):
#Nombre Tabla
    __tablename__= 'producto'
#Columnas
    id_producto = db_sql.Column(db_sql.Integer, primary_key=True)
    id_proveedor = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('proveedor.id_proveedor'), nullable=False)
    nombre = db_sql.Column(db_sql.String(150), nullable=False)
    descripcion = db_sql.Column(db_sql.Text)
    precio = db_sql.Column(db_sql.Numeric(precision=12, scale=2), nullable=False)
    stock = db_sql.Column(db_sql.Integer, default=0)
    activo = db_sql.Column(db_sql.Bool, default=True, nullable=False)
    fecha_creacion = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
#Relaciones
    proveedor = db_sql.relationship('Proveedor', backref='producto', lazy=True)
#Constraints
    __table_args__ = (
        CheckConstraint("precio >= 0", name='check_precio_positivo'),
        CheckConstraint("stock >= 0", name='check_stock_positivo'),
    )

#Modulo Pedidos y Facturacion
class Pedido(db_sql.Model):
#Nombre de la tabla
    __tablename__ = 'pedido'
#Columnas
    id_pedido = db_sql.Column(db_sql.Integer, primary_key=True)
    id_cliente = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('cliente.id_cliente'), nullable=False)
    id_usuario = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('usuario.id_usuario'), nullable=False)
    estado = db_sql.Column(db_sql.String(20), default='PENDIENTE', nullable=False)
    fecha_pedido = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega = db_sql.Column(db_sql.DateTime)
    total = db_sql.Column(db_sql.Numeric(precision=12, scale=2), default=0, nullable=False)
    observaciones = db_sql.Column(db_sql.Text)
#Relaciones
    cliente = db_sql.relationship('Cliente', backref='pedidos', lazy=True)
    usuario = db_sql.relationship('Usuario', backref='pedidos', lazy=True)  
#Constraints
    __table_args__ = (
        CheckConstraint("estado IN ('PENDIENTE', 'CONFIRMADO', 'ENTREGADO', 'CANCELADO')", name='check_estado_pedido'),
        CheckConstraint("total >= 0", name='check_total_positivo'),
    )

#------
class DetallePedido(db_sql.Model):
    __tablename__ = 'detalle_pedido'
    id_detalle = db_sql.Column(db_sql.Integer, primary_key=True)
    id_pedido = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('pedido.id_pedido'), nullable=False)
    id_producto = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('producto.id_producto'), nullable=False)
    cantidad = db_sql.Column(db_sql.Integer, nullable=False)
    precio_unitario = db_sql.Column(db_sql.Numeric(precision=10, scale=2), nullable=False)
    descuento = db_sql.Column(db_sql.Numeric(precision=5, scale=2),default=0)
    subtotal = db_sql.Column(
        db_sql.Numeric(12, 2),
        db_sql.Computed("cantidad * precio_unitario * (1 - descuento / 100)", persisted=True)
    )
    
    # Relaciones
    pedido = db_sql.relationship('Pedido', backref='detalles', lazy=True)
    producto = db_sql.relationship('Producto', backref='detalles', lazy=True)
    
    # Constraints
    __table_args__ = (
    CheckConstraint("cantidad > 0", name='check_cantidad_positiva'),
    CheckConstraint("precio_unitario >= 0", name='check_precio_unitario_positivo'),
    CheckConstraint("subtotal >= 0", name='check_subtotal_positivo'),
    )
    
class Factura(db_sql.Model):
    __tablename__ = 'factura'
    id_factura = db_sql.Column(db_sql.Integer, primary_key=True)
    id_pedido = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('pedido.id_pedido'), nullable=False)
    id_cliente = db_sql.Column(db_sql.Integer, db_sql.ForeignKey('cliente.id_cliente'), nullable=False)
    numero_factura = db_sql.Column(db_sql.String(50), unique=True, nullable=False)
    fecha_emision = db_sql.Column(db_sql.DateTime, default=datetime.utcnow, nullable=False)
    monto_neto = db_sql.Column(db_sql.Numeric(precision=12, scale=2), nullable=False)
    impuesto = db_sql.Column(db_sql.Numeric(precision=5, scale=2), default=19.00, nullable=False)
    monto_total = db_sql.Column(db_sql.Numeric(precision=12, scale=2), default=0, nullable=False)
    estado = db_sql.Column(db_sql.String(20), default='PENDIENTE', nullable=False)
    
    # Relaciones
    pedido = db_sql.relationship('Pedido', backref='facturas', lazy=True)
    cliente = db_sql.relationship('Cliente', backref='facturas', lazy=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("monto_total >= 0", name='check_monto_total_factura_positivo'),
        CheckConstraint("estado IN ('EMITIDA', 'PAGADA', 'ANULADA')", name='check_estado_factura')
    )