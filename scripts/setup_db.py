"""
Setup Database Script - Inicializar BD y crear tablas
"""
import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.database import init_db, engine
from config.settings import settings
from middleware.logger import logger

async def setup_database():
    """Inicializar base de datos"""
    try:
        logger.info(f"🔧 Inicializando BD: {settings.database_url}")
        
        # Crear todas las tablas
        await init_db()
        
        logger.info("✅ Base de datos configurada correctamente")
        
    except Exception as e:
        logger.exception(f"❌ Error configurando BD: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

async def reset_database():
    """Reset completo de la base de datos"""
    try:
        logger.warning("⚠️  RESETEANDO BASE DE DATOS...")
        
        from config.database import Base
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("✅ Todas las tablas eliminadas")
        
        await init_db()
        logger.info("✅ Base de datos reseteada")
        
    except Exception as e:
        logger.exception(f"❌ Error reseteando BD: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        asyncio.run(reset_database())
    else:
        asyncio.run(setup_database())
