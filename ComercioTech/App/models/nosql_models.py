#CREAR LAS MODELOS PARA LA NO SQL
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/comerciotech"
mongo = PyMongo(app)

db = mongo.db
productos = db['productos']
carritos = db['carritos']
logs_navegacion = db['logs_navegacion']
recomendaciones = db['recomendaciones']
sesiones = db['sesiones']
auditoria_nosql = db['auditoria_nosql']
resenas = db['resenas']


def serializacionDatos(doc):
    if doc is None:
        return None
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, list):
            out[k] = [serializacionDatos(i) if isinstance(i, dict) else i for i in v]
        elif isinstance(v, dict):
            out[k] = serializacionDatos(v)
        else:
            out[k] = v
    return out

def registrar_auditoria(coleccion, doc_id, accion, valor_anterior, valor_nuevo, origen="backend_python", id_usuario_sql=None):
    auditoria_nosql.insert_one({
        "coleccion_afectada": coleccion,
        "documento_id": doc_id,
        "accion": accion,
        "valor_anterior": valor_anterior,
        "valor_nuevo": valor_nuevo,
        "origen": origen,
        "id_usuario_sql": id_usuario_sql,
        "timestamp": datetime.now(timezone.utc),
    })

@app.post("/api/sesiones")
def crear_sesion():
    data = request.get_json()
    session_id = data.get("session_id")

    doc = {
        "_id": session_id,
        "id_usuario_sql": data.get("id_usuario_sql"),
        "ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", ""),
        "creada": datetime.now(timezone.utc),
        "expira": datetime.now(timezone.utc) + timedelta(hours=4),
    }
    sesiones.update_one({"_id": session_id}, {"$set": doc}, upsert=True)
    return jsonify(serializacionDatos(doc)), 201

@app.get("/api/sesiones/<session_id>")
def validar_sesion(session_id):
    doc = sesiones.find_one({"_id": session_id})
    if not doc or doc["expira"] < datetime.now(timezone.utc):
        return jsonify({"valida": False}), 401
    return jsonify({"valida": True, "sesion": serializacionDatos(doc)})

@app.post("/api/carritos/<session_id>/items")
def agregar_a_carrito(session_id):
    data = request.get_json()
    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad", 1)

    try:
        oid_producto = ObjectId(producto_id)
    except InvalidId:
        return jsonify({"error": "producto_id inválido"}), 400

    producto = productos.find_one({"_id": oid_producto})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    if producto.get("stock_disponible", 0) < cantidad:
        return jsonify({"error": "Stock insuficiente"}), 409

    item = {
        "producto_id": oid_producto,
        "sku": producto.get("sku"),
        "nombre": producto.get("nombre"),
        "cantidad": cantidad,
        "precio_unitario": producto.get("precio_actual", 0),
    }

    carrito = carritos.find_one({"session_id": session_id, "estado": "activo"})

    if carrito:
        existe = next((i for i in carrito["items"] if i.get("sku") == item["sku"]), None)
        if existe:
            carritos.update_one(
                {"_id": carrito["_id"], "items.sku": item["sku"]},
                {"$inc": {"items.$.cantidad": cantidad},
                 "$set": {"fecha_actualizacion": datetime.now(timezone.utc)}}
            )
        else:
            carritos.update_one(
                {"_id": carrito["_id"]},
                {"$push": {"items": item},
                 "$set": {"fecha_actualizacion": datetime.now(timezone.utc)}}
            )
        carrito_id = carrito["_id"]
        valor_anterior = carrito.get("total", 0)
    else:
        nuevo = {
            "id_cliente_sql": data.get("id_cliente_sql"),
            "session_id": session_id,
            "items": [item],
            "estado": "activo",
            "total": 0,
            "fecha_creacion": datetime.now(timezone.utc),
            "fecha_actualizacion": datetime.now(timezone.utc),
            "ttl_expira": datetime.now(timezone.utc) + timedelta(days=7),
        }
        carrito_id = carritos.insert_one(nuevo).inserted_id
        valor_anterior = 0

    carrito_actualizado = carritos.find_one({"_id": carrito_id})
    nuevo_total = sum(i["cantidad"] * i["precio_unitario"] for i in carrito_actualizado["items"])
    carritos.update_one({"_id": carrito_id}, {"$set": {"total": nuevo_total}})

    registrar_auditoria("carritos", carrito_id, "item_agregado", valor_anterior, nuevo_total, id_usuario_sql=data.get("id_cliente_sql"))

    logs_navegacion.insert_one({
        "id_cliente_sql": data.get("id_cliente_sql"),
        "session_id": session_id,
        "evento": "agregar_carrito",
        "producto_id": oid_producto,
        "sku": producto.get("sku"),
        "categoria": producto.get("categoria"),
        "metadata": {"origen": "ficha_producto", "dispositivo": data.get("dispositivo", "desconocido")},
        "timestamp": datetime.now(timezone.utc),
    })

    return jsonify(serializacionDatos(carritos.find_one({"_id": carrito_id}))), 200

