from app.config.database_config import db_sql
# La idea es permitir definir tablas y hacer consultas
from datetime import datetime
#Este es para poner la fecha de registro automáticamente

# Modelo Cliente
class Cliente(db_sql.Model):
    #Heredar el modelo de db_sql.Model
    #Este comando es parte del FLASK-SQLAlchemy
    __tablename__ = 'clientes' 
    #Esto es para que SQLAlchemy sepa como se llama la tabla en el Postre
    
    #Luego inserto las tablas :)
    #Cliente
    id_cliente = db_sql.Column(db_sql.Integer, primary_key = True)
    
    nombre = db_sql.Column(db_sql.String(100), nullable=False)
    #El nullable es para que sea Obligatorio
    
    email = db_sql.Column(db_sql.String(150), nullable=False, unique=True)
    
    telefono = db_sql.Column(db_sql.String(20))
    
    rut = db_sql.Column(db_sql.String(12), nullable=False, unique=True)
    
    fecha_registro = db_sql.Column(db_sql.DateTime, default=datetime.utcnow)
    
    # RELACIONES sin crear tablas, solo crean relaciones lógicas
    
    direcciones = db_sql.relationship('Direccion', backref='cliente', lazy=True)
    #backref crea un atributo cliente en la clase Direccion
    # lazy=True Carga perezosa (Solo carga las direcciones cuando las necesites)
    