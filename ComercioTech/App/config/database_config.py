from flask_sqlalchemy import SQLAlchemy #Trabajar con SQL
from flask_pymongo import PyMongo #Para el Mongo

db_sql = SQLAlchemy() 
db_mongo = PyMongo() 

def init_db(app):
    #Config postreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://leo:1234@127.0.0.1:5432/comerciotech'
    )
    #El 5432 es el puerto estandar de Postre
    
    # Evitar que guarde un historial innecesario
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    #Configuramos el Mongo
    app.config['MONGO_URI'] = (
        'mongodb://127.0.0.1:27017/comerciotech'
    )
    #Segun la documentación de PyMongo
    #algo así como: mongodb://Servidor:puerto/NombreBD
    
    db_sql.init_app(app)
    db_mongo.init_app(app)