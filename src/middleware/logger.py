"""
Logger configuration - Sistema de logging centralizado con Loguru
"""
import sys
from loguru import logger as _logger
from pathlib import Path
from config.settings import settings

# Configurar directorio de logs
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Remover handler por defecto
_logger.remove()

# Handler para consola
_logger.add(
    sys.stdout,
    format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True
)

# Handler para archivo (solo en producción)
if settings.is_production:
    _logger.add(
        LOG_DIR / "bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="500 MB",  # Rotar cada 500 MB
        retention="7 days",  # Mantener 7 días de logs
        compression="zip"
    )
    
    # Log de errores separado
    _logger.add(
        LOG_DIR / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="500 MB",
        retention="30 days"
    )

logger = _logger

# Decorador para logging automático de funciones
def log_async(func):
    """Decorador para loguear funciones async"""
    async def wrapper(*args, **kwargs):
        logger.debug(f"Ejecutando {func.__name__} con args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"{func.__name__} completado exitosamente")
            return result
        except Exception as e:
            logger.exception(f"Error en {func.__name__}: {e}")
            raise
    return wrapper
