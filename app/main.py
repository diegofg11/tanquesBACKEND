"""
Módulo principal de la aplicación FastAPI.
Configura la instancia de la aplicación, los middlewares CORS y las rutas.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api import users, dashboard

# --- INSTANCIA PRINCIPAL ---
app = FastAPI(
    title="Tanques API",
    description="API REST para el juego de Tanques (Single Player) utilizando Firebase Firestore como backend.",
    version="1.0.0"
)

# ME DOY PERMISOS DE CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aquí conecto mis rutas
app.include_router(users.router)
app.include_router(dashboard.router)

# Servir archivos estáticos para el Dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- MIS MANEJADORES DE ERRORES ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "He detectado un error de validación", "detalle": exc.errors()},
    )

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Ha petado algo interno", "detalle": str(exc)},
    )

@app.get("/dashboard")
async def get_dashboard():
    from fastapi.responses import FileResponse
    return FileResponse("static/dashboard/index.html")

@app.get("/")
async def root():
    return {
        "mensaje": "¡Mi API de Tanques (Single Player) con Firebase está en marcha!",
        "doc_url": "/docs",
        "dashboard_url": "/dashboard"
    }
