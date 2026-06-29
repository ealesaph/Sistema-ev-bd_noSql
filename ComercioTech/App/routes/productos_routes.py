from flask import Blueprint, request, jsonify
from app.config.database_config import db_mongo, db_sql
from bson import ObjectId
from datetime import datetime
import re

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/', methods=['GET'])
#URL: /api/productos
def obtener_productos():
    try:
        categoria = request.args.get('categoria')
        etiqueta = request.args.get('etiqueta')
        busqueda = request.args.get('busqueda')
        activo = request.args.get('activo')
        limit = int(request.args.get('limit', 20))
        
        filtro = {}
        
        if categoria:
            filtro['categoria'] = categoria
            
        if etiqueta:
            filtro['etiqueta'] = etiqueta
            
        if activo is not None:
            filtro['activo'] = activo.lower() in ['true', '1', 'yes']
        else:
            filtro['activo'] = True
        
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


@productos_bp.route('/<string:producto_id>', methods=['GET'])
def obtener_detalle_producto(producto_id):
    try:
        productos_collection = db_mongo.db.productos
        producto = productos_collection.find_one({'_id': ObjectId(producto_id)})
        
        if not producto:
            return jsonify({
                'exito': False,
                'mensaje': 'Producto no encontrado'
            }), 404
            
        producto['_id'] = str(producto['_id'])
        return jsonify({
            'exito': True,
            'producto': producto
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener detalles del producto: {str(e)}'
        }), 500


@productos_bp.route('/<string:producto_id>/recomendaciones', methods=['GET'])
def obtener_recomendaciones_producto(producto_id):
    try:
        productos_collection = db_mongo.db.productos
        producto = productos_collection.find_one({'_id': ObjectId(producto_id)})
        
        if not producto:
            return jsonify({
                'exito': False,
                'mensaje': 'Producto no encontrado'
            }), 404
            
        categoria = producto.get('categoria')
        cliente_id = request.args.get('cliente_id')
        if cliente_id:
            try:
                cliente_id = int(cliente_id)
            except ValueError:
                cliente_id = None
                
        # Buscar otros productos de la misma categoría que estén activos
        filtro = {
            'categoria': categoria,
            'activo': True,
            '_id': {'$ne': ObjectId(producto_id)}
        }
        
        adyacentes = list(productos_collection.find(filtro).limit(6))
        
        adyacentes_resultado = []
        adyacentes_ids = []
        for adj in adyacentes:
            adj['_id'] = str(adj['_id'])
            adyacentes_resultado.append(adj)
            adyacentes_ids.append(adj['_id'])
            
        # Auditoría de vista en logs_navegacion
        logs_collection = db_mongo.db.logs_navegacion
        log_documento = {
            'cliente_id': cliente_id,
            'ip_origen': request.remote_addr,
            'tipo_evento': 'vista_producto',
            'producto_id': producto_id,
            'fecha_hora': datetime.utcnow(),
            'productos_adyacentes': adyacentes_ids
        }
        logs_collection.insert_one(log_documento)
        
        return jsonify({
            'exito': True,
            'recomendaciones': adyacentes_resultado,
            'total': len(adyacentes_resultado)
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener recomendaciones: {str(e)}'
        }), 500


@productos_bp.route('/<string:producto_id>/resenas', methods=['GET'])
def listar_resenas(producto_id):
    try:
        resenas_collection = db_mongo.db.resenas
        resenas = list(resenas_collection.find({'producto_id': ObjectId(producto_id)}).sort('fecha', -1))
        
        resultado = []
        for r in resenas:
            r['_id'] = str(r['_id'])
            r['producto_id'] = str(r['producto_id'])
            if 'fecha' in r and isinstance(r['fecha'], datetime):
                r['fecha'] = r['fecha'].strftime('%Y-%m-%d %H:%M:%S')
            resultado.append(r)
            
        return jsonify({
            'exito': True,
            'resenas': resultado,
            'total': len(resultado)
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al listar reseñas: {str(e)}'
        }), 500


@productos_bp.route('/<string:producto_id>/resenas', methods=['POST'])
def crear_resena(producto_id):
    try:
        datos = request.get_json()
        
        if 'rating' not in datos or 'id_cliente' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere calificación (rating) e id_cliente'
            }), 400
            
        rating = int(datos['rating'])
        id_cliente = int(datos['id_cliente'])
        comentario = datos.get('comentario', '')
        titulo = datos.get('titulo', '')
        nombre_cliente = datos.get('nombre_cliente', 'Cliente Anónimo')
        
        if rating < 0 or rating > 5:
            return jsonify({
                'exito': False,
                'mensaje': 'La calificación debe estar entre 0 y 5 estrellas'
            }), 400
            
        productos_collection = db_mongo.db.productos
        producto = productos_collection.find_one({'_id': ObjectId(producto_id)})
        
        if not producto:
            return jsonify({
                'exito': False,
                'mensaje': 'Producto no encontrado'
            }), 404
            
        id_producto_sql = producto.get('id_producto_sql')
        if not id_producto_sql:
            return jsonify({
                'exito': False,
                'mensaje': 'Este producto no está mapeado en la base de datos PostgreSQL'
            }), 400
            
        # Verificación en PostgreSQL: el cliente debe haber comprado este producto
        from app.models.sql_models import Pedido, DetallePedido
        from app.config.database_config import db_sql
        
        compra_existente = db_sql.session.query(Pedido).join(DetallePedido).filter(
            Pedido.id_cliente == id_cliente,
            DetallePedido.id_producto == id_producto_sql
        ).first()
        
        if not compra_existente:
            return jsonify({
                'exito': False,
                'mensaje': 'Debes haber comprado este producto para poder dejar una reseña.'
            }), 403
            
        resenas_collection = db_mongo.db.resenas
        nueva_resena = {
            'producto_id': ObjectId(producto_id),
            'id_cliente': id_cliente,
            'nombre_cliente': nombre_cliente,
            'rating': rating,
            'titulo': titulo,
            'comentario': comentario,
            'fecha': datetime.utcnow()
        }
        
        resultado = resenas_collection.insert_one(nueva_resena)
        
        # Recalcular promedio de estrellas
        pipeline = [
            {'$match': {'producto_id': ObjectId(producto_id)}},
            {'$group': {'_id': None, 'promedio': {'$avg': '$rating'}, 'total': {'$sum': 1}}}
        ]
        stats = list(resenas_collection.aggregate(pipeline))
        
        rating_promedio = 0
        total_resenas = 0
        if stats:
            rating_promedio = round(stats[0]['promedio'], 1)
            total_resenas = stats[0]['total']
            
        productos_collection.update_one(
            {'_id': ObjectId(producto_id)},
            {'$set': {
                'rating_promedio': rating_promedio,
                'total_resenas': total_resenas
            }}
        )
        
        return jsonify({
            'exito': True,
            'mensaje': 'Reseña publicada exitosamente',
            'id_resena': str(resultado.inserted_id),
            'rating_promedio': rating_promedio,
            'total_resenas': total_resenas
        }), 201
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al publicar reseña: {str(e)}'
        }), 500