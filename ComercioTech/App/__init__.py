#Librerias
from flask import Flask
from flask_cors import CORS
from .config.database_config import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuración de la aplicación
    app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'  # ¡Cámbiar por una clave segura!
    
    # Inicializar conexiones a bases de datos
    init_db(app)
    
    # Registrar rutas existentes
    from .routes.clientes_routes import clientes_bp
    from .routes.pedidos_routes import pedidos_bp
    from .routes.productos_routes import productos_bp
    from .routes.carrito_routes import carrito_bp
    
    # Registrar nuevas rutas de autenticación
    from .routes.auth_routes import auth_bp
    
    app.register_blueprint(clientes_bp, url_prefix='/api/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(carrito_bp, url_prefix='/api/carrito')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app