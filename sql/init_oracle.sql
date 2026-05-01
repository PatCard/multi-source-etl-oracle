-- =============================================
-- multi-source-etl-oracle
-- Inicialización de tablas en Oracle
-- =============================================

-- Se ejecuta con usuario SYSTEM en FREEPDB1

-- Registro de cada ejecución del ETL
CREATE TABLE etl_user.etl_ejecuciones (
    id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fuente         VARCHAR2(50),
    fecha_inicio   TIMESTAMP,
    fecha_fin      TIMESTAMP,
    registros_ok   NUMBER DEFAULT 0,
    registros_err  NUMBER DEFAULT 0,
    estado         VARCHAR2(20)
);

-- Log de errores por fila
CREATE TABLE etl_user.etl_errores (
    id            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ejecucion_id  NUMBER REFERENCES etl_user.etl_ejecuciones(id),
    fila_raw      VARCHAR2(4000),
    mensaje_error VARCHAR2(1000),
    fecha         TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Staging: datos crudos antes de transformar
CREATE TABLE etl_user.stg_datos_raw (
    id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fuente    VARCHAR2(50),
    payload   CLOB,
    procesado CHAR(1) DEFAULT 'N',
    fecha     TIMESTAMP DEFAULT SYSTIMESTAMP
);

-- Tabla final unificada de productos
CREATE TABLE etl_user.productos_unificado (
    id           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo       VARCHAR2(100) UNIQUE,
    nombre       VARCHAR2(255),
    categoria    VARCHAR2(100),
    precio       NUMBER(12,2),
    stock        NUMBER,
    fuente       VARCHAR2(50),
    fecha_carga  TIMESTAMP DEFAULT SYSTIMESTAMP,
    fecha_update TIMESTAMP
);

-- Índices para mejorar rendimiento
CREATE INDEX etl_user.idx_productos_categoria ON etl_user.productos_unificado(categoria);
CREATE INDEX etl_user.idx_stg_fuente ON etl_user.stg_datos_raw(fuente, procesado);
CREATE INDEX etl_user.idx_etl_ejecuciones_fuente ON etl_user.etl_ejecuciones(fuente, estado);