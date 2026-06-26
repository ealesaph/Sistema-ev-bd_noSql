from flask import Blueprint, request, jsonify
from app.config.database_config import db_sql
from app.models.sql_models import Pedido, DetallePedido, Cliente, Producto
from datetime import datetime

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/', methods=['GET'])
# URL: /api/pedidos
def obtener_pedidos():
    try:
        pedidos = Pedido.query.all()
        
        resultado = []
        for pedido in pedidos:
            resultado.append({
                'id_pedido': pedido.id_pedido,
                'cliente': pedido.cliente.nombre,
                'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                'estado': pedido.estado,
                'total': float(pedido.total),
                'cantidad_productos': len(pedido.detalles)
            })
        
        return jsonify({
            'exito': True,
            'pedidos': resultado,
            'total': len(resultado)
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener pedidos: {str(e)}'
        }), 500
        
@pedidos_bp.route('/', methods=['POST'])
# URL: /api/pedidos
def crear_pedido():
    
    try:
        datos = request.get_json()
        
        # 🧠 Valido campos obligatorios
        if 'id_cliente' not in datos or 'productos' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere id_cliente y lista de productos'
            }), 400
        
        # 🧠 Verifico que el cliente existe
        cliente = Cliente.query.get(datos['id_cliente'])
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': f'Cliente con ID {datos["id_cliente"]} no encontrado'
            }), 404
        
        nuevo_pedido = Pedido(
            id_cliente=datos['id_cliente'],
            fecha_pedido=datetime.utcnow(),
            estado='pendiente',
            total=0  # Se calculará después
        )
        db_sql.session.add(nuevo_pedido)
        db_sql.session.flush()
        
        total_pedido = 0
        
        for item in datos['productos']:
            producto = Producto.query.get(item['id_producto'])
            if not producto:
                raise Exception(f'Producto con ID {item["id_producto"]} no encontrado')
            
            if producto.stock_actual < item['cantidad']:
                raise Exception(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}')
            
            detalle = DetallePedido(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=float(producto.precio_base)
            )
            
            db_sql.session.add(detalle)
            
            producto.stock_actual -= item['cantidad']
            
            total_pedido += item['cantidad'] * float(producto.precio_base)
            
        nuevo_pedido.total = total_pedido
        
        db_sql.session.commit()
        
        return jsonify({
            'exito': True,
            'mensaje': 'Pedido creado exitosamente',
            'id_pedido': nuevo_pedido.id_pedido,
            'total': float(total_pedido)
        }), 201
        
    except Exception as e:
        db_sql.session.rollback()
        return jsonify({
            'exito': False,
            'mensaje': f'Error al crear pedido: {str(e)}'
        }), 500