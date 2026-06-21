from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

from config import Config, logger
from models import PasswordRequest, PasswordResponse, ErrorResponse
from security import PasswordGenerator, PasswordStrengthValidator


# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

app = FastAPI(
    title=Config.APP_TITLE,
    description=Config.APP_DESCRIPTION,
    version=Config.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================================
# MIDDLEWARE: CORS (Cross-Origin Resource Sharing)
# ============================================================================
# Configuración restrictiva: solo orígenes permitidos pueden hacer requests

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=Config.CORS_ALLOW_METHODS,
    allow_headers=Config.CORS_ALLOW_HEADERS,
)

# ============================================================================
# MIDDLEWARE: Rate Limiting
# ============================================================================
# Limita a 30 requests por minuto por dirección IP para prevenir abuso

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler personalizado para excepciones de rate limiting.
    Devuelve una respuesta JSON estructurada.
    """
    logger.warning(f"Rate limit excedido para IP: {get_remote_address(request)}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Demasiadas solicitudes. Máximo 30 por minuto.",
            "status_code": 429
        }
    )


# ============================================================================
# MIDDLEWARE: Security Headers
# ============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Agrega cabeceras de seguridad HTTP a todas las respuestas.
    
    - Cache-Control: no-store (previene cacheo de respuestas sensibles)
    - X-Content-Type-Options: nosniff (previene MIME sniffing)
    - X-Frame-Options: DENY (previene clickjacking)
    - Referrer-Policy: no-referrer (no envía referrer)
    - Strict-Transport-Security: HTTPS obligatorio por 1 año
    """
    response = await call_next(request)
    
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# ============================================================================
# RUTAS / ENDPOINTS
# ============================================================================

@app.get(
    "/",
    tags=["Info"],
    summary="Información de la API",
    response_description="Mensaje de bienvenida"
)
async def root():
    """
    Endpoint raíz. Devuelve información sobre la API.
    
    Útil para verificar que el servidor está activo.
    """
    return {
        "message": "Bienvenido al Generador Seguro de Contraseñas",
        "version": Config.APP_VERSION,
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Health check",
    response_description="Estado del servidor"
)
async def health_check():
    """
    Endpoint de health check. Devuelve el estado de disponibilidad del servidor.
    
    Útil para monitoreo y balanceadores de carga.
    """
    return {"status": "healthy", "version": Config.APP_VERSION}


@app.post(
    "/api/v1/password",
    response_model=PasswordResponse,
    status_code=status.HTTP_200_OK,
    tags=["Password Generation"],
    summary="Generar contraseña segura",
    response_description="Contraseña generada con métricas de fuerza",
    responses={
        200: {
            "description": "Contraseña generada exitosamente",
            "model": PasswordResponse
        },
        400: {
            "description": "Parámetros inválidos",
            "model": ErrorResponse
        },
        429: {
            "description": "Límite de tasa excedido (máximo 30 por minuto)"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
@limiter.limit(Config.RATE_LIMIT)
async def generate_password(
    request: Request,
    payload: PasswordRequest
) -> PasswordResponse:
    """
    Endpoint principal: genera una contraseña segura.
    
    Flujo de ejecución:
    1. Validación automática de schema con Pydantic (ocurre implícitamente)
    2. Construcción dinámica del alfabeto según parámetros
    3. Generación criptográfica con secrets.choice() (CSPRNG)
    4. Cálculo de entropía de Shannon
    5. Clasificación de fortaleza según NIST SP 800-63B
    6. Logging de metadatos (sin exponer la contraseña)
    7. Devolución de respuesta JSON tipada
    
    Args:
        request: Objeto de solicitud HTTP (para rate limiting)
        payload: Esquema PasswordRequest validado por Pydantic
    
    Returns:
        PasswordResponse: Contraseña + métricas de fuerza
    
    Raises:
        HTTPException 400: Si los parámetros no son válidos
        HTTPException 500: Si ocurre un error interno
    """
    
    try:
        # Log de entrada (sin detalles sensibles)
        remote_ip = get_remote_address(request)
        logger.info(
            f"Solicitud recibida desde {remote_ip}: "
            f"longitud={payload.length}, "
            f"mayus={payload.useUppercase}, "
            f"minus={payload.useLowercase}, "
            f"digs={payload.useDigits}, "
            f"syms={payload.useSymbols}"
        )
        
        # PASO 1: Generar contraseña
        password = PasswordGenerator.generate(
            length=payload.length,
            use_uppercase=payload.useUppercase,
            use_lowercase=payload.useLowercase,
            use_digits=payload.useDigits,
            use_symbols=payload.useSymbols,
            exclude_ambiguous=payload.excludeAmbiguous
        )
        
        # PASO 2: Construir alfabeto para calcular tamaño (necesario para entropía)
        alphabet, alphabet_size = PasswordGenerator.build_alphabet(
            use_uppercase=payload.useUppercase,
            use_lowercase=payload.useLowercase,
            use_digits=payload.useDigits,
            use_symbols=payload.useSymbols,
            exclude_ambiguous=payload.excludeAmbiguous
        )
        
        # PASO 3: Validar fortaleza y calcular métricas
        validation_result = PasswordStrengthValidator.validate(
            length=payload.length,
            alphabet_size=alphabet_size
        )
        
        # PASO 4: Construir respuesta
        response = PasswordResponse(
            password=password,
            length=payload.length,
            entropyBits=validation_result["entropyBits"],
            strength=validation_result["strength"],
            alphabetSize=alphabet_size
        )
        
        logger.info(
            f"Respuesta enviada a {remote_ip}: "
            f"strength={response.strength}, "
            f"entropia={response.entropyBits} bits"
        )
        
        return response
    
    except ValueError as ve:
        # Errores de validación de lógica de negocio
        logger.warning(f"Validación fallida: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parámetros inválidos: {str(ve)}"
        )
    
    except Exception as e:
        # Errores inesperados
        logger.error(f"Error interno en generación de contraseña: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# ============================================================================
# MANEJADOR DE ERRORES 404
# ============================================================================

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """Maneja rutas no encontradas."""
    logger.warning(f"Ruta no encontrada: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Ruta no encontrada", "status_code": 404}
    )


# ============================================================================
# EJECUCIÓN DE LA APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    logger.info(
        f"Iniciando {Config.APP_TITLE} (v{Config.APP_VERSION}) "
        f"en modo {Config.ENVIRONMENT}"
    )
    logger.info(f"CORS permitido desde: {Config.CORS_ORIGINS}")
    logger.info(f"Rate limit: {Config.RATE_LIMIT}")
    logger.info(f"Servidor escuchando en http://{Config.HOST}:{Config.PORT}")
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
        log_level="info"
    )