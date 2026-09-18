"""
Módulo de configuración global de la aplicación.
Centraliza rutas de almacenamiento, nombres de archivo y parámetros de la API.
"""
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorios de datos y cargas
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "excel_dashboard.db"

# Asegurar que los directorios existan
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Parámetros del servidor local
HOST = "127.0.0.1"
PORT = 8000
APP_URL = f"http://{HOST}:{PORT}"

# Parámetros de validación de archivos
ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
