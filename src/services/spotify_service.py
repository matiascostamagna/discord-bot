"""
Spotify Service - Integración con Spotify API usando spotipy
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from middleware.logger import logger
from config.settings import settings
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class Track:
    """Clase para representar una canción"""
    id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    url: str
    image_url: Optional[str] = None

class SpotifyService:
    """Servicio para interactuar con Spotify API"""
    
    def __init__(self):
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=settings.spotify_client_id,
            client_secret=settings.spotify_client_secret
        )
        self.client = spotipy.Spotify(
            client_credentials_manager=self.client_credentials_manager
        )
        logger.info("✅ Spotify Service inicializado")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def search_track(self, query: str, limit: int = 5) -> List[Track]:
        """
        Buscar canciones en Spotify
        
        Args:
            query: Término de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de Track objects
        """
        try:
            logger.debug(f"Buscando en Spotify: {query}")
            results = self.client.search(q=query, type='track', limit=limit)
            
            tracks = []
            for item in results['tracks']['items']:
                track = Track(
                    id=item['id'],
                    title=item['name'],
                    artist=", ".join([artist['name'] for artist in item['artists']]),
                    album=item['album']['name'],
                    duration_ms=item['duration_ms'],
                    url=item['external_urls']['spotify'],
                    image_url=item['album']['images'][0]['url'] if item['album']['images'] else None
                )
                tracks.append(track)
            
            logger.info(f"✅ Encontradas {len(tracks)} canciones en Spotify")
            return tracks
            
        except Exception as e:
            logger.exception(f"❌ Error buscando en Spotify: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_track(self, track_id: str) -> Optional[Track]:
        """
        Obtener información de una canción por ID
        
        Args:
            track_id: ID de la canción en Spotify
            
        Returns:
            Track object o None
        """
        try:
            logger.debug(f"Obteniendo track Spotify: {track_id}")
            item = self.client.track(track_id)
            
            track = Track(
                id=item['id'],
                title=item['name'],
                artist=", ".join([artist['name'] for artist in item['artists']]),
                album=item['album']['name'],
                duration_ms=item['duration_ms'],
                url=item['external_urls']['spotify'],
                image_url=item['album']['images'][0]['url'] if item['album']['images'] else None
            )
            
            return track
            
        except Exception as e:
            logger.exception(f"❌ Error obteniendo track de Spotify: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_playlist(self, playlist_id: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        """
        Obtener playlist de Spotify
        
        Args:
            playlist_id: ID de la playlist
            limit: Número de canciones a obtener
            
        Returns:
            Dict con información de la playlist
        """
        try:
            logger.debug(f"Obteniendo playlist Spotify: {playlist_id}")
            
            playlist = self.client.playlist(playlist_id)
            tracks = []
            
            results = self.client.playlist_tracks(playlist_id, limit=limit)
            for item in results['items']:
                if item['track']:
                    track_info = item['track']
                    track = Track(
                        id=track_info['id'],
                        title=track_info['name'],
                        artist=", ".join([artist['name'] for artist in track_info['artists']]),
                        album=track_info['album']['name'],
                        duration_ms=track_info['duration_ms'],
                        url=track_info['external_urls']['spotify'],
                        image_url=track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
                    )
                    tracks.append(track)
            
            return {
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'image': playlist['images'][0]['url'] if playlist['images'] else None,
                'track_count': playlist['tracks']['total'],
                'tracks': tracks
            }
            
        except Exception as e:
            logger.exception(f"❌ Error obteniendo playlist de Spotify: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_artist(self, artist_id: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Obtener información del artista y sus top tracks
        
        Args:
            artist_id: ID del artista
            limit: Número de top tracks
            
        Returns:
            Dict con información del artista
        """
        try:
            logger.debug(f"Obteniendo artista Spotify: {artist_id}")
            
            artist = self.client.artist(artist_id)
            top_tracks = self.client.artist_top_tracks(artist_id, country='US')
            
            tracks = []
            for item in top_tracks['tracks'][:limit]:
                track = Track(
                    id=item['id'],
                    title=item['name'],
                    artist=", ".join([a['name'] for a in item['artists']]),
                    album=item['album']['name'],
                    duration_ms=item['duration_ms'],
                    url=item['external_urls']['spotify'],
                    image_url=item['album']['images'][0]['url'] if item['album']['images'] else None
                )
                tracks.append(track)
            
            return {
                'name': artist['name'],
                'image': artist['images'][0]['url'] if artist['images'] else None,
                'genres': artist['genres'],
                'followers': artist['followers']['total'],
                'popularity': artist['popularity'],
                'top_tracks': tracks
            }
            
        except Exception as e:
            logger.exception(f"❌ Error obteniendo artista de Spotify: {e}")
            return None

# Instancia global del servicio
spotify_service = SpotifyService()
