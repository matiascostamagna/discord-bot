"""
Test Queue Service - Tests unitarios para MusicQueue
"""
import pytest
from services.queue_service import MusicQueue, QueueTrack, QueueMode


class TestMusicQueue:
    """Tests para la clase MusicQueue"""
    
    def test_queue_initialization(self, music_queue):
        """Test: Inicializar queue vacía"""
        assert len(music_queue) == 0
        assert music_queue.current_track is None
        assert music_queue.is_playing is False
    
    def test_add_single_track(self, music_queue, sample_track):
        """Test: Agregar una canción"""
        result = music_queue.add_track(sample_track)
        
        assert result is True
        assert len(music_queue) == 1
        assert music_queue.queue[0] == sample_track
    
    def test_add_multiple_tracks(self, music_queue, sample_tracks):
        """Test: Agregar múltiples canciones"""
        added = music_queue.add_multiple_tracks(sample_tracks)
        
        assert added == len(sample_tracks)
        assert len(music_queue) == len(sample_tracks)
    
    def test_queue_max_size(self, sample_track):
        """Test: No agregar más del máximo permitido"""
        queue = MusicQueue(max_size=2)
        
        queue.add_track(sample_track)
        queue.add_track(sample_track)
        result = queue.add_track(sample_track)
        
        assert result is False
        assert len(queue) == 2
    
    def test_next_track(self, music_queue, sample_tracks):
        """Test: Obtener siguiente canción"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        first_track = music_queue.next()
        
        assert first_track == sample_tracks[0]
        assert music_queue.current_track == sample_tracks[0]
        assert len(music_queue) == len(sample_tracks) - 1
    
    def test_skip(self, music_queue, sample_tracks):
        """Test: Saltar canción"""
        music_queue.add_multiple_tracks(sample_tracks)
        music_queue.next()
        
        skipped = music_queue.skip()
        
        assert skipped == sample_tracks[1]
        assert len(music_queue) == len(sample_tracks) - 2
    
    def test_remove_track(self, music_queue, sample_tracks):
        """Test: Remover canción por posición"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        result = music_queue.remove(0)
        
        assert result is True
        assert len(music_queue) == len(sample_tracks) - 1
    
    def test_remove_invalid_position(self, music_queue, sample_tracks):
        """Test: Remover posición inválida"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        result = music_queue.remove(100)
        
        assert result is False
        assert len(music_queue) == len(sample_tracks)
    
    def test_shuffle(self, music_queue, sample_tracks):
        """Test: Mezclar cola"""
        import copy
        
        music_queue.add_multiple_tracks(sample_tracks)
        original_order = copy.deepcopy(music_queue.queue)
        
        music_queue.shuffle()
        
        # La probabilidad de que sea igual después de shuffle es mínima
        # (pero teóricamente posible, por eso no es un assert 100% seguro)
        assert len(music_queue) == len(original_order)
    
    def test_clear_queue(self, music_queue, sample_tracks):
        """Test: Limpiar cola"""
        music_queue.add_multiple_tracks(sample_tracks)
        music_queue.next()
        
        music_queue.clear()
        
        assert len(music_queue) == 0
        assert music_queue.current_track is None
        assert music_queue.is_playing is False
    
    def test_queue_mode_normal(self, music_queue, sample_tracks):
        """Test: Modo normal"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        assert music_queue.mode == QueueMode.NORMAL
    
    def test_queue_mode_loop_track(self, music_queue, sample_tracks):
        """Test: Modo repetir canción"""
        music_queue.add_multiple_tracks(sample_tracks)
        music_queue.next()
        
        music_queue.set_mode(QueueMode.LOOP_TRACK)
        
        next_track = music_queue.next()
        
        assert next_track == sample_tracks[0]  # Misma canción
    
    def test_get_stats(self, music_queue, sample_tracks):
        """Test: Obtener estadísticas"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        stats = music_queue.get_stats()
        
        assert stats['queue_size'] == len(sample_tracks)
        assert stats['max_size'] == 500
        assert 'total_duration' in stats
    
    def test_get_queue_limit(self, music_queue, sample_tracks):
        """Test: Obtener N primeras canciones"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        limited_queue = music_queue.get_queue(limit=2)
        
        assert len(limited_queue) == 2
        assert limited_queue[0] == sample_tracks[0]
    
    def test_history(self, music_queue, sample_tracks):
        """Test: Historial de reproducción"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        first = music_queue.next()
        second = music_queue.next()
        
        assert len(music_queue.history) == 1
        assert music_queue.history[0] == first
    
    def test_previous(self, music_queue, sample_tracks):
        """Test: Volver a canción anterior"""
        music_queue.add_multiple_tracks(sample_tracks)
        
        music_queue.next()
        music_queue.next()
        previous = music_queue.previous()
        
        assert previous == sample_tracks[0]
