#Librerias
from flask import Flask
from flask_cors import CORS # Permite peticiones al backend sin problemas de CORS
from .config.database_config import init_db

def crear_app():
    app = Flask(__name__)
    CORS(app) 
    
    app.config['llave_secreta'] = 'Definir-la-clave-secreta-aqui' #Clave para poder firmar Tokens o Cookies :)
    
    init_db(app) #Conectamos el Postgre y el Mongo
    from .routes.clientes_routes import clientes_bp
    from .routes.pedidos_routes import pedidos_bp
    from .routes.productos_routes import productos_bp
    
    app.register_blueprint(clientes_bp, url_prefix='/api/clientes') #Asignamos URL a clientes
    app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos') #Asignamos URL a pedidos
    app.register_blueprint(productos_bp, url_prefix='/api/productos') #Asignamos URL a productos
    
    return app