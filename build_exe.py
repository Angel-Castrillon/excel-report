"""
Script de compilación para empaquetar la aplicación en un archivo ejecutable (.exe).
Utiliza PyInstaller con todas las dependencias estáticas y módulos ocultos requeridos por Uvicorn.
"""
import sys
import subprocess
from pathlib import Path

def build_executable():
    print("=" * 60)
    print("📦 Compilando Excel Report Dashboard a Ejecutable (.exe)...")
    print("=" * 60)
    
    base_dir = Path(__file__).resolve().parent
    static_dir = base_dir / "app" / "static"
    
    # Parámetro add-data en formato Windows: origen;destino
    add_data_param = f"{static_dir};app/static"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ExcelReportStudio",
        "--noconfirm",
        "--clean",
        # Incluir archivos estáticos (HTML, JS, CSS)
        f"--add-data={add_data_param}",
        # Importaciones dinámicas requeridas por Uvicorn y FastAPI
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespans",
        "--hidden-import=uvicorn.lifespans.on",
        # Archivo principal de entrada
        "run.py"
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}\n")
    try:
        subprocess.check_call(cmd)
        print("\n🎉 ¡Compilación completada exitosamente!")
        print(f"El ejecutable se encuentra en: {base_dir / 'dist' / 'ExcelReportStudio' / 'ExcelReportStudio.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error durante la compilación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
