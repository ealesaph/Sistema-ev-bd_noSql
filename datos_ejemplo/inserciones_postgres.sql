-- =========================================================
-- Inserciones de datos de ejemplo - ComercioTech (PostgreSQL)
-- Ejecutar dentro del contenedor:
--   psql -U leo -d comerciotech -f inserciones_postgres.sql
-- =========================================================

-- 1) Roles
INSERT INTO rol (nombre, descripcion) VALUES
  ('admin', 'Acceso total al sistema'),
  ('vendedor', 'Gestiona pedidos y clientes'),
  ('cliente', 'Usuario final de la tienda');

-- 2) Usuarios (contrasena_hash de ejemplo; en producción usar bcrypt real)
INSERT INTO usuario (id_rol, nombre, apellido, email, contrasena_hash) VALUES
  (1, 'Leonardo', 'Soto', 'leo.admin@comerciotech.cl', '$2b$12$ejemplodehashbcrypt0000000000000000000000000000000'),
  (2, 'Ana', 'Pérez', 'ana.vendedora@comerciotech.cl', '$2b$12$ejemplodehashbcrypt0000000000000000000000000000001');

-- 3) Proveedores
INSERT INTO proveedor (nombre, rut, email, telefono) VALUES
  ('Distribuidora TechChile SpA', '76123456-7', 'contacto@techchile.cl', '+56221234567'),
  ('ImportaTec Ltda.', '77234567-8', 'ventas@importatec.cl', '+56229876543');

-- 4) Clientes
INSERT INTO cliente (nombre, apellido, email, telefono, rut) VALUES
  ('María', 'González', 'maria.gonzalez@example.com', '+56912345678', '12345678-9'),
  ('Carlos', 'Muñoz', 'carlos.munoz@example.com', '+56998765432', '98765432-1');

-- 5) Direcciones
INSERT INTO direccion (id_cliente, calle, numero, ciudad, region, codigo_postal, tipo) VALUES
  (1, 'Av. Providencia', '1234', 'Santiago', 'Metropolitana', '7500000', 'ENVIO'),
  (2, 'Calle Las Flores', '567', 'Valparaíso', 'Valparaíso', '2340000', 'PRINCIPAL');

-- 6) Productos (módulo SQL: costos / stock crítico de inventario)
INSERT INTO producto (id_proveedor, nombre, descripcion, precio, stock) VALUES
  (1, 'Laptop Lenovo ThinkPad X1', 'Ultrabook empresarial 14"', 899990, 35),
  (1, 'Mouse Logitech MX Master 3', 'Mouse inalámbrico ergonómico', 59990, 120),
  (2, 'Teclado Mecánico Redragon K552', 'Switch rojo, retroiluminado', 39990, 80);

-- 7) Pedido + detalle
INSERT INTO pedido (id_cliente, id_usuario, estado, total) VALUES
  (1, 2, 'CONFIRMADO', 959980);

INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES
  (1, 1, 1, 899990),
  (1, 2, 1, 59990);

-- 8) Factura
INSERT INTO factura (id_pedido, id_cliente, numero_factura, monto_neto, impuesto, monto_total, estado) VALUES
  (1, 1, 'F-2026-0001', 806706, 19.00, 959980, 'EMITIDA');
