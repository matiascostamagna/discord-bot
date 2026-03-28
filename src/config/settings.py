"""
Configuration module - Carga y gestiona todas las variables de entorno
"""
from pydantic import BaseSettings, Field
from typing import Optional
import os
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # Discord
    discord_token: str = Field(..., env="DISCORD_TOKEN")
    discord_prefix: str = Field("/", env="DISCORD_PREFIX")
    
    # Database
    database_url: str = Field(
        "sqlite:///./musicbot.db",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(False, env="DATABASE_ECHO")
    
    # Spotify
    spotify_client_id: str = Field(..., env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(..., env="SPOTIFY_CLIENT_SECRET")
    enable_spotify: bool = Field(True, env="ENABLE_SPOTIFY")
    
    # YouTube
    youtube_api_key: Optional[str] = Field(None, env="YOUTUBE_API_KEY")
    enable_youtube: bool = Field(True, env="ENABLE_YOUTUBE")
    
    # Lavalink
    lavalink_host: str = Field("localhost", env="LAVALINK_HOST")
    lavalink_port: int = Field(2333, env="LAVALINK_PORT")
    lavalink_password: str = Field("youshallnotpass", env="LAVALINK_PASSWORD")
    
    # Environment
    node_env: str = Field("development", env="NODE_ENV")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Performance
    cache_ttl: int = Field(3600, env="CACHE_TTL")
    max_queue_size: int = Field(500, env="MAX_QUEUE_SIZE")
    
    # Sentry (optional)
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    
    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Devuelve True si está en producción"""
        return self.node_env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Devuelve True si está en desarrollo"""
        return self.node_env.lower() == "development"
    
    @property
    def lavalink_url(self) -> str:
        """URL del servidor Lavalink"""
        return f"ws://{self.lavalink_host}:{self.lavalink_port}"


# Instancia global de settings
settings = Settings()

# Validación en tiempo de carga
if not settings.discord_token:
    raise ValueError("⚠️  DISCORD_TOKEN no está configurado en .env")

if not settings.spotify_client_id or not settings.spotify_client_secret:
    raise ValueError("⚠️  Credenciales de Spotify no están configuradas")
