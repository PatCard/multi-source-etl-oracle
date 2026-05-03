import os
from dotenv import load_dotenv

load_dotenv()

ORACLE = {
    "host":     os.getenv("ORACLE_HOST", "oracle"),
    "port":     int(os.getenv("ORACLE_PORT", 1521)),
    "service":  os.getenv("ORACLE_SERVICE", "FREEPDB1"),
    "user":     os.getenv("ORACLE_USER", "etl_user"),
    "password": os.getenv("ORACLE_PASSWORD"),
}

MYSQL = {
    "host":     os.getenv("MYSQL_HOST", "mysql"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DB", "source_db"),
    "user":     os.getenv("MYSQL_USER", "etl_reader"),
    "password": os.getenv("MYSQL_PASSWORD"),
}

MYSQL_URL = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    f"?charset=utf8mb4"
)

MONGO = {
    "host":     os.getenv("MONGO_HOST", "mongodb"),
    "port":     int(os.getenv("MONGO_PORT", 27017)),
    "database": os.getenv("MONGO_DB", "source_db"),
    "user":     os.getenv("MONGO_USER", "root"),
    "password": os.getenv("MONGO_PASSWORD"),
}

MONGO_URL = (
    f"mongodb://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}"
    f"@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{os.getenv('MONGO_DB')}"
    f"?authSource=admin"
)

API = {
    "key":      os.getenv("API_KEY"),
    "base_url": os.getenv("API_BASE_URL"),
}

SCRAPING = {
    "url": os.getenv("SCRAPING_URL"),
}

ETL = {
    "batch_size": int(os.getenv("ETL_BATCH_SIZE", 100)),
    "log_level":  os.getenv("ETL_LOG_LEVEL", "INFO"),
}
