"""
Módulo de gestión de base de datos local SQLite.
Maneja la conexión, transacciones y creación de tablas iniciales.
"""
import sqlite3
import json
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Optional
from app.config import DB_PATH

def init_db():
    """Inicializa la base de datos SQLite y crea las tablas del sistema si no existen."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Habilitar claves foráneas y modo WAL (Write-Ahead Logging) para concurrencia local óptima
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        
        # 1. Tabla de metadatos de los datasets cargados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                row_count INTEGER NOT NULL,
                column_count INTEGER NOT NULL,
                columns_metadata TEXT NOT NULL,
                custom_config TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Índice para ordenar rápidamente por fecha de carga
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_datasets_created_at 
            ON datasets (created_at DESC);
        """)
        
        conn.commit()

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager para obtener una conexión a SQLite con fila como diccionario (sqlite3.Row).
    Maneja el commit automático al salir o rollback si ocurre una excepción.
    """
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Ejecuta una consulta SELECT y retorna una lista de diccionarios."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def execute_insert(query: str, params: tuple = ()) -> int:
    """Ejecuta un INSERT y retorna el ID autoincremental insertado."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid

def execute_non_query(query: str, params: tuple = ()) -> int:
    """Ejecuta un UPDATE, DELETE o DDL y retorna el número de filas afectadas."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount
