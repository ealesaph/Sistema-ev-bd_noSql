from flask import Blueprint, request, jsonify
from app.config.database_config import db_mongo
from bson import ObjectId
from datetime import datetime

carrito_bp = Blueprint('carrito', __name__)

# URL: /api/carrito/<int:cliente_id>
@carrito_bp.route('/<int:cliente_id>', methods=['GET'])
def obtener_carrito(cliente_id):
    try:
        carritos_collection = db_mongo.db.carritos
        
        carrito = carritos_collection.find_one({
            'cliente_id': cliente_id,
            'estado': 'activo'
        })
        
        if not carrito:
            return jsonify({
                'exito': True,
                'mensaje': 'No hay carrito activo para este cliente',
                'carrito': None
            }), 200
        
        carrito['_id'] = str(carrito['_id'])
        
        # Enriquecer los items del carrito con los detalles actualizados del producto
        productos_collection = db_mongo.db.productos
        for item in carrito.get('items', []):
            try:
                prod = productos_collection.find_one({'_id': ObjectId(item['producto_id'])})
                if prod:
                    item['categoria'] = prod.get('categoria', '')
                    item['sku'] = prod.get('sku', '')
                    item['atributos'] = prod.get('atributos', prod.get('atributos_variables', {}))
            except Exception:
                pass
                
        return jsonify({
            'exito': True,
            'carrito': carrito
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener carrito: {str(e)}'
        }), 500

# URL: /api/carrito
@carrito_bp.route('/', methods=['POST'])
def agregar_al_carrito():
    try:
        datos = request.get_json()
        
        if 'cliente_id' not in datos or 'producto_id' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere cliente_id y producto_id'
            }), 400
        
        cliente_id = datos['cliente_id']
        producto_id = datos['producto_id']
        cantidad = datos.get('cantidad', 1)
        nombre = datos.get('nombre', 'Producto')
        precio_unitario = datos.get('precio_unitario', 0)
        
        carritos_collection = db_mongo.db.carritos
        
        carrito = carritos_collection.find_one({
            'cliente_id': cliente_id,
            'estado': 'activo'
        })
        
        if not carrito:
            nuevo_carrito = {
                'cliente_id': cliente_id,
                'items': [],
                'total': 0,
                'fecha_creacion': datetime.utcnow(),
                'fecha_actualizacion': datetime.utcnow(),
                'estado': 'activo'
            }
            resultado = carritos_collection.insert_one(nuevo_carrito)
            carrito = carritos_collection.find_one({'_id': resultado.inserted_id})
        
        producto_existente = None
        for item in carrito['items']:
            if item['producto_id'] == producto_id:
                producto_existente = item
                break
        
        if producto_existente:
            producto_existente['cantidad'] += cantidad
            producto_existente['fecha_agregado'] = datetime.utcnow()
        else:
            carrito['items'].append({
                'producto_id': producto_id,
                'nombre': nombre,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'id_producto_sql': datos.get('id_producto_sql'),
                'categoria': datos.get('categoria', ''),
                'sku': datos.get('sku', ''),
                'atributos': datos.get('atributos', {}),
                'fecha_agregado': datetime.utcnow()
            })
        
        total = sum(item['cantidad'] * item['precio_unitario'] for item in carrito['items'])
        carrito['total'] = total
        carrito['fecha_actualizacion'] = datetime.utcnow()
        
        carritos_collection.update_one(
            {'_id': carrito['_id']},
            {'$set': {
                'items': carrito['items'],
                'total': carrito['total'],
                'fecha_actualizacion': carrito['fecha_actualizacion']
            }}
        )
        
        carrito['_id'] = str(carrito['_id'])
        
        return jsonify({
            'exito': True,
            'mensaje': 'Producto agregado al carrito',
            'carrito': carrito
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al agregar al carrito: {str(e)}'
        }), 500

# URL: /api/carrito/<int:cliente_id>
@carrito_bp.route('/<int:cliente_id>', methods=['DELETE'])
def vaciar_carrito(cliente_id):
    try:
        carritos_collection = db_mongo.db.carritos
        
        resultado = carritos_collection.update_one(
            {
                'cliente_id': cliente_id,
                'estado': 'activo'
            },
            {
                '$set': {
                    'items': [],
                    'total': 0,
                    'fecha_actualizacion': datetime.utcnow(),
                    'estado': 'inactivo'
                }
            }
        )
        
        if resultado.matched_count == 0:
            return jsonify({
                'exito': False,
                'mensaje': 'No se encontró un carrito activo para este cliente'
            }), 404
        
        return jsonify({
            'exito': True,
            'mensaje': 'Carrito vaciado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al vaciar carrito: {str(e)}'
        }), 500

# URL: /api/carrito/item
@carrito_bp.route('/item', methods=['DELETE'])
def eliminar_item_carrito():
    try:
        datos = request.get_json()
        
        if 'cliente_id' not in datos or 'producto_id' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere cliente_id y producto_id'
            }), 400
        
        cliente_id = datos['cliente_id']
        producto_id = datos['producto_id']
        
        carritos_collection = db_mongo.db.carritos
        
        carrito = carritos_collection.find_one({
            'cliente_id': cliente_id,
            'estado': 'activo'
        })
        
        if not carrito:
            return jsonify({
                'exito': False,
                'mensaje': 'No hay carrito activo para este cliente'
            }), 404
        
        items_actualizados = [item for item in carrito['items'] if item['producto_id'] != producto_id]
        
        if len(items_actualizados) == len(carrito['items']):
            return jsonify({
                'exito': False,
                'mensaje': 'El producto no está en el carrito'
            }), 404
        
        total = sum(item['cantidad'] * item['precio_unitario'] for item in items_actualizados)
        
        carritos_collection.update_one(
            {'_id': carrito['_id']},
            {'$set': {
                'items': items_actualizados,
                'total': total,
                'fecha_actualizacion': datetime.utcnow()
            }}
        )
        
        return jsonify({
            'exito': True,
            'mensaje': 'Producto eliminado del carrito',
            'total': total
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al eliminar item del carrito: {str(e)}'
        }), 500