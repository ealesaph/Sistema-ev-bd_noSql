from flask import Blueprint, request, jsonify
from app.config.database_config import db_mongo
from bson import ObjectId
from datetime import datetime
import re

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/', methods=['GET'])
#URL: /api/productos
def obtener_productos():
    try:
        categoria = request.args.get('categoria')
        busqueda = request.args.get('busqueda')
        limit = int(request.args.get('limit', 20))
        
        filtro = {}
        
        if categoria:
            filtro['categoria'] = categoria
        
        if busqueda:
            filtro['$or'] = [
                {'nombre': {'$regex': busqueda, '$options': 'i'}},
                {'descripcion': {'$regex': busqueda, '$options': 'i'}}
            ]
        
        productos_collection = db_mongo.db.productos
        
        productos = productos_collection.find(filtro).limit(limit)
        
        resultado = []
        for producto in productos:
            producto['_id'] = str(producto['_id'])
            resultado.append(producto)
        
        return jsonify({
            'exito': True,
            'productos': resultado,
            'total': len(resultado)
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener productos: {str(e)}'
        }), 500

@productos_bp.route('/', methods=['POST'])
#URL: /api/productos
def crear_producto():
    try:
        datos = request.get_json()
        
        if 'nombre' not in datos or 'precio_base' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Los campos "nombre" y "precio_base" son obligatorios'
            }), 400
            
        nuevo_producto = {
            'nombre': datos['nombre'],
            'descripcion': datos.get('descripcion', ''),
            'precio_base': float(datos['precio_base']),
            'categoria': datos.get('categoria', 'general'),
            'atributos_variables': datos.get('atributos_variables', {}),
            'proveedor_id': datos.get('proveedor_id'),
            'fecha_creacion': datetime.utcnow(),
            'fecha_actualizacion': datetime.utcnow(),
            'stock_actual': datos.get('stock_actual', 0),
            'valoraciones': datos.get('valoraciones', [])
        }
        
        productos_collection = db_mongo.db.productos
        resultado = productos_collection.insert_one(nuevo_producto)
        
        return jsonify({
            'exito': True,
            'mensaje': 'Producto creado exitosamente',
            'id_producto': str(resultado.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al crear producto: {str(e)}'
        }), 500
        
@productos_bp.route('/buscar', methods=['GET'])
#URL EJMPLO: /api/productos/buscar?color=rojo&tamaño=M
#URL BÚSQUEDA GENERAL: /api/productos/buscar?q=Laptop&pagina=1&limite=10
def buscar_productos_por_atributo():
    try:
        q = request.args.get('q')
        pagina = int(request.args.get('pagina', 1))
        limite = int(request.args.get('limite', 10))
        
        filtro = {}
        
        # Búsqueda por texto (si se proporciona 'q')
        if q:
            filtro['$or'] = [
                {'nombre': {'$regex': q, '$options': 'i'}},
                {'descripcion': {'$regex': q, '$options': 'i'}}
            ]
        
        # Filtros adicionales por atributos (excluyendo parámetros de paginación y búsqueda general)
        parametros = request.args.to_dict()
        for clave, valor in parametros.items():
            if clave not in ['q', 'pagina', 'limite']:
                filtro[f'atributos_variables.{clave}'] = valor
                
        productos_collection = db_mongo.db.productos
        
        # Calcular paginación
        saltear = (pagina - 1) * limite
        productos = productos_collection.find(filtro).skip(saltear).limit(limite)
        total = productos_collection.count_documents(filtro)
        
        resultado = []
        for producto in productos:
            producto['_id'] = str(producto['_id'])
            resultado.append(producto)
        
        return jsonify({
            'exito': True,
            'productos': resultado,
            'resultados': resultado,  # Para compatibilidad con lo que espera el frontend (searchbar.jsx)
            'total': total,
            'filtros_aplicados': {k: v for k, v in parametros.items() if k not in ['pagina', 'limite']}
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error en búsqueda: {str(e)}'
        }), 500