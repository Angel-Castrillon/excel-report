"""
Instancia principal de la aplicación FastAPI.
Configura rutas de la API, servicios analíticos y sirve la interfaz web local.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import (
    BASE_DIR,
    STATIC_DIR,
    APP_URL,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB
)
from app.database import init_db
from app.models import (
    DatasetDetail,
    DatasetSummary,
    DatasetConfigUpdate,
    QueryFilter,
    QueryRequest,
    AggregationRequest
)
from app.services.dataset_service import (
    create_dataset_from_upload,
    list_datasets,
    get_dataset_detail,
    update_dataset_config,
    delete_dataset
)
from app.services.query_service import (
    get_filter_options,
    get_dataset_kpis,
    get_table_data,
    get_chart_aggregation
)

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

# Asegurar que la base de datos se inicialice al arrancar
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

# ==========================================
# GESTIÓN DE DATASETS (CRUD)
# ==========================================

@app.get("/api/datasets", response_model=List[DatasetSummary])
def get_all_datasets():
    """Retorna la lista histórica de todos los datasets subidos."""
    return list_datasets()

@app.get("/api/datasets/{dataset_id}", response_model=DatasetDetail)
def get_dataset(dataset_id: int):
    """Obtiene el detalle completo de un dataset con sus columnas y configuración guardada."""
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset con ID {dataset_id} no encontrado."
        )
    return dataset

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

@app.put("/api/datasets/{dataset_id}/config")
def save_dataset_configuration(dataset_id: int, payload: DatasetConfigUpdate):
    """Guarda la configuración personalizada de gráficos y filtros para el dataset."""
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset con ID {dataset_id} no encontrado."
        )
    success = update_dataset_config(dataset_id, payload.custom_config)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo actualizar la configuración."
        )
    return {"status": "success", "message": "Configuración guardada exitosamente."}

@app.delete("/api/datasets/{dataset_id}")
def remove_dataset(dataset_id: int):
    """Elimina permanentemente un dataset y su tabla asociada en SQLite."""
    success = delete_dataset(dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset con ID {dataset_id} no encontrado."
        )
    return {
        "status": "deleted",
        "id": dataset_id,
        "message": "Dataset y datos asociados eliminados correctamente."
    }

# ==========================================
# CONSULTAS, FILTROS Y ANALÍTICA
# ==========================================

@app.get("/api/datasets/{dataset_id}/filter-options")
def get_dataset_filter_options(dataset_id: int):
    """Retorna las opciones y rangos de cada columna para configurar filtros dinámicos."""
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return get_filter_options(dataset_id)

@app.post("/api/datasets/{dataset_id}/kpis")
def calculate_dataset_kpis(dataset_id: int, filters: Optional[List[QueryFilter]] = None):
    """Calcula los KPIs filtrados del dataset."""
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return get_dataset_kpis(dataset_id, filters)

@app.post("/api/datasets/{dataset_id}/table")
def query_dataset_table(dataset_id: int, req: QueryRequest):
    """Retorna los datos tabulares paginados y ordenables con filtros aplicados."""
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return get_table_data(dataset_id, req)

@app.post("/api/datasets/{dataset_id}/chart")
def aggregate_chart_data(dataset_id: int, req: AggregationRequest):
    """Genera datos agregados para renderizar un gráfico (barras, líneas, etc.)."""
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    return get_chart_aggregation(dataset_id, req)

# ==========================================
# SERVIR FRONTEND ESTÁTICO (SPA)
# ==========================================

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    """Sirve la interfaz web principal."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return {"message": "Interfaz frontend en construcción."}
    return FileResponse(str(index_file))
