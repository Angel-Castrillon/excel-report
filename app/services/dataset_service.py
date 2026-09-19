"""
Servicio de gestión de datasets.
Coordina el parseo de archivos Excel, persistencia en SQLite y registro de metadatos.
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
        # Usamos index=True como '_row_id' para tener un identificador de fila único y estable
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
