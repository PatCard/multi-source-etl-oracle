import time
from loguru import logger

logger.info("ETL multi-source-etl-oracle iniciado correctamente")
logger.info("Esperando trabajo...")

while True:
    time.sleep(60)
