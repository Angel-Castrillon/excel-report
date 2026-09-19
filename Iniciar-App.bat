@echo off
chcp 65001 >nul
title Excel Report Dashboard
cd /d "%~dp0"

echo ================================================================
echo   🚀 INICIANDO EXCEL REPORT DASHBOARD (MODO LOCAL)
echo ================================================================
echo.

:: Verificar si python está en el PATH
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el sistema.
    echo Por favor instala Python desde https://www.python.org/ y asegurate
    echo de marcar la casilla "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Ejecutar la aplicacion
python run.py

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] La aplicacion se ha detenido con codigo de error %errorlevel%.
    pause
)
