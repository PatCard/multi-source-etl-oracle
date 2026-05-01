# ─────────────────────────────────────────
# multi-source-etl-oracle
# Contenedor Python para el ETL
# ─────────────────────────────────────────
 
FROM python:3.11-slim
 
# Dependencias del sistema necesarias para oracledb y lxml
RUN apt-get update && apt-get install -y \
    gcc \
    libaio1 \
    curl \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
 
# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copiar el código
COPY . .
 
# Por defecto ejecuta el orquestador
CMD ["python", "orchestrator.py"]
 