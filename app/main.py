"""
Módulo principal de la aplicación FastAPI.
Configura la instancia de la aplicación, los middlewares CORS y las rutas.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api import users

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

# Aquí conecto mis rutas de usuarios
app.include_router(users.router)

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

@app.get("/")
async def root():
    return {
        "mensaje": "¡Mi API de Tanques (Single Player) con Firebase está en marcha!",
        "doc_url": "/docs"
    }
