"""
Módulo principal de la aplicación FastAPI.
Configura la instancia de la aplicación, los middlewares CORS y las rutas.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from app.core.logger import setup_logging, get_logger
from app.db_sql import Base, engine
from app.api import users, dashboard, events, audit

# Crear tablas de base de datos local (Auditoría)
Base.metadata.create_all(bind=engine)

# Configurar Logging al inicio
setup_logging()
logger = get_logger("app")

# --- INSTANCIA PRINCIPAL ---
app = FastAPI(
    title="Tanques API",
    description="API REST para el juego de Tanques (Single Player) utilizando Firebase Firestore como backend.",
    version="1.0.0",
    docs_url=None,  # Desactivamos los docs por defecto para personalizarlos (Solución para Render)
    redoc_url=None
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
app.include_router(events.router)
app.include_router(audit.router)

# Servir archivos estáticos para el Dashboard
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- MIS MANEJADORES DE ERRORES ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Maneja errores de validación de datos de entrada (Pydantic).
    Retorna un JSON con el detalle del error y un mensaje amigable.
    """

    logger.warning(f"Error Validación: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"message": "He detectado un error de validación", "detalle": exc.errors()},
    )

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    """
    Maneja excepciones genéricas no capturadas.
    Retorna un error 500 con el detalle de la excepción (útil para depuración).
    """

    logger.error(f"Error No Manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Ha petado algo interno", "detalle": str(exc)},
    )

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Sirve una versión personalizada de Swagger UI.
    Útil cuando los CDNs por defecto fallan o se requiere personalización.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """
    Sirve la documentación ReDoc de la API.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/dashboard")
async def get_dashboard():
    """
    Sirve el archivo HTML principal del Dashboard estático.
    """
    from fastapi.responses import FileResponse
    return FileResponse("static/dashboard/index.html")

@app.get("/")
async def root():
    """
    Punto de entrada raíz de la API.
    Informa sobre el estado y las URLs de documentación y dashboard.
    """

    logger.info("Acceso a root endpoint")
    return {
        "mensaje": "¡Mi API de Tanques (Single Player) con Firebase está en marcha!",
        "doc_url": "/docs",
        "dashboard_url": "/dashboard"
    }
