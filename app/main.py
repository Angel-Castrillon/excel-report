"""
Instancia principal de la aplicación FastAPI.
Configura rutas, middleware y el ciclo de vida de la aplicación.
"""
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import APP_URL, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from app.database import init_db
from app.models import DatasetDetail
from app.services.dataset_service import create_dataset_from_upload

app = FastAPI(
    title="Excel Report Dashboard API",
    description="API local para parseo, persistencia y visualización interactiva de archivos Excel",
    version="0.1.0"
)

# Permitir CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Inicializa la base de datos al arrancar el servidor."""
    init_db()

@app.get("/api/health")
def health_check():
    """Endpoint de comprobación de estado de la aplicación."""
    return {
        "status": "online",
        "service": "Excel Report Dashboard",
        "version": "0.1.0"
    }

@app.post("/api/datasets/upload", response_model=DatasetDetail, status_code=status.HTTP_201_CREATED)
async def upload_excel_dataset(file: UploadFile = File(...)):
    """
    Recibe un archivo Excel (.xlsx / .xls), extrae sus datos y metadatos,
    los persiste en SQLite y retorna el detalle del dataset creado.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido."
        )
        
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato no permitido ({file_ext}). Solo se admiten archivos {', '.join(ALLOWED_EXTENSIONS)}."
        )
        
    # Leer el contenido completo del archivo subido
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el tamaño máximo permitido de {MAX_FILE_SIZE_MB} MB."
        )
        
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo subido está vacío."
        )
        
    try:
        dataset_detail = create_dataset_from_upload(
            original_filename=file.filename,
            file_content=contents
        )
        return dataset_detail
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el archivo Excel: {str(e)}"
        )
