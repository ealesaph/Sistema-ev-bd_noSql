// =========================================================
// Inserciones de datos de ejemplo - ComercioTech (MongoDB)
// Ejecutar dentro del contenedor:
//   mongosh comerciotech inserciones_mongo.js
// (si la autenticación está activada, usar:
//   mongosh "mongodb://app_comerciotech:OtraClaveSegura456!@localhost:27017/comerciotech" inserciones_mongo.js )
// =========================================================

// Limpieza opcional para pruebas repetibles
db.productos.deleteMany({});
db.carritos.deleteMany({});

// 1) Productos (esquema oficial: precio_base, stock_actual, atributos_variables)
const productos = [
  {
    nombre: "Laptop Lenovo ThinkPad X1",
    descripcion: "Ultrabook empresarial de 14 pulgadas",
    precio_base: 899990,
    categoria: "laptops",
    atributos_variables: {
      ram_gb: 16,
      procesador: "Intel i7-13700H",
      almacenamiento_gb: 512,
      tipo_pantalla: "IPS 14 pulgadas"
    },
    proveedor_id: 1,
    stock_actual: 35,
    valoraciones: [],
    fecha_creacion: new Date(),
    fecha_actualizacion: new Date()
  },
  {
    nombre: "Mouse Logitech MX Master 3",
    descripcion: "Mouse inalámbrico ergonómico",
    precio_base: 59990,
    categoria: "perifericos",
    atributos_variables: {
      conectividad: "Bluetooth / USB receptor",
      dpi: 4000,
      color: "Grafito"
    },
    proveedor_id: 1,
    stock_actual: 120,
    valoraciones: [],
    fecha_creacion: new Date(),
    fecha_actualizacion: new Date()
  },
  {
    nombre: "Teclado Mecánico Redragon K552",
    descripcion: "Switch rojo, retroiluminado",
    precio_base: 39990,
    categoria: "perifericos",
    atributos_variables: {
      tipo_switch: "Rojo (lineal)",
      retroiluminacion: "RGB",
      formato: "TKL"
    },
    proveedor_id: 2,
    stock_actual: 80,
    valoraciones: [],
    fecha_creacion: new Date(),
    fecha_actualizacion: new Date()
  }
];

const resultadoInsercion = db.productos.insertMany(productos);
print("Productos insertados:", JSON.stringify(resultadoInsercion.insertedIds));

// IDs de los productos recién creados, para armar el carrito de ejemplo
const idLaptop = resultadoInsercion.insertedIds[0];
const idMouse = resultadoInsercion.insertedIds[1];

// 2) Carrito de ejemplo (esquema oficial: cliente_id, items, total)
db.carritos.insertOne({
  cliente_id: 1, // debe corresponder a un id_cliente existente en PostgreSQL
  items: [
    {
      producto_id: idLaptop.toString(),
      nombre: "Laptop Lenovo ThinkPad X1",
      cantidad: 1,
      precio_unitario: 899990,
      fecha_agregado: new Date()
    },
    {
      producto_id: idMouse.toString(),
      nombre: "Mouse Logitech MX Master 3",
      cantidad: 2,
      precio_unitario: 59990,
      fecha_agregado: new Date()
    }
  ],
  total: 899990 + 2 * 59990,
  estado: "activo",
  fecha_creacion: new Date(),
  fecha_actualizacion: new Date()
});

// 3) Índices recomendados para cumplir <50ms de lectura sobre el catálogo
db.productos.createIndex({ categoria: 1 });
db.productos.createIndex({ nombre: "text", descripcion: "text" });
db.carritos.createIndex({ cliente_id: 1, estado: 1 });

print("Inserción de datos de ejemplo completada.");
