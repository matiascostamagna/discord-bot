"""
Models - SQLAlchemy ORM models con timestamps automáticos
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from uuid import uuid4
import uuid as uuid_lib
from config.database import Base

# Base model con timestamps automáticos
class BaseModel(Base):
    """Modelo base con ID, created_at, updated_at"""
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False
    )
    created_at = Column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        default=datetime.utcnow,
        nullable=False
    )

# ==================== USER MODELS ====================

class User(BaseModel):
    """Modelo de usuario Discord"""
    __tablename__ = "users"
    
    discord_id = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    
    # Preferencias
    language = Column(String(5), default="es_ES")
    timezone = Column(String(50), default="UTC")
    is_banned = Column(Boolean, default=False)
    
    # Relaciones
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")
    stats = relationship("UserStats", back_populates="user", cascade="all, delete-orphan", uselist=False)
    
    def __repr__(self):
        return f"<User {self.username}>"

class UserStats(BaseModel):
    """Estadísticas de usuario"""
    __tablename__ = "user_stats"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    total_songs_played = Column(Integer, default=0)
    total_minutes_played = Column(Integer, default=0)
    favorite_genre = Column(String(100), nullable=True)
    most_played_artist = Column(String(255), nullable=True)
    
    # Relación
    user = relationship("User", back_populates="stats")
    
    def __repr__(self):
        return f"<UserStats user_id={self.user_id}>"

# ==================== PLAYLIST MODELS ====================

class Playlist(BaseModel):
    """Playlist guardada por usuario"""
    __tablename__ = "playlists"
    
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    track_count = Column(Integer, default=0)
    
    # Relaciones
    owner = relationship("User", back_populates="playlists")
    tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('owner_id', 'name', name='uq_playlist_owner_name'),
    )
    
    def __repr__(self):
        return f"<Playlist {self.name}>"

class PlaylistTrack(BaseModel):
    """Pista en una playlist"""
    __tablename__ = "playlist_tracks"
    
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.id"), nullable=False)
    track_id = Column(String(255), nullable=False)  # Spotify track ID o URL
    title = Column(String(500), nullable=False)
    artist = Column(String(255), nullable=False)
    duration_ms = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)  # Posición en la playlist
    
    # Relación
    playlist = relationship("Playlist", back_populates="tracks")
    
    __table_args__ = (
        UniqueConstraint('playlist_id', 'track_id', name='uq_playlist_track'),
    )
    
    def __repr__(self):
        return f"<PlaylistTrack {self.title}>"

# ==================== QUEUE MODELS ====================

class QueueItem(BaseModel):
    """Item en la cola de reproducción"""
    __tablename__ = "queue_items"
    
    guild_id = Column(String(20), nullable=False, index=True)
    track_id = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    artist = Column(String(255), nullable=False)
    duration_ms = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)  # 'spotify', 'youtube', 'soundcloud'
    requested_by = Column(String(20), nullable=False)  # Discord user ID
    position = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<QueueItem {self.title} @{self.guild_id}>"

# ==================== TRACK CACHE ====================

class TrackCache(BaseModel):
    """Cache de canciones para búsquedas rápidas"""
    __tablename__ = "track_cache"
    
    track_id = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    artist = Column(String(255), nullable=False)
    album = Column(String(255), nullable=True)
    duration_ms = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)
    metadata = Column(JSON, nullable=True)  # Datos adicionales
    last_accessed = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TrackCache {self.title}>"

# ==================== PLAY HISTORY ====================

class PlayHistory(BaseModel):
    """Historial de reproducción"""
    __tablename__ = "play_history"
    
    guild_id = Column(String(20), nullable=False, index=True)
    track_id = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    artist = Column(String(255), nullable=False)
    played_by = Column(String(20), nullable=False)  # Discord user ID
    duration_ms = Column(Integer, nullable=False)
    played_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlayHistory {self.title}>"
