"""
multi-source-etl-oracle
Extractor de archivos CSV y Excel con mapeo flexible de columnas.
Conserva todas las columnas del archivo fuente, mapeando las requeridas
y manteniendo cualquier columna extra automáticamente.
"""

import pandas as pd
from pathlib import Path
from loguru import logger


# Columnas mínimas requeridas en el formato interno
COLUMNAS_REQUERIDAS = {"codigo", "nombre", "categoria", "precio", "stock"}

# Mapeo por defecto
MAPEO_DEFAULT = {
    "codigo":    "codigo",
    "nombre":    "nombre",
    "categoria": "categoria",
    "precio":    "precio",
    "stock":     "stock",
}

# Mapeo para CSVs en inglés
MAPEO_PROVEEDOR_EN = {
    "product_code": "codigo",
    "product_name": "nombre",
    "category":     "categoria",
    "price":        "precio",
    "quantity":     "stock",
}

# Mapeo para CSVs abreviados
MAPEO_PROVEEDOR_ABREV = {
    "cod":  "codigo",
    "nom":  "nombre",
    "cat":  "categoria",
    "pre":  "precio",
    "qty":  "stock",
}


def extraer_csv(filepath: str, mapeo: dict = None) -> list[dict]:
    path = Path(filepath)

    if not path.exists():
        logger.error(f"Archivo no encontrado: {filepath}")
        return []

    if path.suffix.lower() != ".csv":
        logger.error(f"El archivo no es un CSV: {filepath}")
        return []

    try:
        df = pd.read_csv(path)
        logger.info(f"CSV leído: {path.name} — {len(df)} filas, columnas: {list(df.columns)}")
        return _normalizar(df, fuente=f"csv:{path.name}", mapeo=mapeo or MAPEO_DEFAULT)
    except Exception as e:
        logger.error(f"Error leyendo CSV {filepath}: {e}")
        return []


def extraer_excel(filepath: str, hoja: str = 0, mapeo: dict = None) -> list[dict]:
    path = Path(filepath)

    if not path.exists():
        logger.error(f"Archivo no encontrado: {filepath}")
        return []

    if path.suffix.lower() not in (".xlsx", ".xls"):
        logger.error(f"El archivo no es un Excel: {filepath}")
        return []

    try:
        df = pd.read_excel(path, sheet_name=hoja)
        logger.info(f"Excel leído: {path.name} hoja={hoja} — {len(df)} filas, columnas: {list(df.columns)}")
        return _normalizar(df, fuente=f"excel:{path.name}", mapeo=mapeo or MAPEO_DEFAULT)
    except Exception as e:
        logger.error(f"Error leyendo Excel {filepath}: {e}")
        return []


def _normalizar(df: pd.DataFrame, fuente: str, mapeo: dict) -> list[dict]:
    """
    Normaliza el DataFrame:
    - Convierte columnas a minúsculas
    - Aplica mapeo solo en columnas que necesitan renombrarse
    - Conserva todas las columnas extra automáticamente
    - Valida que las columnas requeridas estén presentes
    - Limpia valores nulos
    - Agrega campo fuente
    """
    # Columnas a minúsculas y sin espacios
    df.columns = df.columns.str.strip().str.lower()

    # Detectar columnas del mapeo que no existen en el archivo
    columnas_no_mapeadas = set(mapeo.keys()) - set(df.columns)
    if columnas_no_mapeadas:
        logger.warning(f"Columnas del mapeo no encontradas en {fuente}: {columnas_no_mapeadas}")

    # Aplicar mapeo solo en columnas existentes
    mapeo_aplicable = {k: v for k, v in mapeo.items() if k in df.columns}
    df = df.rename(columns=mapeo_aplicable)

    # Validar columnas requeridas tras el mapeo
    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        logger.warning(f"Columnas requeridas faltantes en {fuente}: {faltantes}")

    # Columnas extra (todo lo que no es requerido ni fuente)
    columnas_extra = [c for c in df.columns if c not in COLUMNAS_REQUERIDAS]
    if columnas_extra:
        logger.info(f"Columnas extra conservadas desde {fuente}: {columnas_extra}")

    # Limpiar nulos
    df = df.where(pd.notnull(df), None)

    # Agregar fuente
    df["fuente"] = fuente

    registros = df.to_dict(orient="records")
    logger.info(f"Extracción completada desde {fuente}: {len(registros)} registros, {len(df.columns)} columnas")
    return registros


if __name__ == "__main__":
    logger.info("=== Prueba CSV formato estándar (con columnas extra) ===")
    registros = extraer_csv("data/productos.csv")
    for r in registros:
        print(r)

    logger.info("=== Prueba CSV con mapeo en inglés ===")
    registros_en = extraer_csv("data/productos_en.csv", mapeo=MAPEO_PROVEEDOR_EN)
    for r in registros_en:
        print(r)