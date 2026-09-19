"""
Servicio de parseo e inferencia de tipos de datos para archivos Excel (.xlsx / .xls).
Utiliza Pandas y OpenPyXL/xlrd para extraer la estructura y normalizar los registros.
"""
import re
import unicodedata
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from app.models import ColumnMetadata

def sanitize_column_name(col_name: str, index: int) -> str:
    """
    Genera un identificador seguro para SQL a partir del nombre original de la columna.
    Ejemplo: 'Ventas ($ USD)' -> 'col_0_ventas_usd'
    """
    if not col_name or str(col_name).strip() == "" or "unnamed" in str(col_name).lower():
        return f"col_{index}_campo_{index+1}"
    
    # Normalizar caracteres unicode (eliminar tildes/acentos)
    s = unicodedata.normalize('NFKD', str(col_name)).encode('ASCII', 'ignore').decode('utf-8')
    # Reemplazar caracteres no alfanuméricos por guiones bajos
    s = re.sub(r'[^a-zA-Z0-9]+', '_', s).strip('_').lower()
    if not s:
        s = f"campo_{index+1}"
    return f"col_{index}_{s}"

def infer_column_type(series: pd.Series, total_rows: int) -> str:
    """
    Infiere el tipo de dato de una columna:
    - 'numeric': enteros o decimales
    - 'date': fechas o marcas de tiempo
    - 'category': textos con baja cardinalidad (dimensiones, estados, categorías)
    - 'text': descripciones largas o identificadores de alta cardinalidad
    """
    non_null_series = series.dropna()
    if non_null_series.empty:
        return "text"
    
    # 1. Verificar si ya es tipo fecha nativo
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    
    # 2. Verificar numérico
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    
    # 3. Intentar parsear como fecha si es string u object
    if pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
        sample = non_null_series.head(30)
        date_pattern = re.compile(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}|^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}')
        try:
            matches = sample.astype(str).str.match(date_pattern).sum()
            if len(sample) > 0 and (matches / len(sample)) >= 0.8:
                pd.to_datetime(sample, errors='raise')
                return "date"
        except Exception:
            pass

    # 4. Determinar entre categoría y texto libre
    unique_count = non_null_series.nunique()
    avg_len = non_null_series.astype(str).str.len().mean() if not non_null_series.empty else 0
    
    # Si los textos son cortos (<= 60 caracteres) y hay repetibilidad o pocas opciones
    if avg_len <= 60 and (unique_count <= 50 or (total_rows > 10 and (unique_count / total_rows) <= 0.35)):
        return "category"
        
    return "text"

def parse_excel_file(file_path_or_buffer: Any) -> Tuple[pd.DataFrame, List[ColumnMetadata]]:
    """
    Lee un archivo Excel, sanea encabezados, infiere tipos de datos y prepara el DataFrame.
    Retorna el DataFrame normalizado y la lista de metadatos de columnas.
    """
    # Leer el archivo con Pandas
    df = pd.read_excel(file_path_or_buffer, sheet_name=0)
    
    # Si el archivo está vacío
    if df.empty:
        return df, []
    
    total_rows = len(df)
    columns_metadata: List[ColumnMetadata] = []
    clean_columns_map: Dict[str, str] = {}
    
    for idx, original_col in enumerate(df.columns):
        clean_name = sanitize_column_name(str(original_col), idx)
        clean_columns_map[original_col] = clean_name
        
        series = df[original_col]
        col_type = infer_column_type(series, total_rows)
        
        # Formatear fechas de manera consistente para SQLite (ISO-8601 string)
        if col_type == "date":
            try:
                parsed_dates = pd.to_datetime(series, errors='coerce')
                # Si tiene hora relevante, guardar datetime; si no, date
                has_time = parsed_dates.dt.time.dropna().ne(pd.Timestamp('00:00:00').time()).any()
                if has_time:
                    df[original_col] = parsed_dates.dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    df[original_col] = parsed_dates.dt.strftime('%Y-%m-%d')
            except Exception:
                col_type = "text"
        elif col_type == "numeric":
            df[original_col] = pd.to_numeric(series, errors='coerce')
        else:
            # Convertir a string limpio
            df[original_col] = series.apply(lambda x: str(x).strip() if pd.notna(x) else None)
            
        # Muestra de 3 a 5 valores no nulos
        non_null_samples = df[original_col].dropna().unique()[:4].tolist()
        # Asegurar serialización JSON limpia
        clean_samples = []
        for v in non_null_samples:
            if isinstance(v, (np.integer, int)):
                clean_samples.append(int(v))
            elif isinstance(v, (np.floating, float)):
                clean_samples.append(round(float(v), 2))
            else:
                clean_samples.append(str(v))
                
        unique_count = int(df[original_col].nunique(dropna=True))
        null_count = int(df[original_col].isna().sum())
        
        columns_metadata.append(ColumnMetadata(
            name=str(original_col).strip(),
            clean_name=clean_name,
            data_type=col_type,
            sample_values=clean_samples,
            null_count=null_count,
            unique_count=unique_count
        ))
        
    # Renombrar columnas del DataFrame con los nombres sanitizados para SQL
    df.rename(columns=clean_columns_map, inplace=True)
    
    # Reemplazar NaN de numpy por None de Python para que SQLite inserte NULLs
    df = df.replace({np.nan: None})
    
    return df, columns_metadata
