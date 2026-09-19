"""
Módulo de configuración global de la aplicación.
Centraliza rutas de almacenamiento, nombres de archivo y parámetros de la API.
Compatible con ejecución desde código fuente y como ejecutable congelado (.exe con PyInstaller).
"""
import sys
from pathlib import Path

# Detectar si se está ejecutando como ejecutable empaquetado (PyInstaller)
IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    # Directorio donde se encuentra el .exe
    BASE_DIR = Path(sys.executable).resolve().parent
    # Directorio temporal donde PyInstaller descomprime los recursos estáticos
    BUNDLE_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR))
    STATIC_DIR = BUNDLE_DIR / "app" / "static"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_DIR = BASE_DIR / "app" / "static"

# Directorios de datos y cargas persistentes (siempre junto al ejecutable o en la raíz)
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
