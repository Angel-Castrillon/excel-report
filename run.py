"""
Punto de entrada principal para ejecutar la aplicación en 1 solo comando.
Inicia el servidor local FastAPI y abre el navegador web automáticamente.
"""
import sys
import subprocess
import webbrowser
import time
import os

def check_and_install_dependencies():
    """Verifica si las dependencias requeridas están instaladas; si faltan, las instala."""
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
    from app.config import HOST, PORT, APP_URL
    
    print(f"\n🌐 Servidor disponible en: {APP_URL}")
    print("💡 Presiona CTRL + C en esta terminal para detener la aplicación.\n")
    
    # Abrir el navegador tras 1 segundo
    def open_browser():
        time.sleep(1.2)
        webbrowser.open(APP_URL)
        
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)

if __name__ == "__main__":
    main()
