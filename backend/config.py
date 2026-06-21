import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os


class Config:
    """Configuración central de la aplicación."""
    
    # Información de la API
    APP_TITLE = "Generador Seguro de Contraseñas"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "API REST para generar contraseñas de forma segura utilizando CSPRNG"
    
    # Entorno
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # Servidor
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    
    # CORS - Configuración restrictiva
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    
    # Rate Limiting
    RATE_LIMIT = "30/minute"  # Máximo 30 solicitudes por minuto por IP
    
    # Validación de contraseñas
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_DEFAULT_LENGTH = 16
    
    # Alfabetos disponibles
    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    DIGITS = "0123456789"
    SYMBOLS = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    
    # Caracteres ambiguos (para excluir si lo solicita el usuario)
    AMBIGUOUS_CHARS = "il1Lo0O"
    
    # Clasificación de fuerza según entropía en bits
    STRENGTH_THRESHOLDS = {
        "very_weak": (0, 28),
        "weak": (28, 36),
        "reasonable": (36, 60),
        "strong": (60, 128),
        "very_strong": (128, float('inf'))
    }


def setup_logging():
    """
    Configura el sistema de logging de la aplicación.
    
    - Logs en archivo (rotating file handler)
    - Logs en consola (para desarrollo)
    - NO registra contraseñas ni datos sensibles
    """
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    logger = logging.getLogger("password_generator")
    logger.setLevel(logging.INFO)
    
    # Formato de log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler: archivo rotativo (max 10MB, mantiene 5 archivos)
    file_handler = RotatingFileHandler(
        filename="logs/password_generator.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler: consola (solo en desarrollo)
    if Config.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# Instancia global de logger
logger = setup_logging()