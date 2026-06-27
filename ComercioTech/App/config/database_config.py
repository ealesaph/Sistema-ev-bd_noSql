from flask_sqlalchemy import SQLAlchemy  # Trabajar con SQL
from flask_pymongo import PyMongo        # Para el Mongo

db_sql = SQLAlchemy()
db_mongo = PyMongo()


def init_db(app):
    # --- PostgreSQL ---
    # Flask, Postgres y Mongo corren dentro del MISMO contenedor Debian,
    # por eso se usa 'localhost'. Si alguno viviera en otro contenedor,
    # aquí iría el nombre de ese contenedor en vez de localhost.
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'postgresql://leo:1234@localhost:5432/comerciotech'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- MongoDB ---
    # Si ya activaste 'security.authorization: enabled' en mongod.conf
    # (ver Guía de Instalación del DBMS), usa esta línea con usuario/clave:
    app.config['MONGO_URI'] = (
        'mongodb://app_comerciotech:OtraClaveSegura456!@localhost:27017/comerciotech'
        '?authSource=comerciotech'
    )
    # Si TODAVÍA NO activaste autenticación en Mongo, comenta la línea de
    # arriba y descomenta esta:
    # app.config['MONGO_URI'] = 'mongodb://localhost:27017/comerciotech'

    db_sql.init_app(app)
    db_mongo.init_app(app)
