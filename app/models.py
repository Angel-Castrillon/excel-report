"""
Modelos de datos y esquemas de validación (Pydantic).
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class ColumnMetadata(BaseModel):
    """Metadatos de una columna del archivo Excel."""
    name: str = Field(..., description="Nombre original de la columna en el Excel")
    clean_name: str = Field(..., description="Nombre sanitizado para uso seguro en SQL")
    data_type: str = Field(..., description="Tipo inferido: numeric, date, category, text")
    sample_values: List[Any] = Field(default_factory=list, description="Muestra de valores representativos")
    null_count: int = Field(0, description="Cantidad de valores nulos o vacíos")
    unique_count: int = Field(0, description="Cantidad de valores únicos distintos")

class DatasetSummary(BaseModel):
    """Resumen liviano de un dataset para la lista de la biblioteca."""
    id: int
    original_filename: str
    file_size_bytes: int
    file_size_human: str
    row_count: int
    column_count: int
    created_at: str

class DatasetDetail(BaseModel):
    """Detalle completo de un dataset incluyendo sus columnas y configuración guardada."""
    id: int
    original_filename: str
    file_size_bytes: int
    file_size_human: str
    row_count: int
    column_count: int
    columns_metadata: List[ColumnMetadata]
    custom_config: Optional[Dict[str, Any]] = None
    created_at: str

class DatasetConfigUpdate(BaseModel):
    """Cuerpo de petición para actualizar la configuración de visualización de un dataset."""
    custom_config: Dict[str, Any]

class QueryFilter(BaseModel):
    """Definición de un filtro individual sobre una columna."""
    column: str
    operator: str = Field("eq", description="eq, neq, gt, gte, lt, lte, in, between, contains")
    value: Union[str, int, float, list, None]

class QueryRequest(BaseModel):
    """Petición de consulta para tabla y paginación con filtros."""
    filters: Optional[List[QueryFilter]] = Field(default_factory=list)
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    sort_by: Optional[str] = None
    sort_order: str = Field("asc", pattern="^(asc|desc|ASC|DESC)$")

class AggregationRequest(BaseModel):
    """Petición de agregación para renderizar gráficos."""
    dimension: str = Field(..., description="Columna para el Eje X (categoría o fecha)")
    metric: Optional[str] = Field(None, description="Columna numérica para el Eje Y")
    aggregation_func: str = Field("sum", pattern="^(sum|avg|count|min|max)$", description="Operación: sum, avg, count, min, max")
    filters: Optional[List[QueryFilter]] = Field(default_factory=list)
    limit: int = Field(15, ge=1, le=100, description="Límite de categorías para evitar saturar el gráfico")
    sort_by_metric: bool = Field(True, description="Si es True, ordena por el valor de la métrica de mayor a menor")
