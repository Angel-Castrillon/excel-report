"""
Servicio de gestión de datasets.
Coordina el parseo de archivos Excel, persistencia en SQLite, registro de metadatos y CRUD.
"""
import io
import json
from typing import List, Dict, Any, Optional
import pandas as pd
from app.database import get_db_connection, execute_query, execute_insert, execute_non_query
from app.models import DatasetDetail, DatasetSummary, ColumnMetadata
from app.services.excel_parser import parse_excel_file

def format_file_size(size_bytes: int) -> str:
    """Convierte un tamaño en bytes a formato legible (KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def create_dataset_from_upload(original_filename: str, file_content: bytes) -> DatasetDetail:
    """
    Parsea el archivo Excel desde los bytes en memoria, crea la tabla de datos en SQLite
    e inserta los metadatos correspondientes.
    """
    file_size_bytes = len(file_content)
    file_buffer = io.BytesIO(file_content)
    
    # 1. Parsear el archivo Excel con pandas e inferir tipos
    df, columns_metadata = parse_excel_file(file_buffer)
    
    row_count = len(df)
    column_count = len(columns_metadata)
    
    # Convertir metadatos de columnas a formato JSON
    columns_json = json.dumps([col.model_dump() for col in columns_metadata], ensure_ascii=False)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 2. Insertar registro en la tabla 'datasets'
        cursor.execute("""
            INSERT INTO datasets (
                original_filename, file_size_bytes, row_count, column_count, columns_metadata
            ) VALUES (?, ?, ?, ?, ?);
        """, (original_filename, file_size_bytes, row_count, column_count, columns_json))
        
        dataset_id = cursor.lastrowid
        table_name = f"dataset_{dataset_id}_records"
        
        # 3. Guardar el DataFrame completo en su tabla dedicada en SQLite
        df.to_sql(table_name, con=conn, if_exists='replace', index=True, index_label='_row_id')
        
        # 4. Obtener la fecha de creación registrada
        cursor.execute("SELECT created_at FROM datasets WHERE id = ?;", (dataset_id,))
        created_at_row = cursor.fetchone()
        created_at = created_at_row["created_at"] if created_at_row else ""
        
    return DatasetDetail(
        id=dataset_id,
        original_filename=original_filename,
        file_size_bytes=file_size_bytes,
        file_size_human=format_file_size(file_size_bytes),
        row_count=row_count,
        column_count=column_count,
        columns_metadata=columns_metadata,
        custom_config=None,
        created_at=str(created_at)
    )

def list_datasets() -> List[DatasetSummary]:
    """
    Retorna la lista de todos los datasets disponibles ordenados por fecha más reciente.
    """
    query = """
        SELECT id, original_filename, file_size_bytes, row_count, column_count, created_at
        FROM datasets
        ORDER BY created_at DESC, id DESC;
    """
    rows = execute_query(query)
    datasets: List[DatasetSummary] = []
    for r in rows:
        datasets.append(DatasetSummary(
            id=r["id"],
            original_filename=r["original_filename"],
            file_size_bytes=r["file_size_bytes"],
            file_size_human=format_file_size(r["file_size_bytes"]),
            row_count=r["row_count"],
            column_count=r["column_count"],
            created_at=str(r["created_at"])
        ))
    return datasets

def get_dataset_detail(dataset_id: int) -> Optional[DatasetDetail]:
    """
    Obtiene los detalles completos y metadatos de un dataset específico por su ID.
    """
    query = """
        SELECT id, original_filename, file_size_bytes, row_count, column_count, 
               columns_metadata, custom_config, created_at
        FROM datasets
        WHERE id = ?;
    """
    rows = execute_query(query, (dataset_id,))
    if not rows:
        return None
    
    r = rows[0]
    raw_columns = json.loads(r["columns_metadata"]) if r["columns_metadata"] else []
    columns_metadata = [ColumnMetadata(**col) for col in raw_columns]
    
    custom_config = None
    if r["custom_config"]:
        try:
            custom_config = json.loads(r["custom_config"])
        except Exception:
            custom_config = None
            
    return DatasetDetail(
        id=r["id"],
        original_filename=r["original_filename"],
        file_size_bytes=r["file_size_bytes"],
        file_size_human=format_file_size(r["file_size_bytes"]),
        row_count=r["row_count"],
        column_count=r["column_count"],
        columns_metadata=columns_metadata,
        custom_config=custom_config,
        created_at=str(r["created_at"])
    )

def update_dataset_config(dataset_id: int, custom_config: Dict[str, Any]) -> bool:
    """
    Guarda la configuración personalizada de gráficos y filtros para un dataset.
    """
    config_json = json.dumps(custom_config, ensure_ascii=False)
    query = "UPDATE datasets SET custom_config = ? WHERE id = ?;"
    affected = execute_non_query(query, (config_json, dataset_id))
    return affected > 0

def delete_dataset(dataset_id: int) -> bool:
    """
    Elimina en cascada el dataset: borra su tabla física en SQLite y su registro de metadatos.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Comprobar si existe
        cursor.execute("SELECT id FROM datasets WHERE id = ?;", (dataset_id,))
        if not cursor.fetchone():
            return False
            
        # 2. Eliminar la tabla de datos física
        table_name = f"dataset_{dataset_id}_records"
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        
        # 3. Eliminar el registro de metadatos
        cursor.execute("DELETE FROM datasets WHERE id = ?;", (dataset_id,))
        conn.commit()
        return True
