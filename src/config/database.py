"""
Database configuration - SQLAlchemy async setup con PostgreSQL/SQLite
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
from config.settings import settings
from middleware.logger import logger

# Base para todos los modelos
Base = declarative_base()

# Convertir URL a async
def get_async_database_url() -> str:
    """Convierte DATABASE_URL a URL async"""
    url = settings.database_url
    
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    
    return url

# Crear engine async
async_database_url = get_async_database_url()

engine = create_async_engine(
    async_database_url,
    echo=settings.database_echo,
    future=True,
    # Pool configuration para PostgreSQL
    poolclass=QueuePool if "postgresql" in async_database_url else NullPool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Validar conexiones antes de usar
    pool_recycle=3600,   # Reciclar conexiones cada hora
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

async def get_session() -> AsyncSession:
    """Obtener sesión de base de datos"""
    async with async_session_maker() as session:
        yield session

@asynccontextmanager
async def get_db_session():
    """Context manager para sesiones de BD"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.exception(f"Error en sesión BD: {e}")
            raise
        finally:
            await session.close()

async def init_db():
    """Inicializar base de datos - crear todas las tablas"""
    logger.info("Inicializando base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Base de datos inicializada")

async def close_db():
    """Cerrar conexión a la base de datos"""
    logger.info("Cerrando conexión a BD...")
    await engine.dispose()
    logger.info("✅ Conexión a BD cerrada")
