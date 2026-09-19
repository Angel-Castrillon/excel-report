"""
Servicio de consultas, filtros dinámicos, cálculo de KPIs y agregaciones para gráficos.
Construye sentencias SQL parametrizadas y seguras contra SQLite.
"""
from typing import List, Dict, Any, Tuple, Optional
from app.database import get_db_connection, execute_query
from app.models import QueryFilter, QueryRequest, AggregationRequest, ColumnMetadata
from app.services.dataset_service import get_dataset_detail

def build_where_clause(
    filters: Optional[List[QueryFilter]],
    columns_map: Dict[str, ColumnMetadata]
) -> Tuple[str, List[Any]]:
    """
    Construye la cláusula WHERE y sus parámetros seguros a partir de la lista de filtros.
    Valida que las columnas existan para prevenir inyección SQL.
    """
    if not filters:
        return "", []
    
    conditions = []
    params = []
    
    for f in filters:
        col_clean = f.column
        # Validar que la columna sea válida
        if col_clean not in columns_map:
            continue
        
        op = f.operator.lower()
        val = f.value
        
        if val is None or val == "":
            continue
            
        if op == "eq":
            conditions.append(f'"{col_clean}" = ?')
            params.append(val)
        elif op == "neq":
            conditions.append(f'"{col_clean}" != ?')
            params.append(val)
        elif op == "gt":
            conditions.append(f'"{col_clean}" > ?')
            params.append(val)
        elif op == "gte":
            conditions.append(f'"{col_clean}" >= ?')
            params.append(val)
        elif op == "lt":
            conditions.append(f'"{col_clean}" < ?')
            params.append(val)
        elif op == "lte":
            conditions.append(f'"{col_clean}" <= ?')
            params.append(val)
        elif op == "contains":
            conditions.append(f'"{col_clean}" LIKE ?')
            params.append(f"%{val}%")
        elif op == "in" and isinstance(val, list) and len(val) > 0:
            placeholders = ", ".join(["?"] * len(val))
            conditions.append(f'"{col_clean}" IN ({placeholders})')
            params.extend(val)
        elif op == "between" and isinstance(val, list) and len(val) == 2:
            conditions.append(f'"{col_clean}" BETWEEN ? AND ?')
            params.append(val[0])
            params.append(val[1])
            
    if not conditions:
        return "", []
        
    return "WHERE " + " AND ".join(conditions), params

def get_filter_options(dataset_id: int) -> Dict[str, Any]:
    """
    Retorna opciones de filtro para cada columna:
    - Categóricas: lista de opciones únicas
    - Numéricas: min y max
    - Fechas: min_date y max_date
    """
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        return {}
        
    table_name = f"dataset_{dataset_id}_records"
    columns_map = {col.clean_name: col for col in dataset.columns_metadata}
    options: Dict[str, Any] = {}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for col in dataset.columns_metadata:
            c_name = col.clean_name
            if col.data_type == "category":
                cursor.execute(f'SELECT DISTINCT "{c_name}" FROM {table_name} WHERE "{c_name}" IS NOT NULL ORDER BY "{c_name}" ASC LIMIT 50;')
                unique_vals = [r[0] for r in cursor.fetchall() if r[0] is not None and str(r[0]).strip() != ""]
                options[c_name] = {
                    "type": "category",
                    "values": unique_vals
                }
            elif col.data_type == "numeric":
                cursor.execute(f'SELECT MIN("{c_name}"), MAX("{c_name}"), AVG("{c_name}") FROM {table_name} WHERE "{c_name}" IS NOT NULL;')
                row = cursor.fetchone()
                options[c_name] = {
                    "type": "numeric",
                    "min": row[0] if row and row[0] is not None else 0,
                    "max": row[1] if row and row[1] is not None else 0,
                    "avg": round(row[2], 2) if row and row[2] is not None else 0
                }
            elif col.data_type == "date":
                cursor.execute(f'SELECT MIN("{c_name}"), MAX("{c_name}") FROM {table_name} WHERE "{c_name}" IS NOT NULL;')
                row = cursor.fetchone()
                options[c_name] = {
                    "type": "date",
                    "min_date": str(row[0]) if row and row[0] else "",
                    "max_date": str(row[1]) if row and row[1] else ""
                }
            else:
                options[c_name] = {
                    "type": "text"
                }
    return options

