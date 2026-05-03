"""
multi-source-etl-oracle
Extractor Web Scraping — BBC Mundo Economía
Extrae noticias económicas desde bbc.com/mundo
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "https://www.bbc.com"
URL_ECONOMIA = f"{BASE_URL}/mundo/topics/c06gq9v4xp3t"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-CL,es;q=0.9",
}


def extraer_noticias_economia(paginas: int = 1) -> list[dict]:
    """
    Extrae noticias económicas desde BBC Mundo.

    Args:
        paginas: Número de páginas a extraer (cada página ~20 noticias)
    """
    todas = []

    for pagina in range(1, paginas + 1):
        url = URL_ECONOMIA if pagina == 1 else f"{URL_ECONOMIA}?page={pagina}"
        registros = _extraer_pagina(url, pagina)
        todas.extend(registros)

        if len(registros) == 0:
            logger.info(f"No hay más noticias en página {pagina}, deteniendo.")
            break

    logger.info(f"Total noticias extraídas: {len(todas)}")
    return todas


def _extraer_pagina(url: str, pagina: int) -> list[dict]:
    """
    Extrae noticias de una página específica.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Las noticias están en el grid principal
        grid = soup.find(attrs={"data-testid": "curation-grid-normal"})
        promos = soup.find(attrs={"data-testid": "topic-promos"})

        registros = []

        for contenedor in [grid, promos]:
            if not contenedor:
                continue

            links = contenedor.find_all("a", href=True)
            for a in links:
                titulo = a.get_text(strip=True)
                href = a["href"]

                # Filtrar solo artículos reales
                if not titulo or "/mundo/articles/" not in href:
                    continue

                # URL completa
                url_articulo = href if href.startswith("http") else BASE_URL + href

                # Buscar descripción si existe
                descripcion = None
                parent = a.find_parent()
                if parent:
                    p = parent.find("p")
                    if p:
                        descripcion = p.get_text(strip=True)

                registros.append({
                    "codigo":      href.split("/")[-1],
                    "titulo":      titulo,
                    "descripcion": descripcion,
                    "url":         url_articulo,
                    "categoria":   "Economía",
                    "fuente":      "scraping:bbc_mundo_economia",
                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "pagina":      pagina
                })

        # Eliminar duplicados por código
        vistos = set()
        unicos = []
        for r in registros:
            if r["codigo"] not in vistos:
                vistos.add(r["codigo"])
                unicos.append(r)

        logger.info(f"Página {pagina}: {len(unicos)} noticias extraídas")
        return unicos

    except requests.exceptions.Timeout:
        logger.error(f"Timeout al conectar con BBC Mundo (página {pagina})")
        return []
    except Exception as e:
        logger.error(f"Error en scraping BBC Mundo página {pagina}: {e}")
        return []


if __name__ == "__main__":
    logger.info("=== Extrayendo noticias económicas BBC Mundo ===")
    noticias = extraer_noticias_economia(paginas=2)

    print(f"\n{'#':<4} {'Título':<70} {'URL'}")
    print("-" * 120)
    for i, n in enumerate(noticias, 1):
        print(f"{i:<4} {n['titulo'][:68]:<70} {n['url']}")

    print(f"\nTotal: {len(noticias)} noticias")