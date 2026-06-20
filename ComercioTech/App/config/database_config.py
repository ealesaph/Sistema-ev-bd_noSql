from flask_sqlalchemy import SQLAlchemy #Trabajar con SQL
from flask_pymongo import PyMongo #Para el Mongo

db_sql = SQLAlchemy() 
db_mongo = PyMongo() 

def init_db(app):
    #Config postreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost:5432/nombre_base_de_datos'
    #El 5432 es el puerto estandar de Postre
    
    # Evitar que guarde un historial innecesario
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    #Configuramos el Mongo
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/nombre_base_de_datos_mongo'
    #Segun la documentación debería ser algo así como: mongodb://Servidor:puerto/NombreBD
    
    db_sql.init_app(app)
    db_mongo.init_app(app)
    