import os
import sys

# Añadir el directorio del proyecto al path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ComercioTech'))

from app import create_app
from app.config.database_config import db_sql, db_mongo
from app.models.sql_models import Usuario, Cliente, Pedido, DetallePedido, Producto, Direccion
from bson import ObjectId

def test_integration():
    print("Iniciando pruebas de integración automatizadas...")
    app = create_app()
    client = app.test_client()
    
    # Datos de prueba
    email = "testuser_unique@comerciotech.com"
    password = "supersecretpassword"
    nombre = "Juan"
    apellido = "Pérez"
    rut = "99.999.999-9"
    
    # 0. Limpiar registros de prueba anteriores si existen
    with app.app_context():
        cli = Cliente.query.filter_by(email=email).first()
        if cli:
            # Eliminar direcciones asociadas
            Direccion.query.filter_by(id_cliente=cli.id_cliente).delete()
            # Eliminar pedidos y detalles asociados
            peds = Pedido.query.filter_by(id_cliente=cli.id_cliente).all()
            for p in peds:
                DetallePedido.query.filter_by(id_pedido=p.id_pedido).delete()
                db_sql.session.delete(p)
            # Eliminar cliente
            db_sql.session.delete(cli)
        
        usr = Usuario.query.filter_by(email=email).first()
        if usr:
            db_sql.session.delete(usr)
        db_sql.session.commit()
        
        # Obtener un ID de producto de PostgreSQL con stock disponible
        prod = Producto.query.filter(Producto.stock > 0).first()
        if not prod:
            print("Error: No hay productos en la base de datos PostgreSQL. Ejecuta primero sync_db.py")
            return
        id_producto_sql = prod.id_producto
        nombre_producto = prod.nombre
        precio_producto = float(prod.precio)
        print(f"Producto de prueba seleccionado: {nombre_producto} (ID SQL: {id_producto_sql}, Stock: {prod.stock})")

        # Buscar el ID correspondiente en MongoDB
        prod_mongo = db_mongo.db.productos.find_one({"id_producto_sql": id_producto_sql})
        assert prod_mongo is not None, "El producto no está en MongoDB"
        producto_id_mongo = str(prod_mongo["_id"])
        print(f"Producto correspondiente en MongoDB encontrado: {producto_id_mongo}")
        
        # Limpiar cualquier reseña antigua de prueba de este producto en MongoDB
        db_mongo.db.resenas.delete_many({"producto_id": ObjectId(producto_id_mongo)})

    # 1. Registrar Cliente
    print("\nPaso 1: Registrando cliente...")
    register_payload = {
        "email": email,
        "contraseña": password,
        "nombre": nombre,
        "apellido": apellido,
        "rut": rut,
        "telefono": "+56912345678",
        "direccion": {
            "calle": "Alameda",
            "numero": "340",
            "comuna": "Santiago",
            "ciudad": "Santiago",
            "region": "Metropolitana",
            "pais": "Chile",
            "codigo_postal": "8320000"
        }
    }
    
    res = client.post('/leo/auth/register-cliente', json=register_payload)
    data = res.get_json()
    assert res.status_code == 201, f"Registro fallido: {data}"
    assert data['exito'] is True
    print("Cliente registrado exitosamente!")
    
    cliente_id = data['cliente_id']
    usuario_id = data['usuario_id']
    
    # 2. Iniciar Sesión (Login)
    print("\nPaso 2: Iniciando sesión...")
    login_payload = {
        "email": email,
        "contraseña": password
    }
    res = client.post('/leo/auth/login', json=login_payload)
    data = res.get_json()
    assert res.status_code == 200, f"Login fallido: {data}"
    assert data['exito'] is True
    assert data['usuario']['id_cliente'] == cliente_id
    assert data['usuario']['id_usuario'] == usuario_id
    print("Login exitoso! Token y id_cliente obtenidos correctamente.")
    
    token = data['token']
    
    # 3. Consultar Detalles de Producto
    print("\nPaso 3: Consultando detalles del producto en MongoDB...")
    res = client.get(f'/leo/productos/{producto_id_mongo}')
    data = res.get_json()
    assert res.status_code == 200, f"Error al cargar detalle: {data}"
    assert data['exito'] is True
    assert data['producto']['nombre'] == nombre_producto
    print("Detalles del producto cargados correctamente!")

    # 4. Obtener Recomendaciones y verificar log de Auditoría de Vistas (Adyacentes)
    print("\nPaso 4: Obteniendo recomendaciones y auditando productos adyacentes...")
    res = client.get(f'/leo/productos/{producto_id_mongo}/recomendaciones?cliente_id={cliente_id}')
    data = res.get_json()
    assert res.status_code == 200, f"Error al cargar recomendaciones: {data}"
    assert data['exito'] is True
    print(f"Recomendaciones cargadas: {len(data['recomendaciones'])} productos adyacentes.")
    
    # Verificar que se guardó el log con adyacentes en MongoDB
    with app.app_context():
        log = db_mongo.db.logs_navegacion.find_one({
            "cliente_id": cliente_id,
            "producto_id": producto_id_mongo,
            "tipo_evento": "vista_producto"
        })
        assert log is not None, "El log de auditoría de vistas no fue registrado"
        assert "productos_adyacentes" in log, "No se registraron los productos adyacentes en la auditoría"
        print(f"Auditoría exitosa: Log de vista registrado con {len(log['productos_adyacentes'])} productos adyacentes en metadatos.")

    # 5. Intentar publicar reseña SIN haber comprado el producto (Bloqueo 403)
    print("\nPaso 5: Intentando publicar reseña SIN haber comprado el producto (Debe fallar)...")
    resena_payload = {
        "id_cliente": cliente_id,
        "rating": 5,
        "titulo": "Excelente!",
        "comentario": "Me gustó mucho aunque no lo compré.",
        "nombre_cliente": "Juan Pérez"
    }
    res = client.post(f'/leo/productos/{producto_id_mongo}/resenas', json=resena_payload)
    data = res.get_json()
    assert res.status_code == 403, f"Se debió denegar el acceso pero retornó: {res.status_code}"
    assert data['exito'] is False
    assert "Debes haber comprado este producto" in data['mensaje']
    print("Acceso denegado correctamente (Código 403)! Un usuario que no ha comprado no puede reseñar.")

    # 6. Agregar elemento a carrito en MongoDB
    print("\nPaso 6: Agregando producto al carrito en MongoDB...")
    carrito_payload = {
        "cliente_id": cliente_id,
        "producto_id": producto_id_mongo,
        "cantidad": 1,
        "nombre": nombre_producto,
        "precio_unitario": precio_producto,
        "id_producto_sql": id_producto_sql
    }
    res = client.post('/leo/carrito/', json=carrito_payload)
    data = res.get_json()
    assert res.status_code == 200, f"Error al agregar al carrito: {data}"
    assert data['exito'] is True
    print("Producto agregado al carrito de MongoDB con éxito.")
    
    # 7. Crear Pedido (Compra) en PostgreSQL
    print("\nPaso 7: Realizando compra (Pedido) en PostgreSQL...")
    pedido_payload = {
        "id_cliente": cliente_id,
        "id_usuario": usuario_id,
        "productos": [
            {
                "id_producto": id_producto_sql,
                "cantidad": 1
            }
        ]
    }
    res = client.post('/leo/pedidos/', json=pedido_payload, headers={'Authorization': f'Bearer {token}'})
    data = res.get_json()
    assert res.status_code == 201, f"Error al crear pedido: {data}"
    assert data['exito'] is True
    id_pedido = data['id_pedido']
    print(f"Pedido de compra creado exitosamente con ID: {id_pedido}")
    
    # 8. Publicar reseña DESPUÉS de haber comprado el producto (Éxito 201)
    print("\nPaso 8: Publicando reseña DESPUÉS de haber comprado el producto (Debe funcionar)...")
    res = client.post(f'/leo/productos/{producto_id_mongo}/resenas', json=resena_payload)
    data = res.get_json()
    assert res.status_code == 201, f"Error al publicar reseña: {data}"
    assert data['exito'] is True
    print("Reseña publicada exitosamente con el producto comprado!")

    # 9. Listar Reseñas y Verificar que aparezca
    print("\nPaso 9: Consultando la lista de reseñas del producto...")
    res = client.get(f'/leo/productos/{producto_id_mongo}/resenas')
    data = res.get_json()
    assert res.status_code == 200
    assert len(data['resenas']) == 1
    assert data['resenas'][0]['titulo'] == "Excelente!"
    assert data['resenas'][0]['rating'] == 5
    # 10. Listar Pedidos del Cliente y Consultar Detalle de un Pedido
    print("\nPaso 10: Listando historial de pedidos y obteniendo detalles...")
    res = client.get('/leo/pedidos/', headers={'Authorization': f'Bearer {token}'})
    data = res.get_json()
    assert res.status_code == 200, f"Error al listar pedidos: {data}"
    assert data['exito'] is True
    assert len(data['pedidos']) >= 1, "Debe haber al menos un pedido en el historial"
    print(f"Pedidos recuperados en el historial: {len(data['pedidos'])}")
    
    # Consultar detalle del pedido creado en Paso 7
    res = client.get(f'/leo/pedidos/{id_pedido}', headers={'Authorization': f'Bearer {token}'})
    data = res.get_json()
    assert res.status_code == 200, f"Error al obtener detalle del pedido: {data}"
    assert data['exito'] is True
    assert data['pedido']['id_pedido'] == id_pedido
    assert len(data['pedido']['detalles']) == 1
    assert data['pedido']['detalles'][0]['id_producto'] == id_producto_sql
    print("Detalles del pedido verificados con éxito a través del endpoint seguro!")

    print("\n¡TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON EXITOSAMENTE!")

if __name__ == "__main__":
    test_integration()
