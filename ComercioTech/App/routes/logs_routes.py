from flask import Blueprint, request, jsonify
from app.config.database_config import db_mongo
from datetime import datetime, timedelta

logs_bp = Blueprint('logs', __name__)

# URL: /api/logs/navegacion
@logs_bp.route('/navegacion', methods=['POST'])
def registrar_log_navegacion():

    try:
        datos = request.get_json()
        
        # Validar campos obligatorios
        if 'tipo_evento' not in datos:
            return jsonify({
                'exito': False,
                'mensaje': 'Se requiere tipo_evento'
            }), 400
        
        # Crear el documento de log
        log_documento = {
            'cliente_id': datos.get('cliente_id'),
            'session_id': datos.get('session_id'),
            'ip_origen': request.remote_addr,
            'tipo_evento': datos['tipo_evento'],
            'pagina': datos.get('pagina'),
            'producto_id': datos.get('producto_id'),
            'termino_busqueda': datos.get('termino_busqueda'),
            'referer': request.headers.get('Referer'),
            'user_agent': request.headers.get('User-Agent'),
            'fecha_hora': datetime.utcnow(),
            'tiempo_estadia': datos.get('tiempo_estadia', 0)
        }
        
        # Insertar en MongoDB
        resultado = db_mongo.db.logs_navegacion.insert_one(log_documento)
        
        return jsonify({
            'exito': True,
            'mensaje': 'Log registrado exitosamente',
            'id_log': str(resultado.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al registrar log: {str(e)}'
        }), 500

# URL: /api/logs/recomendaciones/<int:cliente_id>
@logs_bp.route('/recomendaciones/<int:cliente_id>', methods=['GET'])
def obtener_recomendaciones(cliente_id):
    
    try:
        logs_collection = db_mongo.db.logs_navegacion
        
        # Obtener productos vistos recientemente (últimos 7 días)
        fecha_limite = datetime.utcnow() - timedelta(days=7)
        
        pipeline = [
            {
                '$match': {
                    'cliente_id': cliente_id,
                    'fecha_hora': {'$gte': fecha_limite},
                    'tipo_evento': {'$in': ['vista_producto', 'agregado_carrito']}
                }
            },
            {
                '$group': {
                    '_id': '$producto_id',
                    'frecuencia': {'$sum': 1},
                    'ultima_vista': {'$max': '$fecha_hora'}
                }
            },
            {
                '$sort': {'frecuencia': -1, 'ultima_vista': -1}
            },
            {
                '$limit': 10
            }
        ]
        
        resultados = logs_collection.aggregate(pipeline)
        
        recomendaciones = []
        for item in resultados:
            recomendaciones.append({
                'producto_id': item['_id'],
                'frecuencia': item['frecuencia'],
                'ultima_vista': item['ultima_vista'].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'exito': True,
            'cliente_id': cliente_id,
            'recomendaciones': recomendaciones,
            'total': len(recomendaciones)
        }), 200
        
    except Exception as e:
        return jsonify({
            'exito': False,
            'mensaje': f'Error al obtener recomendaciones: {str(e)}'
        }), 500