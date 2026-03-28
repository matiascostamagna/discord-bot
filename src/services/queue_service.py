"""
Queue Service - Gestión de la cola de reproducción
"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
from middleware.logger import logger

class QueueMode(Enum):
    """Modos de reproducción de la cola"""
    NORMAL = "normal"
    LOOP_QUEUE = "loop_queue"  # Repetir toda la cola
    LOOP_TRACK = "loop_track"  # Repetir canción actual

@dataclass
class QueueTrack:
    """Estructura de una canción en la cola"""
    track_id: str
    title: str
    artist: str
    duration_ms: int
    source: str  # 'spotify', 'youtube'
    requested_by: str  # Discord user ID
    url: str
    image_url: Optional[str] = None
    added_at: datetime = field(default_factory=datetime.utcnow)
    
    def __repr__(self):
        return f"{self.title} by {self.artist} ({self.duration_ms}ms)"

class MusicQueue:
    """Gestor de la cola de reproducción"""
    
    def __init__(self, max_size: int = 500):
        self.queue: List[QueueTrack] = []
        self.history: List[QueueTrack] = []
        self.current_track: Optional[QueueTrack] = None
        self.mode: QueueMode = QueueMode.NORMAL
        self.max_size = max_size
        self.is_playing = False
        self.is_paused = False
        logger.info(f"✅ MusicQueue inicializada (max_size={max_size})")
    
    def add_track(self, track: QueueTrack, position: Optional[int] = None) -> bool:
        """
        Agregar canción a la cola
        
        Args:
            track: Track a agregar
            position: Posición específica (None = al final)
            
        Returns:
            True si se agregó, False si la cola está llena
        """
        if len(self.queue) >= self.max_size:
            logger.warning(f"❌ Cola llena (max: {self.max_size})")
            return False
        
        if position is None:
            self.queue.append(track)
            logger.info(f"✅ Track agregado al final: {track}")
        else:
            self.queue.insert(position, track)
            logger.info(f"✅ Track agregado en posición {position}: {track}")
        
        return True
    
    def add_multiple_tracks(self, tracks: List[QueueTrack]) -> int:
        """
        Agregar múltiples canciones a la cola
        
        Args:
            tracks: Lista de tracks
            
        Returns:
            Número de tracks agregados
        """
        added = 0
        for track in tracks:
            if self.add_track(track):
                added += 1
            else:
                logger.warning(f"Cola llena, solo se agregaron {added}/{len(tracks)} tracks")
                break
        
        return added
    
    def next(self) -> Optional[QueueTrack]:
        """
        Obtener siguiente canción y actualizar estado
        
        Returns:
            Siguiente track o None
        """
        if self.current_track:
            self.history.append(self.current_track)
        
        if not self.queue:
            self.current_track = None
            self.is_playing = False
            logger.info("⏹️  Cola vacía")
            return None
        
        # Manejo de modos de repetición
        if self.mode == QueueMode.LOOP_TRACK and self.current_track:
            logger.info(f"🔄 Repetiendo: {self.current_track}")
            return self.current_track
        
        self.current_track = self.queue.pop(0)
        self.is_playing = True
        logger.info(f"▶️  Reproduciendo: {self.current_track}")
        
        return self.current_track
    
    def skip(self) -> Optional[QueueTrack]:
        """Saltar a la siguiente canción"""
        logger.info("⏭️  Skip")
        return self.next()
    
    def previous(self) -> Optional[QueueTrack]:
        """Volver a la canción anterior"""
        if not self.history:
            logger.warning("No hay canciones anteriores")
            return None
        
        if self.current_track:
            self.queue.insert(0, self.current_track)
        
        self.current_track = self.history.pop()
        logger.info(f"⏮️  Volviendo a: {self.current_track}")
        
        return self.current_track
    
    def remove(self, position: int) -> bool:
        """
        Remover una canción por posición
        
        Args:
            position: Índice de la canción
            
        Returns:
            True si se removió, False si posición inválida
        """
        try:
            track = self.queue.pop(position)
            logger.info(f"❌ Track removido: {track}")
            return True
        except IndexError:
            logger.warning(f"Posición inválida: {position}")
            return False
    
    def shuffle(self) -> None:
        """Mezclar la cola"""
        import random
        random.shuffle(self.queue)
        logger.info(f"🔀 Cola mezclada ({len(self.queue)} canciones)")
    
    def clear(self) -> None:
        """Limpiar la cola"""
        count = len(self.queue)
        self.queue.clear()
        self.current_track = None
        self.is_playing = False
        logger.info(f"🗑️  Cola limpiada ({count} canciones removidas)")
    
    def set_mode(self, mode: QueueMode) -> None:
        """Cambiar modo de reproducción"""
        self.mode = mode
        logger.info(f"🔄 Modo cambiado a: {mode.value}")
    
    def get_queue(self, limit: int = 10) -> List[QueueTrack]:
        """
        Obtener los próximos N tracks de la cola
        
        Args:
            limit: Número de tracks a retornar
            
        Returns:
            Lista de tracks
        """
        return self.queue[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la cola"""
        total_duration_ms = sum(t.duration_ms for t in self.queue)
        hours = total_duration_ms // (1000 * 60 * 60)
        minutes = (total_duration_ms % (1000 * 60 * 60)) // (1000 * 60)
        
        return {
            'queue_size': len(self.queue),
            'max_size': self.max_size,
            'current_track': str(self.current_track) if self.current_track else None,
            'mode': self.mode.value,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'total_duration': f"{hours}h {minutes}m",
            'history_count': len(self.history)
        }
    
    def __len__(self) -> int:
        return len(self.queue)
    
    def __repr__(self) -> str:
        return f"<MusicQueue size={len(self.queue)} current={self.current_track}>"
