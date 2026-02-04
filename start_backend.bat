@echo off
echo Iniciando Servidor de Tanques Backend...
cd /d %~dp0
if not exist venv (
    echo Error: No se encontro la carpeta 'venv'. Asegurate de estar en la raiz de tanquesBACKEND.
    pause
    exit /b
)
echo Activando entorno virtual...
call venv\Scripts\activate
echo Iniciando Uvicorn en http://127.0.0.1:8000...
echo Presiona Ctrl+C para detener el servidor.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
