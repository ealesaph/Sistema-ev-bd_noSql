from flask import Blueprint, request, jsonify
from app.config.database_config import db_sql
from app.models.sql_models import Pedido, DetallePedido, Cliente, Producto, Usuario, Factura, PagoProveedor, Proveedor
from datetime import datetime
from app.middleware.auth_middleware import token_requerido, rol_requerido

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/', methods=['GET'])
@token_requerido
# URL: /api/pedidos
def obtener_pedidos():
    try:
        payload = request.usuario_payload
        usuario_id = payload['usuario_id']
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({
                'exito': False,
                'mensaje': 'Usuario no encontrado'
            }), 404
            
        cliente = Cliente.query.filter_by(email=usuario.email).first()
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': 'Cliente no encontrado'
            }), 404
            
        pedidos = Pedido.query.filter_by(id_cliente=cliente.id_cliente).order_by(Pedido.fecha_pedido.desc()).all()
        
        resultado = []
        for pedido in pedidos:
            resultado.append({
                'id_pedido': pedido.id_pedido,
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

@pedidos_bp.route('/<int:id_pedido>', methods=['GET'])
@token_requerido
# URL: /api/pedidos/<id_pedido>
def obtener_detalle_pedido(id_pedido):
    try:
        payload = request.usuario_payload
        usuario_id = payload['usuario_id']
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({
                'exito': False,
                'mensaje': 'Usuario no encontrado'
            }), 404
            
        cliente = Cliente.query.filter_by(email=usuario.email).first()
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': 'Cliente no encontrado'
            }), 404
            
        pedido = Pedido.query.filter_by(id_pedido=id_pedido, id_cliente=cliente.id_cliente).first()
        if not pedido:
            return jsonify({
                'exito': False,
                'mensaje': 'Pedido no encontrado o no pertenece al usuario'
            }), 404
            
        detalles_resultado = []
        for detalle in pedido.detalles:
            detalles_resultado.append({
                'id_detalle': detalle.id_detalle,
                'id_producto': detalle.id_producto,
                'nombre_producto': detalle.producto.nombre,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.subtotal)
            })
            
        return jsonify({
            'exito': True,
            'pedido': {
                'id_pedido': pedido.id_pedido,
                'fecha_pedido': pedido.fecha_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                'estado': pedido.estado,
                'total': float(pedido.total),
                'detalles': detalles_resultado
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener detalles del pedido: {str(e)}'
        }), 500

@pedidos_bp.route('/', methods=['POST'])
@token_requerido
# URL: /api/pedidos
def crear_pedido():
    try:
        datos = request.get_json()
        
        if 'id_cliente' not in datos or 'id_usuario' not in datos or 'productos' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere id_cliente, id_usuario y lista de productos'
            }), 400
        
        cliente = Cliente.query.get(datos['id_cliente'])
        if not cliente:
            return jsonify({
                'exito': False,
                'mensaje': f'Cliente con ID {datos["id_cliente"]} no encontrado'
            }), 404
            
        from app.models.sql_models import Usuario
        usuario = Usuario.query.get(datos['id_usuario'])
        if not usuario:
            return jsonify({
                'exito': False,
                'mensaje': f'Usuario con ID {datos["id_usuario"]} no encontrado'
            }), 404
        
        nuevo_pedido = Pedido(
            id_cliente=datos['id_cliente'],
            id_usuario=datos['id_usuario'],
            fecha_pedido=datetime.utcnow(),
            estado='PENDIENTE',
            total=0
        )
        db_sql.session.add(nuevo_pedido)
        db_sql.session.flush()
        
        total_pedido = 0
        
        for item in datos['productos']:
            producto = Producto.query.get(item['id_producto'])
            if not producto:
                raise Exception(f'Producto con ID {item["id_producto"]} no encontrado')
            
            if producto.stock < item['cantidad']:
                raise Exception(f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}')
            
            detalle = DetallePedido(
                id_pedido=nuevo_pedido.id_pedido,
                id_producto=item['id_producto'],
                cantidad=item['cantidad'],
                precio_unitario=float(producto.precio)
            )
            
            db_sql.session.add(detalle)
            producto.stock -= item['cantidad']
            
            total_pedido += item['cantidad'] * float(producto.precio)
        
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

@pedidos_bp.route('/facturas', methods=['GET'])
@token_requerido
@rol_requerido(['Administrador'])
def listar_facturas_admin():
    try:
        facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
        resultado = []
        for fac in facturas:
            resultado.append({
                'id_factura': fac.id_factura,
                'numero_factura': fac.numero_factura,
                'id_pedido': fac.id_pedido,
                'cliente': fac.cliente.nombre,
                'fecha_emision': fac.fecha_emision.strftime('%Y-%m-%d %H:%M:%S'),
                'monto_neto': float(fac.monto_neto),
                'impuesto': float(fac.impuesto),
                'monto_total': float(fac.monto_total),
                'estado': fac.estado
            })
        return jsonify({
            'exito': True,
            'facturas': resultado,
            'total': len(resultado)
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener facturas: {str(e)}'
        }), 500

@pedidos_bp.route('/reporte-contable', methods=['GET'])
@token_requerido
@rol_requerido(['Administrador'])
def obtener_reporte_contable():
    try:
        # Sumas de facturas
        facturas = Factura.query.all()
        total_ventas = sum(float(f.monto_total) for f in facturas if f.estado != 'ANULADA')
        total_neto = sum(float(f.monto_neto) for f in facturas if f.estado != 'ANULADA')
        total_impuestos = total_ventas - total_neto
        
        # Pagos pendientes a proveedores (Cuentas por pagar)
        pagos = PagoProveedor.query.all()
        cuentas_por_pagar = sum(float(p.monto) for p in pagos if p.estado == 'PENDIENTE')
        cuentas_pagadas = sum(float(p.monto) for p in pagos if p.estado == 'PAGADO')
        
        # Cantidades
        count_facturas = len(facturas)
        count_proveedores = Proveedor.query.count()
        count_pedidos = Pedido.query.count()
        
        # Ultimas facturas emitidas
        ultimas_facturas = []
        for f in Factura.query.order_by(Factura.fecha_emision.desc()).limit(5).all():
            ultimas_facturas.append({
                'numero_factura': f.numero_factura,
                'cliente': f.cliente.nombre,
                'monto_total': float(f.monto_total),
                'fecha': f.fecha_emision.strftime('%Y-%m-%d')
            })

        return jsonify({
            'exito': True,
            'reporte': {
                'total_ventas': total_ventas,
                'total_neto': total_neto,
                'total_impuestos': total_impuestos,
                'cuentas_por_pagar': cuentas_por_pagar,
                'cuentas_pagadas': cuentas_pagadas,
                'count_facturas': count_facturas,
                'count_proveedores': count_proveedores,
                'count_pedidos': count_pedidos,
                'ultimas_facturas': ultimas_facturas
            }
        }), 200
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al generar reporte contable: {str(e)}'
        }), 500