# Cambios realizados sobre el proyecto original

Este archivo resume, archivo por archivo, qué se corrigió respecto a la versión
que subiste. La idea es que puedas explicar cada cambio si te preguntan por él.

## 1. ComercioTech/run.py
- Estaba vacío (0 bytes). Se agregó el arranque real de la app:
  `from App import create_app` (con A mayúscula, coincide con el nombre real
  de la carpeta) y `app.run(debug=True, host='0.0.0.0', port=5000)`.
- `host='0.0.0.0'` para que el servidor sea alcanzable desde fuera del
  contenedor si publicas el puerto 5000.

## 2. Imports en minúscula (`from app...` / `import app...`)
- Todos los archivos bajo `App/` importaban desde `app` (minúscula) pero la
  carpeta real se llama `App` (mayúscula). En Linux esto rompe el import
  porque el sistema de archivos es case-sensitive. Se corrigió con:
  ```
  find App -type f -name "*.py" -exec sed -i 's/from app\./from App./g' {} +
  find App -type f -name "*.py" -exec sed -i 's/import app\./import App./g' {} +
  ```

## 3. App/config/database_config.py
- Las cadenas de conexión eran placeholders (`usuario:contraseña@localhost...`).
- Se reemplazaron por las credenciales reales creadas en Postgres (`leo`/`1234`,
  base `comerciotech`) y por una cadena de Mongo con usuario de aplicación
  (`app_comerciotech`) en vez de conexión sin autenticación.

## 4. App/services/auth_service.py y App/middleware/auth_middleware.py
- El código original usaba campos que **no existen** en el modelo `Usuario`/`Rol`
  de `sql_models.py`: `nombre_usuario`, `hash_password`, `estado`, `id_cliente`,
  `nombre_rol`, `nivel_permiso`.
- El modelo real tiene: `Usuario(nombre, apellido, email, contrasena_hash, activo)`
  y `Rol(nombre, descripcion, activo)`.
- Se reescribió `auth_service.py` para usar **email** como identificador de
  login (no hay columna de nombre de usuario) y los campos reales del modelo.
- `auth_middleware.py`: como `Rol` no tiene `nivel_permiso`, el control de
  acceso por rol ahora compara `rol.nombre` contra una lista de roles
  permitidos: `@rol_requerido(['admin', 'vendedor'])`.

## 5. App/routes/auth_routes.py
- Actualizado para enviar `nombre`, `apellido`, `email`, `contraseña`, `id_rol`
  al registrar, y `email`/`contraseña` al iniciar sesión (antes pedía
  `nombre_usuario`).

## 6. App/routes/clientes_routes.py
- `obtener_cliente` y `crear_cliente` usaban `direccion.comuna`, columna que
  no existe en el modelo `Direccion` (tiene `calle`, `numero`, `ciudad`,
  `region`, `codigo_postal`, `tipo`). Se quitó esa referencia.
- `crear_cliente` no pedía `apellido`, que en el modelo es obligatorio
  (`nullable=False`) — esto causaba un error de integridad en cada alta de
  cliente. Se agregó como campo requerido.
- Se agregó `db_sql.session.flush()` antes de crear direcciones, para que
  `nuevo_cliente.id_cliente` ya tenga valor al usarlo como llave foránea.

## 7. App/routes/pedidos_routes.py
- Usaba `producto.stock_actual` y `producto.precio_base`, campos que **no
  existen** en el modelo SQL `Producto` (que tiene `stock` y `precio`). Esos
  nombres pertenecen al esquema de Mongo, no al de Postgres. Se corrigió para
  usar `producto.stock` y `producto.precio`.
- El estado del pedido se creaba como `'pendiente'` (minúscula), pero el
  `CheckConstraint` de la tabla exige `'PENDIENTE'` (mayúscula) — esto hacía
  fallar cualquier creación de pedido. Se corrigió a `'PENDIENTE'`.

## 8. Decisión de arquitectura confirmada (no se tocó código de Mongo)
- El proyecto tenía dos esquemas de catálogo en Mongo incompatibles entre sí:
  uno en `productos_routes.py`/`carrito_routes.py` (`precio_base`,
  `stock_actual`, `cliente_id`) y otro en `nosql_models.py` / el script de
  seed (`sku`, `precio_actual`, `stock_disponible`, `session_id`).
- Se mantiene oficialmente el primero, porque es el que ya está conectado a
  la app real vía Blueprints. `nosql_models.py` sigue siendo una app Flask
  standalone (puerto 5001) separada, no integrada — si no la vas a usar,
  puedes eliminarla más adelante.

## 9. Carpetas nuevas
- `datos_ejemplo/`: scripts de inserción (`inserciones_postgres.sql`,
  `inserciones_mongo.js`) con datos consistentes entre ambas bases.
- `docs/`: Informe Técnico (`Informe_Tecnico_ComercioTech.docx`) con los
  entregables pedidos por la guía de la asignatura.