def get_dataset_kpis(dataset_id: int, filters: Optional[List[QueryFilter]] = None) -> Dict[str, Any]:
    """
    Calcula indicadores clave de rendimiento (KPIs) sobre los registros filtrados:
    - Conteo total filtrado vs registros totales del dataset
    - Resumen de métricas numéricas principales (suma, promedio)
    """
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        return {}
        
    table_name = f"dataset_{dataset_id}_records"
    columns_map = {col.clean_name: col for col in dataset.columns_metadata}
    where_clause, params = build_where_clause(filters, columns_map)
    
    # 1. Total filtrado
    count_query = f"SELECT COUNT(*) as filtered_count FROM {table_name} {where_clause};"
    rows = execute_query(count_query, tuple(params))
    filtered_count = rows[0]["filtered_count"] if rows else 0
    
    # 2. Resumen de columnas numéricas (hasta las primeras 3 columnas numéricas para las tarjetas)
    numeric_cols = [col for col in dataset.columns_metadata if col.data_type == "numeric"]
    kpi_cards = []
    
    # Tarjeta 1: Total registros
    kpi_cards.append({
        "id": "total_records",
        "title": "Registros Filtrados",
        "value": f"{filtered_count:,}",
        "subtitle": f"De un total de {dataset.row_count:,} registros",
        "type": "count"
    })
    
    for num_col in numeric_cols[:3]:
        c_name = num_col.clean_name
        stat_query = f"""
            SELECT 
                SUM("{c_name}") as total_sum,
                AVG("{c_name}") as total_avg,
                MAX("{c_name}") as max_val
            FROM {table_name} {where_clause} AND "{c_name}" IS NOT NULL;
        """ if where_clause else f"""
            SELECT 
                SUM("{c_name}") as total_sum,
                AVG("{c_name}") as total_avg,
                MAX("{c_name}") as max_val
            FROM {table_name} WHERE "{c_name}" IS NOT NULL;
        """
        stat_rows = execute_query(stat_query, tuple(params))
        if stat_rows and stat_rows[0]["total_sum"] is not None:
            r = stat_rows[0]
            val_sum = round(r["total_sum"], 2)
            val_avg = round(r["total_avg"], 2)
            kpi_cards.append({
                "id": f"kpi_{c_name}",
                "title": f"Total {num_col.name}",
                "value": f"{val_sum:,.2f}" if val_sum % 1 != 0 else f"{int(val_sum):,}",
                "subtitle": f"Promedio: {val_avg:,.2f}",
                "type": "metric"
            })
            
    return {
        "dataset_id": dataset_id,
        "total_rows": dataset.row_count,
        "filtered_rows": filtered_count,
        "kpi_cards": kpi_cards
    }

def get_table_data(dataset_id: int, req: QueryRequest) -> Dict[str, Any]:
    """
    Retorna los datos tabulares paginados y ordenados con filtros aplicados.
    """
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        return {"total": 0, "rows": [], "page": 1, "pages": 0}
        
    table_name = f"dataset_{dataset_id}_records"
    columns_map = {col.clean_name: col for col in dataset.columns_metadata}
    where_clause, params = build_where_clause(req.filters, columns_map)
    
    # Total de registros con filtro
    count_query = f"SELECT COUNT(*) as total FROM {table_name} {where_clause};"
    count_rows = execute_query(count_query, tuple(params))
    total = count_rows[0]["total"] if count_rows else 0
    
    # Orden
    order_clause = ""
    if req.sort_by and req.sort_by in columns_map:
        order_dir = "DESC" if req.sort_order.upper() == "DESC" else "ASC"
        order_clause = f'ORDER BY "{req.sort_by}" {order_dir}'
    else:
        order_clause = "ORDER BY _row_id ASC"
        
    # Paginación
    data_query = f"""
        SELECT * FROM {table_name} 
        {where_clause} 
        {order_clause} 
        LIMIT ? OFFSET ?;
    """
    query_params = list(params) + [req.limit, req.offset]
    rows = execute_query(data_query, tuple(query_params))
    
    return {
        "total": total,
        "limit": req.limit,
        "offset": req.offset,
        "page": (req.offset // req.limit) + 1,
        "pages": (total + req.limit - 1) // req.limit if total > 0 else 0,
        "rows": rows
    }

def get_chart_aggregation(dataset_id: int, req: AggregationRequest) -> Dict[str, Any]:
    """
    Ejecuta una agregación agrupada (GROUP BY) para renderizar gráficos de barras, líneas o dona.
    """
    dataset = get_dataset_detail(dataset_id)
    if not dataset:
        return {"labels": [], "values": []}
        
    table_name = f"dataset_{dataset_id}_records"
    columns_map = {col.clean_name: col for col in dataset.columns_metadata}
    
    dim_col = req.dimension
    if dim_col not in columns_map:
        return {"labels": [], "values": [], "error": f"Columna dimensión {dim_col} inválida."}
        
    where_clause, params = build_where_clause(req.filters, columns_map)
    
    # Métrica y función de agregación
    agg_func = req.aggregation_func.upper() # SUM, AVG, COUNT, MIN, MAX
    
    if req.metric and req.metric in columns_map and agg_func != "COUNT":
        metric_expr = f'{agg_func}("{req.metric}")'
        metric_label = f"{agg_func} de {columns_map[req.metric].name}"
    else:
        metric_expr = "COUNT(*)"
        metric_label = "Cantidad de Registros"
        
    # Agrupación y orden
    # Excluir dimensiones nulas
    filter_dim = f'"{dim_col}" IS NOT NULL AND "{dim_col}" != \'\''
    if where_clause:
        full_where = f"{where_clause} AND {filter_dim}"
    else:
        full_where = f"WHERE {filter_dim}"
        
    order_by = 'metric_val DESC' if req.sort_by_metric else f'"{dim_col}" ASC'
    
    query = f"""
        SELECT 
            "{dim_col}" as dim_val,
            {metric_expr} as metric_val
        FROM {table_name}
        {full_where}
        GROUP BY "{dim_col}"
        ORDER BY {order_by}
        LIMIT ?;
    """
    query_params = list(params) + [req.limit]
    rows = execute_query(query, tuple(query_params))
    
    labels = []
    values = []
    for r in rows:
        labels.append(str(r["dim_val"]))
        val = r["metric_val"]
        values.append(round(float(val), 2) if val is not None else 0)
        
    return {
        "dimension": dim_col,
        "dimension_name": columns_map[dim_col].name,
        "metric": req.metric,
        "metric_name": columns_map[req.metric].name if req.metric and req.metric in columns_map else "Conteo",
        "aggregation": agg_func,
        "metric_label": metric_label,
        "labels": labels,
        "values": values
    }
