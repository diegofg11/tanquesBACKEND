@echo off
echo ==========================================
echo   INSTALADOR DE DEPENDENCIAS - TANQUES
echo ==========================================
echo.

:: 1. Comprobar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta en el PATH o no esta instalado.
    echo Por favor, instala Python desde python.org y marca la casilla "Add Python to PATH".
    pause
    exit /b
)

:: 2. Crear entorno virtual (opcional pero recomendado)
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

:: 3. Instalar librerias
echo Instalando/Actualizando librerias (FastAPI, Uvicorn, Firebase)...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install fastapi uvicorn firebase-admin

echo.
echo ==========================================
echo   INSTALACION COMPLETADA
echo   Ya puedes iniciar el server desde Unity.
echo ==========================================
pause
