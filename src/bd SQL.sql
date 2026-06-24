-- ============================================================
--  MÓDULO: SEGURIDAD Y AUDITORÍA
-- ============================================================

CREATE TABLE Rol (
    id_rol          SERIAL          PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL UNIQUE,
    descripcion     VARCHAR(200),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE Usuario (
    id_usuario      SERIAL          PRIMARY KEY,
    id_rol          INT             NOT NULL REFERENCES Rol(id_rol),
    nombre          VARCHAR(100)    NOT NULL,
    apellido        VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255)    NOT NULL,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP       NOT NULL DEFAULT NOW(),
    ultimo_login    TIMESTAMP
);

CREATE TABLE Auditoria (
    id_auditoria    SERIAL          PRIMARY KEY,
    id_usuario      INT             REFERENCES Usuario(id_usuario),
    tabla_afectada  VARCHAR(100)    NOT NULL,
    operacion       VARCHAR(10)     NOT NULL CHECK (operacion IN ('INSERT','UPDATE','DELETE','SELECT')),
    datos_anteriores JSONB,
    datos_nuevos    JSONB,
    ip_origen       INET,
    fecha_accion      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE LogAuditoriaSeguridad (
    id_log          SERIAL          PRIMARY KEY,
    id_usuario      INT             REFERENCES Usuario(id_usuario),
    id_aprobador    INT             REFERENCES Usuario(id_usuario),
    evento          VARCHAR(100)    NOT NULL,
    descripcion     TEXT,
    ip_origen       INET,
    exitoso         BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_accion    TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE SolicitudEliminacion (
    id_solicitud    SERIAL          PRIMARY KEY,
    id_usuario      INT             NOT NULL REFERENCES Usuario(id_usuario),
    tabla_objetivo  VARCHAR(100)    NOT NULL,
    id_registro     INT             NOT NULL,
    motivo          TEXT            NOT NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'PENDIENTE'
                        CHECK (estado IN ('PENDIENTE','APROBADA','RECHAZADA')),
    id_aprobador    INT             REFERENCES Usuario(id_usuario),
    fecha_solicitud TIMESTAMP       NOT NULL DEFAULT NOW(),
    fecha_resolucion TIMESTAMP
);

-- ============================================================
--  MÓDULO: CLIENTES
-- ============================================================

CREATE TABLE Direccion (
    id_direccion    SERIAL          PRIMARY KEY,
    calle           VARCHAR(200)    NOT NULL,
    numero          VARCHAR(20),
    ciudad          VARCHAR(100)    NOT NULL,
    region          VARCHAR(100),
    pais            VARCHAR(100)    NOT NULL DEFAULT 'Chile',
    codigo_postal   VARCHAR(20),
    tipo            VARCHAR(20)     NOT NULL DEFAULT 'ENVIO'
                        CHECK (tipo IN ('ENVIO','FACTURACION','PRINCIPAL'))
);

CREATE TABLE Cliente (
    id_cliente      SERIAL          PRIMARY KEY,
    id_direccion    INT             REFERENCES Direccion(id_direccion),
    nombre          VARCHAR(100)    NOT NULL,
    apellido        VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    telefono        VARCHAR(20),
    rut             VARCHAR(20)     UNIQUE,
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_registro  TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
--  MÓDULO: PROVEEDORES
-- ============================================================

CREATE TABLE Proveedor (
    id_proveedor    SERIAL          PRIMARY KEY,
    id_direccion    INT             REFERENCES Direccion(id_direccion),
    nombre          VARCHAR(150)    NOT NULL,
    rut             VARCHAR(20)     UNIQUE,
    email           VARCHAR(150),
    telefono        VARCHAR(20),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_registro  TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE PagoProveedor (
    id_pago         SERIAL          PRIMARY KEY,
    id_proveedor    INT             NOT NULL REFERENCES Proveedor(id_proveedor),
    monto           NUMERIC(12,2)   NOT NULL CHECK (monto > 0),
    metodo_pago     VARCHAR(50)     NOT NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'PENDIENTE'
                        CHECK (estado IN ('PENDIENTE','PAGADO','ANULADO')),
    referencia      VARCHAR(100),
    fecha_pago      DATE,
    fecha_creacion  TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
--  MÓDULO: INVENTARIO
-- ============================================================

CREATE TABLE Producto (
    id_producto     SERIAL          PRIMARY KEY,
    id_proveedor    INT             REFERENCES Proveedor(id_proveedor),
    nombre          VARCHAR(150)    NOT NULL,
    descripcion     TEXT,
    precio_unitario NUMERIC(10,2)   NOT NULL CHECK (precio_unitario >= 0),
    stock           INT             NOT NULL DEFAULT 0 CHECK (stock >= 0),
    activo          BOOLEAN         NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
--  MÓDULO: PEDIDOS Y FACTURACIÓN
-- ============================================================

CREATE TABLE Pedido (
    id_pedido       SERIAL          PRIMARY KEY,
    id_cliente      INT             NOT NULL REFERENCES Cliente(id_cliente),
    id_usuario      INT             REFERENCES Usuario(id_usuario),
    estado          VARCHAR(20)     NOT NULL DEFAULT 'PENDIENTE'
                        CHECK (estado IN ('PENDIENTE','CONFIRMADO','ENVIADO','ENTREGADO','CANCELADO')),
    fecha_pedido    TIMESTAMP       NOT NULL DEFAULT NOW(),
    fecha_entrega   DATE,
    total           NUMERIC(12,2)   NOT NULL DEFAULT 0 CHECK (total >= 0),
    observaciones   TEXT
);

CREATE TABLE DetallePedido (
    id_detalle      SERIAL          PRIMARY KEY,
    id_pedido       INT             NOT NULL REFERENCES Pedido(id_pedido) ON DELETE CASCADE,
    id_producto     INT             NOT NULL REFERENCES Producto(id_producto),
    cantidad        INT             NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2)   NOT NULL CHECK (precio_unitario >= 0),
    descuento       NUMERIC(5,2)    DEFAULT 0,
    subtotal        NUMERIC(12,2)   GENERATED ALWAYS AS
                        (cantidad * precio_unitario * (1 - descuento / 100)) STORED,
    UNIQUE (id_pedido, id_producto)
);

CREATE TABLE Factura (
    id_factura      SERIAL          PRIMARY KEY,
    id_pedido       INT             NOT NULL UNIQUE REFERENCES Pedido(id_pedido),
    id_cliente      INT             NOT NULL REFERENCES Cliente(id_cliente),
    numero_factura  VARCHAR(50)     NOT NULL UNIQUE,
    fecha_emision   TIMESTAMP       NOT NULL DEFAULT NOW(),
    monto_neto      NUMERIC(12,2)   NOT NULL CHECK (monto_neto >= 0),
    impuesto        NUMERIC(5,2)    NOT NULL DEFAULT 19.00,
    monto_total     NUMERIC(12,2)   NOT NULL CHECK (monto_total >= 0),
    estado          VARCHAR(20)     NOT NULL DEFAULT 'EMITIDA'
                        CHECK (estado IN ('EMITIDA','PAGADA','ANULADA')),
);

-- ============================================================
--  ÍNDICES
-- ============================================================

CREATE INDEX idx_usuario_rol         ON Usuario(id_rol);
CREATE INDEX idx_cliente_email       ON Cliente(email);
CREATE INDEX idx_pedido_cliente      ON Pedido(id_cliente);
CREATE INDEX idx_pedido_estado       ON Pedido(estado);
CREATE INDEX idx_detalle_pedido      ON DetallePedido(id_pedido);
CREATE INDEX idx_detalle_producto    ON DetallePedido(id_producto);
CREATE INDEX idx_auditoria_usuario   ON Auditoria(id_usuario);
CREATE INDEX idx_auditoria_fecha     ON Auditoria(fecha_hora);
CREATE INDEX idx_log_usuario         ON LogAuditoriaSeguridad(id_usuario);
CREATE INDEX idx_producto_proveedor  ON Producto(id_proveedor);
CREATE INDEX idx_pago_proveedor      ON PagoProveedor(id_proveedor);
CREATE INDEX idx_factura_cliente     ON Factura(id_cliente);

-- ============================================================
--  COMENTARIOS DE TABLAS
-- ============================================================

COMMENT ON TABLE Rol                    IS 'Roles del sistema para control de acceso';
COMMENT ON TABLE Usuario                IS 'Usuarios del sistema con autenticación';
COMMENT ON TABLE Auditoria              IS 'Registro de cambios en tablas del sistema';
COMMENT ON TABLE LogAuditoriaSeguridad  IS 'Eventos de seguridad: logins, intentos fallidos, etc.';
COMMENT ON TABLE SolicitudEliminacion   IS 'Solicitudes de eliminación de registros con flujo de aprobación';
COMMENT ON TABLE Direccion              IS 'Direcciones reutilizables para clientes y proveedores';
COMMENT ON TABLE Cliente                IS 'Clientes que realizan pedidos';
COMMENT ON TABLE Proveedor              IS 'Proveedores de productos';
COMMENT ON TABLE PagoProveedor          IS 'Pagos realizados a proveedores';
COMMENT ON TABLE Producto               IS 'Catálogo de productos con stock';
COMMENT ON TABLE Pedido                 IS 'Pedidos realizados por clientes';
COMMENT ON TABLE DetallePedido          IS 'Líneas de detalle de cada pedido';
COMMENT ON TABLE Factura                IS 'Facturas generadas a partir de pedidos';