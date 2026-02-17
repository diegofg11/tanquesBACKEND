"""
Módulo de configuración de logging.

Define la configuración para el sistema de logs de la aplicación,
especificando formatos y manejadores para la salida por consola.
"""
import logging
import logging.config
import sys

# Configuración de Logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {  # Nuestro logger principal
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "app.database": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def setup_logging() -> None:
    """
    Inicializa la configuración de logging de la aplicación.
    
    Aplica la configuración definida en LOGGING_CONFIG.
    """
    logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene una instancia de logger con el nombre especificado.

    Args:
        name (str): El nombre del logger (ej: 'app.services').

    Returns:
        logging.Logger: La instancia del logger configurado.
    """
    return logging.getLogger(name)
