## no es la CMF

"""
multi-source-etl-oracle
Extractor de Indicadores Económicos Chile — mindicador.cl
Obtiene UF, UTM, Dólar, Euro, IPC, Bitcoin y más sin API key.
Fuente oficial basada en datos del Banco Central y CMF Chile.
"""

import requests
from datetime import datetime
from loguru import logger
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "https://mindicador.cl/api"
HEADERS = {"Accept": "application/json"}

# Indicadores disponibles
INDICADORES = [
    "uf", "ivp", "dolar", "dolar_intercambio", "euro",
    "ipc", "utm", "imacec", "tpm", "libra_cobre",
    "tasa_desempleo", "bitcoin"
]


def extraer_indicadores_hoy() -> list[dict]:
    """
    Extrae todos los indicadores económicos del día actual.
    """
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        fecha_consulta = data.get("fecha", datetime.now().isoformat())
        registros = []

        for codigo in INDICADORES:
            if codigo not in data:
                continue

            ind = data[codigo]
            registros.append({
                "codigo":          ind.get("codigo", codigo),
                "nombre":          ind.get("nombre", codigo),
                "valor":           ind.get("valor"),
                "unidad_medida":   ind.get("unidad_medida", ""),
                "fecha_valor":     ind.get("fecha", ""),
                "fecha_consulta":  fecha_consulta,
                "fuente":          "api:mindicador.cl"
            })

        logger.info(f"Indicadores económicos extraídos: {len(registros)}")
        return registros

    except Exception as e:
        logger.error(f"Error extrayendo indicadores económicos: {e}")
        return []


def extraer_indicador_historico(codigo: str, anio: int = None) -> list[dict]:
    """
    Extrae el historial de un indicador específico.

    Args:
        codigo: Código del indicador (ej: 'uf', 'dolar', 'ipc')
        anio:   Año a consultar. Si es None trae el último año disponible.
    """
    url = f"{BASE_URL}/{codigo}"
    if anio:
        url += f"/{anio}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        nombre = data.get("nombre", codigo)
        unidad = data.get("unidad_medida", "")
        serie = data.get("serie", [])

        registros = []
        for item in serie:
            registros.append({
                "codigo":        codigo,
                "nombre":        nombre,
                "valor":         item.get("valor"),
                "unidad_medida": unidad,
                "fecha_valor":   item.get("fecha", ""),
                "fuente":        f"api:mindicador.cl:{codigo}"
            })

        logger.info(f"Historial {codigo} ({anio or 'reciente'}): {len(registros)} registros")
        return registros

    except Exception as e:
        logger.error(f"Error extrayendo historial de {codigo}: {e}")
        return []


if __name__ == "__main__":
    # Indicadores del día
    logger.info("=== Indicadores económicos Chile — Hoy ===")
    indicadores = extraer_indicadores_hoy()

    print(f"\n{'Indicador':<35} {'Valor':>15} {'Unidad':<10}")
    print("-" * 65)
    for i in indicadores:
        valor = f"{i['valor']:,.2f}" if i['valor'] else "N/A"
        print(f"{i['nombre']:<35} {valor:>15} {i['unidad_medida']:<10}")

    # Historial UF último año
    logger.info("\n=== Historial UF 2025 ===")
    uf_hist = extraer_indicador_historico("uf", 2025)
    print(f"\nUF 2025 — {len(uf_hist)} registros")
    for r in uf_hist[:5]:
        print(f"  {r['fecha_valor'][:10]}  ${r['valor']:,.2f}")
    print("  ...")

    # Historial Dólar
    logger.info("\n=== Historial Dólar 2025 ===")
    dolar_hist = extraer_indicador_historico("dolar", 2025)
    print(f"\nDólar 2025 — {len(dolar_hist)} registros")
    for r in dolar_hist[:5]:
        print(f"  {r['fecha_valor'][:10]}  ${r['valor']:,.2f}")