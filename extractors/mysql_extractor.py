"""
multi-source-etl-oracle
Extractor de MySQL.
Lee tablas o queries desde MySQL y retorna una lista de diccionarios normalizada.
"""

from sqlalchemy import create_engine, text
from loguru import logger
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import MYSQL_URL


def extraer_tabla(tabla: str, mapeo: dict = None, filtro: str = None) -> list[dict]:
    """
    Extrae todos los registros de una tabla MySQL.

    Args:
        tabla:  Nombre de la tabla a extraer
        mapeo:  Diccionario {columna_origen: columna_destino}
        filtro: Condición WHERE opcional (ej: "stock > 0")
    """
    query = f"SELECT * FROM {tabla}"
    if filtro:
        query += f" WHERE {filtro}"

    return _ejecutar_query(query, fuente=f"mysql:{tabla}", mapeo=mapeo)


def extraer_query(query: str, fuente: str = "mysql:custom", mapeo: dict = None) -> list[dict]:
    """
    Extrae registros desde una query SQL personalizada.

    Args:
        query:  Query SQL a ejecutar
        fuente: Nombre descriptivo para identificar el origen
        mapeo:  Diccionario {columna_origen: columna_destino}
    """
    return _ejecutar_query(query, fuente=fuente, mapeo=mapeo)


def _ejecutar_query(query: str, fuente: str, mapeo: dict = None) -> list[dict]:
    """
    Ejecuta una query y retorna los resultados normalizados.
    """
    try:
        engine = create_engine(MYSQL_URL)
        with engine.connect() as conn:
            resultado = conn.execute(text(query))
            columnas = list(resultado.keys())
            filas = resultado.fetchall()

        logger.info(f"MySQL leído: {fuente} — {len(filas)} filas, columnas: {columnas}")

        # Convertir a lista de dicts
        registros = [dict(zip(columnas, fila)) for fila in filas]

        # Aplicar mapeo si existe
        if mapeo:
            registros = _aplicar_mapeo(registros, mapeo, fuente)

        # Agregar fuente
        for r in registros:
            r["fuente"] = fuente

        logger.info(f"Extracción completada desde {fuente}: {len(registros)} registros")
        return registros

    except Exception as e:
        logger.error(f"Error extrayendo desde MySQL ({fuente}): {e}")
        return []


def _aplicar_mapeo(registros: list[dict], mapeo: dict, fuente: str) -> list[dict]:
    """
    Renombra las claves de cada registro según el mapeo.
    Conserva las claves que no están en el mapeo.
    """
    columnas_no_mapeadas = set(mapeo.keys()) - set(registros[0].keys()) if registros else set()
    if columnas_no_mapeadas:
        logger.warning(f"Columnas del mapeo no encontradas en {fuente}: {columnas_no_mapeadas}")

    resultado = []
    for registro in registros:
        nuevo = {}
        for k, v in registro.items():
            nuevo[mapeo.get(k, k)] = v  # renombra si está en mapeo, si no conserva
        resultado.append(nuevo)
    return resultado


if __name__ == "__main__":
    # Prueba extracción de tabla completa
    logger.info("=== Prueba extracción tabla completa ===")
    registros = extraer_tabla("productos")
    for r in registros:
        print(r)

    # Prueba con filtro
    logger.info("=== Prueba con filtro stock > 50 ===")
    registros_filtrados = extraer_tabla("productos", filtro="stock > 50")
    for r in registros_filtrados:
        print(r)

    # Prueba con query personalizada
    logger.info("=== Prueba con query personalizada ===")
    registros_query = extraer_query(
        "SELECT codigo, nombre, precio FROM productos ORDER BY precio DESC",
        fuente="mysql:productos_precio"
    )
    for r in registros_query:
        print(r)