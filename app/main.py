"""
Instancia principal de la aplicación FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_URL

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

@app.get("/api/health")
def health_check():
    """Endpoint de comprobación de estado de la aplicación."""
    return {
        "status": "online",
        "service": "Excel Report Dashboard",
        "version": "0.1.0"
    }
