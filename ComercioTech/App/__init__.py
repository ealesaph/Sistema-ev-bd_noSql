#Librerias
import os
from flask import Flask
from flask_cors import CORS
from .config.database_config import init_db

def create_app():
    # Ruta a la carpeta dist compilada por Vite
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Frontend', 'static', 'dist')
    
    app = Flask(__name__, static_folder=frontend_dist, static_url_path='/')
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
    from .routes.logs_routes import logs_bp
    
    app.register_blueprint(clientes_bp, url_prefix='/api/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/api/pedidos')
    app.register_blueprint(productos_bp, url_prefix='/api/productos')
    app.register_blueprint(carrito_bp, url_prefix='/api/carrito')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    
    # Ruta para servir el frontend de React
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path.startswith('api/'):
            return "Not Found", 404
        
        # Si el archivo existe en la carpeta dist (ej. assets, imagenes), sírvelo
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)
        # En caso contrario, retorna el index.html para que React Router se encargue
        else:
            return app.send_static_file('index.html')
            
    return app