@app.post("/api/logs/vista-producto")
def registrar_vista():
    data = request.get_json()
    try:
        oid_producto = ObjectId(data["producto_id"])
    except (InvalidId, KeyError):
        return jsonify({"error": "producto_id inválido o faltante"}), 400

    producto = productos.find_one({"_id": oid_producto}, {"categoria": 1, "sku": 1})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    log = {
        "id_cliente_sql": data.get("id_cliente_sql"),
        "session_id": data.get("session_id"),
        "evento": "vista_producto",
        "producto_id": oid_producto,
        "sku": producto.get("sku"),
        "categoria": producto.get("categoria"),
        "metadata": {
            "origen": data.get("origen", "desconocido"),
            "dispositivo": data.get("dispositivo", "desconocido"),
            "duracion_vista_seg": data.get("duracion_vista_seg"),
        },
        "timestamp": datetime.now(timezone.utc),
    }
    logs_navegacion.insert_one(log)
    return jsonify({"mensaje": "Vista registrada"}), 201

@app.get("/api/recomendaciones/<id_cliente_sql>")
def obtener_recomendaciones(id_cliente_sql):
    try:
        id_cliente_sql = int(id_cliente_sql)
    except ValueError:
        pass

    pipeline_vistos = [
        {"$match": {
            "id_cliente_sql": id_cliente_sql,
            "evento": {"$in": ["vista_producto", "agregar_carrito"]},
            "timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)},
        }},
        {"$sort": {"timestamp": -1}},
        {"$group": {
            "_id": "$producto_id",
            "sku": {"$first": "$sku"},
            "categoria": {"$first": "$categoria"},
            "ultima_vista": {"$first": "$timestamp"},
        }},
        {"$limit": 5},
    ]
    vistos = list(logs_navegacion.aggregate(pipeline_vistos))

    if not vistos:
        return jsonify({"productos_vistos_recientes": [], "productos_recomendados": []})

    categorias_interes = list({v.get("categoria") for v in vistos if v.get("categoria")})
    productos_vistos_ids = [v["_id"] for v in vistos]

    candidatos = list(productos.find(
        {
            "categoria": {"$in": categorias_interes},
            "_id": {"$nin": productos_vistos_ids},
            "activo": True,
        },
        {"sku": 1, "nombre": 1, "categoria": 1, "rating_promedio": 1, "total_resenas": 1}
    ).sort("rating_promedio", -1).limit(5))

    recomendados = [
        {
            "producto_id": str(c["_id"]),
            "sku": c.get("sku"),
            "score": round(min(0.5 + c.get("rating_promedio", 0) / 10, 0.99), 2),
            "motivo": "categoria_relacionada",
        }
        for c in candidatos
    ]

    resultado = {
        "id_cliente_sql": id_cliente_sql,
        "productos_vistos_recientes": [
            {"producto_id": str(v["_id"]), "sku": v.get("sku"), "ultima_vista": v["ultima_vista"].isoformat()}
            for v in vistos if v.get("ultima_vista")
        ],
        "productos_recomendados": recomendados,
        "fecha_calculo": datetime.now(timezone.utc),
    }

    recomendaciones.update_one(
        {"id_cliente_sql": id_cliente_sql},
        {"$set": resultado},
        upsert=True,
    )

    return jsonify(serializacionDatos(resultado))

