"""
multi-source-etl-oracle
Extractor de API REST.
Ejemplo con CoinGecko (precios crypto, sin API key).
Diseño genérico reutilizable para cualquier API REST.
"""

import requests
from loguru import logger
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from config.settings import API

# ─────────────────────────────────────────
# Configuración CoinGecko
# ─────────────────────────────────────────
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "multi-source-etl-oracle/1.0"
}


def extraer_api(url: str, params: dict = None, mapeo: dict = None,
                fuente: str = "api", ruta_datos: str = None) -> list[dict]:
    """
    Extractor genérico para cualquier API REST que retorne JSON.

    Args:
        url:         URL del endpoint
        params:      Query params (ej: {"vs_currency": "usd"})
        mapeo:       Diccionario {campo_origen: campo_destino}
        fuente:      Nombre descriptivo del origen
        ruta_datos:  Si el JSON tiene los datos anidados (ej: "data.items")
    """
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Navegar ruta anidada si se especifica
        if ruta_datos:
            for key in ruta_datos.split("."):
                data = data[key]

        # Si viene un dict en vez de lista, envolverlo
        if isinstance(data, dict):
            data = [data]

        logger.info(f"API leída: {fuente} — {len(data)} registros, status: {response.status_code}")

        return _normalizar(data, fuente=fuente, mapeo=mapeo)

    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con API: {url}")
        return []
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error HTTP en API {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error extrayendo desde API ({fuente}): {e}")
        return []


def extraer_coingecko_mercado(monedas: list[str] = None, currency: str = "usd") -> list[dict]:
    """
    Extrae precios y datos de mercado de CoinGecko.

    Args:
        monedas:  Lista de IDs de monedas (ej: ["bitcoin", "ethereum"])
                  Si es None trae el top 20 por market cap
        currency: Moneda de referencia (usd, eur, clp, etc.)
    """
    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }

    if monedas:
        params["ids"] = ",".join(monedas)

    return extraer_api(
        url=f"{COINGECKO_BASE_URL}/coins/markets",
        params=params,
        fuente=f"api:coingecko:mercado:{currency}",
        mapeo={
            "id":                    "codigo",
            "name":                  "nombre",
            "symbol":                "simbolo",
            "current_price":         "precio_actual",
            "market_cap":            "market_cap",
            "price_change_24h":      "cambio_24h",
            "price_change_percentage_24h": "cambio_pct_24h",
            "total_volume":          "volumen_total",
            "last_updated":          "ultima_actualizacion",
        }
    )


def extraer_coingecko_detalle(moneda_id: str) -> list[dict]:
    """
    Extrae el detalle completo de una moneda específica.

    Args:
        moneda_id: ID de la moneda en CoinGecko (ej: "bitcoin")
    """
    return extraer_api(
        url=f"{COINGECKO_BASE_URL}/coins/{moneda_id}",
        fuente=f"api:coingecko:detalle:{moneda_id}",
        mapeo={
            "id":     "codigo",
            "name":   "nombre",
            "symbol": "simbolo",
        }
    )


def _normalizar(data: list[dict], fuente: str, mapeo: dict = None) -> list[dict]:
    """
    Normaliza registros de API:
    - Aplica mapeo de campos si existe
    - Conserva todos los campos extra
    - Agrega campo fuente
    """
    registros = []
    for item in data:
        if mapeo:
            nuevo = {}
            for k, v in item.items():
                nuevo[mapeo.get(k, k)] = v
            item = nuevo

        item["fuente"] = fuente
        registros.append(item)

    if registros and mapeo:
        campos_extra = [k for k in registros[0].keys()
                       if k not in set(mapeo.values()) | {"fuente"}]
        if campos_extra:
            logger.info(f"Campos extra conservados desde {fuente}: {campos_extra}")

    logger.info(f"Extracción completada desde {fuente}: {len(registros)} registros")
    return registros


if __name__ == "__main__":
    # Prueba top 5 cryptos por market cap
    logger.info("=== Prueba top 5 cryptos (USD) ===")
    registros = extraer_coingecko_mercado(
        monedas=["bitcoin", "ethereum", "tether", "binancecoin", "solana"],
        currency="usd"
    )
    for r in registros:
        print(f"{r.get('nombre'):<20} ${r.get('precio_actual'):>12,.2f} | cambio 24h: {r.get('cambio_pct_24h'):>6.2f}%")

    # Prueba con precios en CLP (peso chileno)
    logger.info("=== Prueba top 3 cryptos (CLP) ===")
    registros_clp = extraer_coingecko_mercado(
        monedas=["bitcoin", "ethereum", "solana"],
        currency="clp"
    )
    for r in registros_clp:
        print(f"{r.get('nombre'):<20} ${r.get('precio_actual'):>15,.0f} CLP")