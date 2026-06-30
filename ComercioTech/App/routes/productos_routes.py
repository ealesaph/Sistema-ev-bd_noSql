from flask import Blueprint, request, jsonify
from app.config.database_config import db_mongo, db_sql
from bson import ObjectId
from datetime import datetime
import re
from app.models.sql_models import Producto as ProductoSQL, Proveedor, PagoProveedor, Usuario
from app.middleware.auth_middleware import token_requerido, rol_requerido

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/', methods=['GET'])
#URL: /api/productos
def obtener_productos():
    try:
        categoria = request.args.get('categoria')
        etiqueta = request.args.get('etiqueta')
        busqueda = request.args.get('busqueda') or request.args.get('q')
        activo = request.args.get('activo')
        page = int(request.args.get('page', 1))
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
        
        skip = (page - 1) * limit
        productos = productos_collection.find(filtro).skip(skip).limit(limit)
        
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

@productos_bp.route('/admin/stock', methods=['GET'])
@token_requerido
@rol_requerido(['Administrador'])
def listar_stock_admin():
    try:
        productos = ProductoSQL.query.all()
        resultado = []
        for p in productos:
            resultado.append({
                'id_producto': p.id_producto,
                'nombre': p.nombre,
                'stock': p.stock,
                'precio': float(p.precio),
                'activo': p.activo,
                'proveedor': p.proveedor.nombre if p.proveedor else 'Sin Proveedor'
            })
        return jsonify({
            'exito': True,
            'productos': resultado,
            'total': len(resultado)
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener stock: {str(e)}'
        }), 500

@productos_bp.route('/<int:id_producto>/stock', methods=['POST'])
@token_requerido
@rol_requerido(['Administrador'])
def actualizar_stock_producto(id_producto):
    try:
        datos = request.get_json()
        cantidad_cambio = int(datos.get('cantidad_cambio', 0))
        if cantidad_cambio == 0:
            return jsonify({'exito': False, 'mensaje': 'El cambio de cantidad no puede ser cero'}), 400
            
        # 1. Obtener producto en SQL
        producto = ProductoSQL.query.get(id_producto)
        if not producto:
            return jsonify({'exito': False, 'mensaje': 'Producto no encontrado en PostgreSQL'}), 404
            
        nuevo_stock = producto.stock + cantidad_cambio
        if nuevo_stock < 0:
            return jsonify({'exito': False, 'mensaje': f'Stock insuficiente. Stock actual: {producto.stock}'}), 400
            
        # 2. Modificar stock en SQL
        producto.stock = nuevo_stock
        
        # 3. Lógica de PagoProveedor (Cuentas por Pagar)
        costo_unitario = float(producto.precio)
        costo_total = abs(cantidad_cambio) * costo_unitario
        
        if cantidad_cambio > 0:
            # Aumento de stock: Crear una cuenta por pagar al proveedor
            pago = PagoProveedor(
                id_proveedor=producto.id_proveedor,
                monto=costo_total,
                metodo_pago='TRANSFERENCIA',
                estado='PENDIENTE',
                referencia=f'Abastecimiento de {cantidad_cambio} unidades de {producto.nombre}',
                fecha_creacion=datetime.utcnow()
            )
            db_sql.session.add(pago)
        else:
            # Disminución de stock: Buscar el último pago pendiente al proveedor para restar
            pago_pendiente = PagoProveedor.query.filter_by(
                id_proveedor=producto.id_proveedor,
                estado='PENDIENTE'
            ).order_by(PagoProveedor.fecha_creacion.desc()).first()
            
            if pago_pendiente:
                nuevo_monto = float(pago_pendiente.monto) - costo_total
                if nuevo_monto <= 0:
                    db_sql.session.delete(pago_pendiente)
                else:
                    pago_pendiente.monto = nuevo_monto
            
        # 4. Modificar en MongoDB (Mantener consistencia)
        db_mongo.db.productos.update_one(
            {'id_producto_sql': id_producto},
            {'$set': {'stock': nuevo_stock}}
        )
        
        # Guardar todo en SQL
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Stock actualizado y registro de proveedor procesado en transacción ACID',
            'nuevo_stock': nuevo_stock
        }), 200
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({'exito': False, 'mensaje': f'Error al actualizar stock: {str(e)}'}), 500

@productos_bp.route('/proveedores', methods=['GET'])
@token_requerido
@rol_requerido(['Administrador'])
def listar_proveedores_admin():
    try:
        proveedores = Proveedor.query.all()
        resultado = []
        for prov in proveedores:
            resultado.append({
                'id_proveedor': prov.id_proveedor,
                'nombre': prov.nombre,
                'rut': prov.rut,
                'email': prov.email,
                'telefono': prov.telefono,
                'activo': prov.activo
            })
        return jsonify({
            'exito': True,
            'proveedores': resultado,
            'total': len(resultado)
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener proveedores: {str(e)}'
        }), 500

@productos_bp.route('/proveedores/pagos', methods=['GET'])
@token_requerido
@rol_requerido(['Administrador'])
def listar_pagos_proveedores():
    try:
        pagos = PagoProveedor.query.order_by(PagoProveedor.fecha_creacion.desc()).all()
        resultado = []
        for p in pagos:
            resultado.append({
                'id_pago': p.id_pago,
                'id_proveedor': p.id_proveedor,
                'proveedor': p.proveedor.nombre if p.proveedor else 'Desconocido',
                'monto': float(p.monto),
                'metodo_pago': p.metodo_pago,
                'estado': p.estado,
                'referencia': p.referencia,
                'fecha_pago': p.fecha_pago.strftime('%Y-%m-%d') if p.fecha_pago else None,
                'fecha_creacion': p.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({
            'exito': True,
            'pagos': resultado,
            'total': len(resultado)
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener pagos: {str(e)}'
        }), 500

@productos_bp.route('/proveedores/pagos/<int:id_pago>/pagar', methods=['POST'])
@token_requerido
@rol_requerido(['Administrador'])
def pagar_proveedor(id_pago):
    try:
        pago = PagoProveedor.query.get(id_pago)
        if not pago:
            return jsonify({'exito': False, 'mensaje': 'Registro de pago no encontrado'}), 404
            
        pago.estado = 'PAGADO'
        pago.fecha_pago = datetime.utcnow().date()
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Pago al proveedor registrado exitosamente'
        }), 200
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({'exito': False, 'mensaje': f'Error al registrar pago: {str(e)}'}), 500