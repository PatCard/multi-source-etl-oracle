# multi-source-etl-oracle

Pipeline ETL multi-fuente que extrae datos desde CSV/Excel, MySQL, MongoDB, APIs REST y Web Scraping, los transforma y los carga en una base de datos **Oracle Database Free 23ai**, todo contenido en Docker.

---

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Requisitos](#requisitos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Fuentes de Datos](#fuentes-de-datos)
- [Base de Datos Oracle](#base-de-datos-oracle)
- [Uso](#uso)
- [Variables de Entorno](#variables-de-entorno)
- [Roadmap](#roadmap)

---

## Arquitectura

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  CSV/Excel  │  │    MySQL    │  │   MongoDB   │  │  CoinGecko  │  │  BBC Mundo  │  │mindicador.cl│
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                 │                │                │
       └────────────────┴────────────────┴─────────────────┴────────────────┴────────────────┘
                                                  │
                                         [Capa Extract]
                                         extractors/
                                                  │
                                         [Capa Transform]
                                         transformers/
                                    (limpieza, normalización,
                                     validación, tipado)
                                                  │
                                         [Capa Load]
                                         loaders/
                                       MERGE en Oracle
                                                  │
                                ┌─────────────────────────────┐
                                │     Oracle DB (Docker)      │
                                │  - stg_datos_raw            │
                                │  - productos_unificado      │
                                │  - etl_ejecuciones          │
                                │  - etl_errores              │
                                └─────────────────────────────┘
```

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Base de datos destino | Oracle Database Free 23ai |
| Base de datos fuente | MySQL 8.0 |
| Base de datos fuente | MongoDB 7.0 |
| ORM / Conexión MySQL | SQLAlchemy + PyMySQL |
| Conexión Oracle | oracledb |
| Conexión MongoDB | pymongo |
| CSV / Excel | pandas + openpyxl |
| API REST | requests |
| Web Scraping | BeautifulSoup4 + lxml |
| Logging | loguru |
| Contenedores | Docker + Docker Compose |

---

## Requisitos

- Docker >= 24.0
- Docker Compose >= 2.0
- Git

No se requiere instalar Python ni ninguna dependencia en la máquina host. Todo corre dentro de contenedores Docker.

---

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/multi-source-etl-oracle.git
cd multi-source-etl-oracle
```

### 2. Crear el archivo de variables de entorno

```bash
cp env.example .env.dev
```

Edita `.env.dev` con tus valores si es necesario. Los valores por defecto funcionan con el `docker-compose.dev.yml` sin modificaciones.

> ⚠️ **Importante:** El archivo `.env.dev` nunca debe subirse al repositorio. Está incluido en `.gitignore`.

### 3. Levantar los contenedores

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Esto levanta 4 contenedores:
- `etl_oracle` — Oracle Database Free 23ai
- `etl_mysql` — MySQL 8.0 con datos de ejemplo
- `etl_mongodb` — MongoDB 7.0 con datos de ejemplo
- `etl_python` — Contenedor Python con el pipeline ETL

### 4. Verificar que todo está corriendo

```bash
docker compose -f docker-compose.dev.yml ps
```

Todos los contenedores deben aparecer como `healthy`.

---

## Estructura del Proyecto

```
multi-source-etl-oracle/
│
├── docker-compose.dev.yml      # Entorno de desarrollo
├── docker-compose.prod.yml     # Entorno de producción (próximamente)
├── Dockerfile                  # Imagen Python ETL
├── requirements.txt            # Dependencias Python
├── env.example                 # Plantilla de variables de entorno
├── .gitignore
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuración central desde .env
│
├── extractors/                 # Capa Extract — una fuente por módulo
│   ├── __init__.py
│   ├── csv_extractor.py        # CSV y Excel con mapeo flexible
│   ├── mysql_extractor.py      # MySQL con filtros y queries
│   ├── mongo_extractor.py      # MongoDB con aggregation pipeline
│   ├── api_extractor.py        # CoinGecko API (crypto)
│   ├── scraping_extractor.py   # Web scraping BBC Mundo Economía
│   └── api_cmf_extractor.py    # Indicadores económicos Chile
│
├── transformers/               # Capa Transform
│   └── transformer.py          # Limpieza, normalización y tipado
│
├── loaders/                    # Capa Load
│   └── oracle_loader.py        # MERGE en Oracle + staging + logs
│
├── sql/
│   ├── init_oracle.sql         # Tablas Oracle (se ejecuta al iniciar)
│   ├── init_mysql.sql          # Datos de ejemplo MySQL
│   └── init_mongo.js           # Datos de ejemplo MongoDB
│
├── data/                       # Archivos CSV/Excel de prueba
│   ├── productos.csv           # Productos en español
│   └── productos_en.csv        # Productos en inglés (prueba mapeo)
│
└── orchestrator.py             # Pipeline completo
```

---

## Fuentes de Datos

### 1. CSV / Excel (`csv_extractor.py`)
Extrae datos desde archivos planos. Soporta mapeo flexible de columnas para adaptarse a distintos formatos de proveedores. Las columnas extra se conservan automáticamente.

```python
from extractors.csv_extractor import extraer_csv, MAPEO_PROVEEDOR_EN

# Formato estándar
registros = extraer_csv("data/productos.csv")

# Con mapeo para proveedor en inglés
registros = extraer_csv("data/productos_en.csv", mapeo=MAPEO_PROVEEDOR_EN)
```

### 2. MySQL (`mysql_extractor.py`)
Extrae datos desde MySQL. Soporta extracción de tablas completas, con filtros WHERE o queries SQL personalizadas.

```python
from extractors.mysql_extractor import extraer_tabla, extraer_query

# Tabla completa
registros = extraer_tabla("productos")

# Con filtro
registros = extraer_tabla("productos", filtro="stock > 50")

# Query personalizada
registros = extraer_query("SELECT * FROM productos ORDER BY precio DESC")
```

### 3. MongoDB (`mongo_extractor.py`)
Extrae documentos desde MongoDB. Soporta filtros nativos de MongoDB y pipelines de agregación.

```python
from extractors.mongo_extractor import extraer_coleccion, extraer_aggregate

# Colección completa
registros = extraer_coleccion("productos")

# Con filtro MongoDB
registros = extraer_coleccion("productos", filtro={"stock": {"$gt": 50}})

# Aggregation pipeline
pipeline = [{"$group": {"_id": "$categoria", "total": {"$sum": 1}}}]
registros = extraer_aggregate("productos", pipeline)
```

### 4. CoinGecko API (`api_extractor.py`)
Extrae precios y datos de mercado de criptomonedas en tiempo real desde la API pública de CoinGecko. No requiere API key.

```python
from extractors.api_extractor import extraer_coingecko_mercado

# Top 5 cryptos en USD
registros = extraer_coingecko_mercado(
    monedas=["bitcoin", "ethereum", "solana"],
    currency="usd"
)

# Precios en CLP (peso chileno)
registros = extraer_coingecko_mercado(currency="clp")
```

### 5. Web Scraping BBC Mundo (`scraping_extractor.py`)
Extrae noticias económicas en tiempo real desde BBC Mundo mediante web scraping con BeautifulSoup. Soporta paginación.

```python
from extractors.scraping_extractor import extraer_noticias_economia

# Extraer 2 páginas (~40 noticias)
noticias = extraer_noticias_economia(paginas=2)
```

### 6. Indicadores Económicos Chile (`api_cmf_extractor.py`)

> ⚠️ **Nota:** Actualmente este extractor usa [mindicador.cl](https://mindicador.cl) como fuente de datos, que provee los mismos indicadores oficiales del Banco Central y la CMF de Chile de forma gratuita y sin API key. En una próxima versión se migrará directamente a la [API oficial de la CMF](https://api.cmfchile.cl) con autenticación por API key.

Extrae indicadores económicos chilenos: UF, UTM, Dólar, Euro, IPC, TPM, Imacec, Bitcoin y más.

```python
from extractors.api_cmf_extractor import extraer_indicadores_hoy, extraer_indicador_historico

# Indicadores del día
indicadores = extraer_indicadores_hoy()

# Historial de un indicador
uf_2026 = extraer_indicador_historico("uf", 2026)
dolar_2026 = extraer_indicador_historico("dolar", 2026)
```

**Indicadores disponibles:**

| Código | Nombre | Unidad |
|---|---|---|
| `uf` | Unidad de Fomento | Pesos |
| `dolar` | Dólar observado | Pesos |
| `euro` | Euro | Pesos |
| `ipc` | Índice de Precios al Consumidor | Porcentaje |
| `utm` | Unidad Tributaria Mensual | Pesos |
| `tpm` | Tasa Política Monetaria | Porcentaje |
| `imacec` | Imacec | Porcentaje |
| `libra_cobre` | Libra de Cobre | Dólar |
| `tasa_desempleo` | Tasa de Desempleo | Porcentaje |
| `bitcoin` | Bitcoin | Dólar |

---

## Base de Datos Oracle

### Tablas

| Tabla | Descripción |
|---|---|
| `etl_ejecuciones` | Registro de cada ejecución del pipeline |
| `etl_errores` | Log de errores por fila durante la carga |
| `stg_datos_raw` | Staging — datos crudos antes de transformar |
| `productos_unificado` | Tabla final con datos unificados de todas las fuentes |

### Conexión desde DBeaver

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Port | `1521` |
| Database | `FREEPDB1` |
| User | `etl_user` |
| Password | `Etl123` |

---

## Uso

### Ejecutar un extractor individual

```bash
docker run --rm \
  --network multi-source-etl-oracle_etl_network \
  --env-file .env.dev \
  -v $(pwd):/app \
  -w /app \
  multi-source-etl-oracle-etl \
  python -m extractors.csv_extractor
```

### Ejecutar el pipeline completo

```bash
docker exec etl_python python orchestrator.py
```

---

## Variables de Entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `ORACLE_HOST` | Host Oracle | `oracle` |
| `ORACLE_PORT` | Puerto Oracle | `1521` |
| `ORACLE_SERVICE` | Servicio Oracle | `FREEPDB1` |
| `ORACLE_USER` | Usuario Oracle | `etl_user` |
| `ORACLE_PASSWORD` | Contraseña Oracle | — |
| `MYSQL_HOST` | Host MySQL | `mysql` |
| `MYSQL_PORT` | Puerto MySQL | `3306` |
| `MYSQL_DB` | Base de datos MySQL | `source_db` |
| `MYSQL_USER` | Usuario MySQL | `etl_reader` |
| `MYSQL_PASSWORD` | Contraseña MySQL | — |
| `MONGO_HOST` | Host MongoDB | `mongodb` |
| `MONGO_PORT` | Puerto MongoDB | `27017` |
| `MONGO_DB` | Base de datos MongoDB | `source_db` |
| `MONGO_USER` | Usuario MongoDB | `root` |
| `MONGO_PASSWORD` | Contraseña MongoDB | — |
| `ETL_BATCH_SIZE` | Tamaño del batch de carga | `100` |
| `ETL_LOG_LEVEL` | Nivel de logging | `INFO` |

---

## Roadmap

- [x] Extractor CSV/Excel con mapeo flexible
- [x] Extractor MySQL
- [x] Extractor MongoDB
- [x] Extractor API REST (CoinGecko)
- [x] Extractor Web Scraping (BBC Mundo Economía)
- [x] Extractor Indicadores Económicos Chile (mindicador.cl)
- [ ] Transformer — limpieza y normalización
- [ ] Loader Oracle con MERGE y staging
- [ ] Orchestrator — pipeline completo
- [ ] Migrar `api_cmf_extractor.py` a API oficial CMF
- [ ] Web scraping Bolsa de Santiago con Playwright
- [ ] `docker-compose.prod.yml`
- [ ] Tests unitarios

---

## Autor

Desarrollado como proyecto de portfolio para demostrar habilidades en ETL, bases de datos Oracle, Python y Docker.