"""
Pytest Configuration - Fixtures y setup para tests
"""
import pytest
import asyncio
from services.queue_service import MusicQueue, QueueTrack
from datetime import datetime


@pytest.fixture
def event_loop():
    """Crear event loop para tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def music_queue():
    """Crear instancia de MusicQueue para tests"""
    return MusicQueue(max_size=100)


@pytest.fixture
def sample_track():
    """Track de ejemplo para tests"""
    return QueueTrack(
        track_id="spotify_123",
        title="Test Song",
        artist="Test Artist",
        duration_ms=180000,
        source="spotify",
        requested_by="123456789",
        url="https://open.spotify.com/track/123",
        image_url="https://example.com/image.jpg"
    )


@pytest.fixture
def sample_tracks(sample_track):
    """Múltiples tracks para tests"""
    tracks = [sample_track]
    for i in range(1, 5):
        track = QueueTrack(
            track_id=f"spotify_{i}",
            title=f"Song {i}",
            artist=f"Artist {i}",
            duration_ms=180000 + (i * 10000),
            source="spotify",
            requested_by="123456789",
            url=f"https://open.spotify.com/track/{i}",
            image_url="https://example.com/image.jpg"
        )
        tracks.append(track)
    return tracks


# Configuración global de pytest
def pytest_configure(config):
    """Configuración inicial de pytest"""
    config.addinivalue_line(
        "markers", "asyncio: marca tests como async"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )
