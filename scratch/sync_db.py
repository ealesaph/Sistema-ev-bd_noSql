import sys
import psycopg2
from pymongo import MongoClient

def sync():
    print("Iniciando sincronización de base de datos...")
    
    # Conexiones
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db_mongo = mongo_client["comerciotech"]
    productos_col = db_mongo["productos"]
    
    pg_conn = psycopg2.connect("postgresql://leo:1234@127.0.0.1:5432/comerciotech")
    pg_cur = pg_conn.cursor()
    
    # 1. Obtener proveedores únicos de MongoDB
    print("Obteniendo proveedores de MongoDB...")
    proveedores_ids = productos_col.distinct("id_proveedor_sql")
    print(f"Encontrados {len(proveedores_ids)} proveedores únicos en MongoDB.")
    
    # 2. Insertar proveedores en PostgreSQL
    print("Insertando proveedores en PostgreSQL...")
    for prov_id in proveedores_ids:
        pg_cur.execute(
            "INSERT INTO proveedor (id_proveedor, nombre, rut, activo) VALUES (%s, %s, %s, %s) ON CONFLICT (id_proveedor) DO NOTHING",
            (prov_id, f"Proveedor {prov_id}", f"{prov_id}-{prov_id % 9}", True)
        )
    pg_conn.commit()
    print("Proveedores sincronizados en PostgreSQL.")
    
    # 3. Limpiar tabla productos en PostgreSQL para evitar duplicados si se corre de nuevo
    print("Limpiando tabla producto en PostgreSQL...")
    pg_cur.execute("TRUNCATE TABLE producto CASCADE")
    pg_conn.commit()
    
    # 4. Insertar productos en PostgreSQL y actualizar MongoDB
    print("Sincronizando productos...")
    mongo_products = list(productos_col.find({}))
    total = len(mongo_products)
    print(f"Procesando {total} productos...")
    
    for idx, p in enumerate(mongo_products):
        # Insertar en Postgres
        nombre = p.get("nombre", "Producto Sin Nombre")
        descripcion = p.get("descripcion", "")
        precio = float(p.get("precio_actual", p.get("precio", 0)))
        stock = int(p.get("stock_disponible", 100))
        activo = bool(p.get("activo", True))
        id_proveedor = int(p.get("id_proveedor_sql", proveedores_ids[0]))
        
        pg_cur.execute(
            """
            INSERT INTO producto (id_proveedor, nombre, descripcion, precio, stock, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_producto
            """,
            (id_proveedor, nombre, descripcion, precio, stock, activo)
        )
        id_producto_sql = pg_cur.fetchone()[0]
        
        # Actualizar MongoDB
        productos_col.update_one(
            {"_id": p["_id"]},
            {"$set": {"id_producto_sql": id_producto_sql}}
        )
        
        if (idx + 1) % 500 == 0:
            print(f"  → {idx + 1} / {total} sincronizados...")
            pg_conn.commit()
            
    pg_conn.commit()
    print("¡Sincronización finalizada con éxito!")
    
    pg_cur.close()
    pg_conn.close()
    mongo_client.close()

if __name__ == "__main__":
    sync()
