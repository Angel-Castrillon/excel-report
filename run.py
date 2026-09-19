"""
Punto de entrada principal para ejecutar la aplicación en 1 solo comando.
Inicia el servidor local FastAPI y abre el navegador web automáticamente.
Compatible con ejecución directa desde consola y como ejecutable compilado.
"""
import sys
import subprocess
import webbrowser
import time
import os
import threading

def check_and_install_dependencies():
    """Verifica si las dependencias requeridas están instaladas; si faltan, las instala."""
    # Si está corriendo como .exe empaquetado, no necesita pip
    if getattr(sys, 'frozen', False):
        return

    required_packages = ["fastapi", "uvicorn", "pandas", "openpyxl", "python-multipart"]
    missing = []
    
    for package in required_packages:
        pkg_import_name = "multipart" if package == "python-multipart" else package
        try:
            __import__(pkg_import_name)
        except ImportError:
            missing.append(package)
            
    if missing:
        print(f"📦 Instalando dependencias faltantes: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(" Dependencias instaladas con éxito.\n")

def main():
    print("=" * 60)
    print("🚀 Iniciando Excel Report Dashboard (Modo Local)")
    print("=" * 60)
    
    check_and_install_dependencies()
    
    import uvicorn
    from app.config import HOST, PORT, APP_URL, IS_FROZEN
    from app.main import app as fastapi_app
    
    print(f"\n🌐 Servidor disponible en: {APP_URL}")
    print("💡 Presiona CTRL + C en esta terminal para detener la aplicación.\n")
    
    # Abrir el navegador tras 1.2 segundos
    def open_browser():
        time.sleep(1.2)
        webbrowser.open(APP_URL)
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor uvicorn pasando el objeto de la aplicación directamente
    # reload=False es necesario para ejecutables congelados y garantiza máxima estabilidad
    uvicorn.run(fastapi_app, host=HOST, port=PORT, reload=False, log_level="info")

if __name__ == "__main__":
    main()
