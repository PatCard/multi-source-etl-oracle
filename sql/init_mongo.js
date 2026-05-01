// =============================================
// multi-source-etl-oracle
// Inicialización de datos de ejemplo en MongoDB
// =============================================
 
db = db.getSiblingDB("source_db");
 
db.productos.insertMany([
  { codigo: "MDB-001", nombre: "Silla Ergonómica",   categoria: "Mobiliario",   precio: 249.99, stock: 25 },
  { codigo: "MDB-002", nombre: "Escritorio Ajustable",categoria: "Mobiliario",   precio: 399.99, stock: 15 },
  { codigo: "MDB-003", nombre: "Lámpara LED",         categoria: "Iluminación",  precio:  49.99, stock: 100 },
  { codigo: "MDB-004", nombre: "Webcam HD",            categoria: "Periféricos",  precio:  79.99, stock: 60 },
  { codigo: "MDB-005", nombre: "Hub USB-C",            categoria: "Periféricos",  precio:  39.99, stock: 90 }
]);
 