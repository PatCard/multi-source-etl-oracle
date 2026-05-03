"""
multi-source-etl-oracle
Extractor de MongoDB.
Lee colecciones o queries desde MongoDB y retorna una lista de diccionarios normalizada.
"""

from pymongo import MongoClient
from loguru import logger
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import MONGO, MONGO_URL


def extraer_coleccion(coleccion: str, filtro: dict = None, mapeo: dict = None, limite: int = None) -> list[dict]:
    """
    Extrae documentos de una colección MongoDB.

    Args:
        coleccion: Nombre de la colección
        filtro:    Filtro MongoDB (ej: {"stock": {"$gt": 50}})
        mapeo:     Diccionario {campo_origen: campo_destino}
        limite:    Número máximo de documentos a extraer
    """
    try:
        client = MongoClient(MONGO_URL)
        db = client[MONGO["database"]]
        col = db[coleccion]

        query = filtro or {}
        cursor = col.find(query)
        if limite:
            cursor = cursor.limit(limite)

        documentos = list(cursor)
        client.close()

        logger.info(f"MongoDB leído: {coleccion} — {len(documentos)} documentos")

        # Normalizar
        registros = _normalizar(documentos, fuente=f"mongo:{coleccion}", mapeo=mapeo)
        return registros

    except Exception as e:
        logger.error(f"Error extrayendo desde MongoDB ({coleccion}): {e}")
        return []


def extraer_aggregate(coleccion: str, pipeline: list, fuente: str = None, mapeo: dict = None) -> list[dict]:
    """
    Extrae documentos usando un pipeline de agregación MongoDB.

    Args:
        coleccion: Nombre de la colección
        pipeline:  Pipeline de agregación MongoDB
        fuente:    Nombre descriptivo del origen
        mapeo:     Diccionario {campo_origen: campo_destino}
    """
    fuente = fuente or f"mongo:{coleccion}:aggregate"
    try:
        client = MongoClient(MONGO_URL)
        db = client[MONGO["database"]]
        col = db[coleccion]

        documentos = list(col.aggregate(pipeline))
        client.close()

        logger.info(f"MongoDB aggregate: {fuente} — {len(documentos)} documentos")
        return _normalizar(documentos, fuente=fuente, mapeo=mapeo)

    except Exception as e:
        logger.error(f"Error en aggregate MongoDB ({fuente}): {e}")
        return []


def _normalizar(documentos: list[dict], fuente: str, mapeo: dict = None) -> list[dict]:
    """
    Normaliza los documentos MongoDB:
    - Elimina el campo _id de MongoDB
    - Aplica mapeo de campos si existe
    - Conserva todos los campos extra
    - Agrega campo fuente
    """
    registros = []
    for doc in documentos:
        # Eliminar _id de MongoDB (no serializable en Oracle)
        doc.pop("_id", None)

        # Aplicar mapeo si existe
        if mapeo:
            nuevo = {}
            for k, v in doc.items():
                nuevo[mapeo.get(k, k)] = v
            doc = nuevo

        doc["fuente"] = fuente
        registros.append(doc)

    # Columnas extra detectadas
    if registros:
        campos_extra = [k for k in registros[0].keys() if k not in {"codigo", "nombre", "categoria", "precio", "stock", "fuente"}]
        if campos_extra:
            logger.info(f"Campos extra conservados desde {fuente}: {campos_extra}")

    logger.info(f"Extracción completada desde {fuente}: {len(registros)} registros")
    return registros


if __name__ == "__main__":
    # Prueba extracción colección completa
    logger.info("=== Prueba extracción colección completa ===")
    registros = extraer_coleccion("productos")
    for r in registros:
        print(r)

    # Prueba con filtro MongoDB
    logger.info("=== Prueba con filtro stock > 50 ===")
    registros_filtrados = extraer_coleccion(
        "productos",
        filtro={"stock": {"$gt": 50}}
    )
    for r in registros_filtrados:
        print(r)

    # Prueba con pipeline de agregación
    logger.info("=== Prueba con aggregate por categoría ===")
    pipeline = [
        {"$group": {
            "_id": "$categoria",
            "total_productos": {"$sum": 1},
            "stock_total": {"$sum": "$stock"},
            "precio_promedio": {"$avg": "$precio"}
        }},
        {"$sort": {"stock_total": -1}}
    ]
    registros_agg = extraer_aggregate("productos", pipeline, fuente="mongo:productos:por_categoria")
    for r in registros_agg:
        print(r)