@app.get("/api/auditoria")
def consultar_auditoria():
    coleccion = request.args.get("coleccion")
    origen = request.args.get("origen")
    desde = request.args.get("desde")

    filtro = {}
    if coleccion:
        filtro["coleccion_afectada"] = coleccion
    if origen:
        filtro["origen"] = origen
    if desde:
        filtro["timestamp"] = {"$gte": datetime.fromisoformat(desde)}

    cursor = auditoria_nosql.find(filtro).sort("timestamp", -1).limit(100)
    return jsonify([serializacionDatos(doc) for doc in cursor])

@app.post("/api/productos/<producto_id>/resenas")
def crear_resena(producto_id):
    try:
        oid_producto = ObjectId(producto_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400

    data = request.get_json()
    producto = productos.find_one({"_id": oid_producto}, {"sku": 1})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    resena = {
        "producto_id": oid_producto,
        "sku": producto.get("sku"),
        "id_cliente_sql": data.get("id_cliente_sql"),
        "nombre_cliente": data.get("nombre_cliente"),
        "rating": data.get("rating"),
        "titulo": data.get("titulo", ""),
        "comentario": data.get("comentario", ""),
        "verificada": data.get("verificada", False),
        "fecha": datetime.now(timezone.utc),
    }
    resena_id = resenas.insert_one(resena).inserted_id

    pipeline = [
        {"$match": {"producto_id": oid_producto}},
        {"$group": {"_id": None, "promedio": {"$avg": "$rating"}, "total": {"$sum": 1}}},
    ]
    agregado = list(resenas.aggregate(pipeline))
    if agregado:
        stats = agregado[0]
        productos.update_one(
            {"_id": oid_producto},
            {"$set": {
                "rating_promedio": round(stats["promedio"], 1),
                "total_resenas": stats["total"],
            }}
        )

    return jsonify(serializacionDatos(resenas.find_one({"_id": resena_id}))), 201

@app.get("/api/productos/<producto_id>/resenas")
def listar_resenas(producto_id):
    try:
        oid_producto = ObjectId(producto_id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400

    cursor = resenas.find({"producto_id": oid_producto}).sort("fecha", -1)
    return jsonify([serializacionDatos(doc) for doc in cursor])

@app.put("/api/proveedores/productos/<sku>/stock-precio")
def actualizar_desde_proveedor(sku):
    data = request.get_json()
    nuevo_stock = data.get("stock_disponible")
    nuevo_precio = data.get("precio_actual")

    producto = productos.find_one({"sku": sku})
    if not producto:
        return jsonify({"error": "SKU no encontrado"}), 404

    cambios = {}
    if nuevo_stock is not None and nuevo_stock != producto.get("stock_disponible"):
        registrar_auditoria(
            "productos", producto["_id"], "actualizacion_stock",
            valor_anterior=producto.get("stock_disponible"),
            valor_nuevo=nuevo_stock,
            origen="api_proveedor",
            id_usuario_sql=None,
        )
        cambios["stock_disponible"] = nuevo_stock

    if nuevo_precio is not None and nuevo_precio != producto.get("precio_actual"):
        registrar_auditoria(
            "productos", producto["_id"], "actualizacion_precio",
            valor_anterior=producto.get("precio_actual"),
            valor_nuevo=nuevo_precio,
            origen="api_proveedor",
        )
        cambios["precio_actual"] = nuevo_precio

    if not cambios:
        return jsonify({"mensaje": "Sin cambios"}), 200

    cambios["fecha_actualizacion"] = datetime.now(timezone.utc)
    productos.update_one({"_id": producto["_id"]}, {"$set": cambios})

    return jsonify(serializacionDatos(productos.find_one({"_id": producto["_id"]})))

def job_recalcular_recomendaciones():
    clientes_activos = logs_navegacion.distinct(
        "id_cliente_sql",
        {"timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(days=7)}}
    )

    for id_cliente in clientes_activos:
        if id_cliente is None:
            continue
        anterior = recomendaciones.find_one({"id_cliente_sql": id_cliente})

        # La lógica de recálculo se omitió en el snippet o se llama por el endpoint
        pass

if __name__ == '__main__':
    app.run(debug=True, port=5001)
