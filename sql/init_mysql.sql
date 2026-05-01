-- =============================================
-- multi-source-etl-oracle
-- Inicialización de datos de ejemplo en MySQL
-- =============================================

USE source_db;

CREATE TABLE productos (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    codigo    VARCHAR(100) UNIQUE NOT NULL,
    nombre    VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    precio    DECIMAL(12,2),
    stock     INT DEFAULT 0,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO productos (codigo, nombre, categoria, precio, stock) VALUES
('MSQ-001', 'Laptop Pro 15',       'Electrónica',  1299.99, 45),
('MSQ-002', 'Mouse Inalámbrico',   'Periféricos',    29.99, 200),
('MSQ-003', 'Teclado Mecánico',    'Periféricos',    89.99, 150),
('MSQ-004', 'Monitor 27 pulgadas', 'Electrónica',   399.99, 30),
('MSQ-005', 'Auriculares BT',      'Audio',          59.99, 80);