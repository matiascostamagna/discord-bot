# 🏗️ Arquitectura del Music Bot Pro

## Visión General

El Music Bot es una aplicación modular basada en **Discord.py** que integra:
- **Spotify API** para búsqueda y metadatos
- **Lavalink** para reproducción de audio profesional
- **PostgreSQL/SQLite** para persistencia
- **Async/await** para máximo rendimiento

---

## 🎯 Capas de Arquitectura

### 1. Capa de Presentación (Discord)
```
Discord Server
      ↓
   Slash Commands (/play, /queue, /skip, etc)
      ↓
   Bot.py (MusicBot class)
```

### 2. Capa de Aplicación (Cogs)
```
Cogs/
├── music.py          → Comandos de reproducción
├── playlist.py       → Gestión de playlists
├── admin.py          → Admin commands
└── stats.py          → Estadísticas
```

### 3. Capa de Servicios
```
Services/
├── spotify_service.py    → Búsqueda y metadatos
├── queue_service.py      → Lógica de cola
├── music_service.py      → Reproducción
└── search_service.py     → Búsqueda unificada
```

### 4. Capa de Datos
```
Models/
├── User              → Usuarios Discord
├── Playlist          → Playlists guardadas
├── PlaylistTrack     → Canciones en playlists
├── QueueItem         → Items en cola
├── TrackCache        → Cache de canciones
└── PlayHistory       → Historial
```

### 5. Capa de Infraestructura
```
Config/
├── settings.py       → Variables de entorno
└── database.py       → SQLAlchemy + conexiones

Middleware/
├── logger.py         → Logging centralizado
└── error_handler.py  → Manejo de errores
```

---

## 🔄 Flujo de Datos

### Escenario: Usuario ejecuta /play

```
1. Discord UI
   └─→ Usuario escribe: /play "Bohemian Rhapsody Queen"

2. Bot.py (MusicBot)
   └─→ interaction.response.defer()
   └─→ Valida que usuario esté en canal de voz

3. Cogs/music.py (Music.play)
   └─→ spotify_service.search_track("Bohemian Rhapsody Queen")

4. Services/spotify_service.py
   └─→ self.client.search(q=query, type='track', limit=1)
   └─→ Retorna: Track object con metadata

5. Services/queue_service.py
   └─→ MusicQueue.add_track(QueueTrack)
   └─→ Guarda en memoria la canción

6. Database (opcional)
   └─→ PlayHistory.add() - guardar en BD
   └─→ TrackCache.add() - cachear para futuras búsquedas

7. Discord Response
   └─→ Embed con info de la canción
   └─→ "✅ Canción agregada a la cola"
```

---

## 💾 Diagrama de Base de Datos

```sql
users
  ├─ id (UUID)
  ├─ discord_id (String unique)
  ├─ username
  └─ created_at

user_stats
  ├─ id (UUID)
  ├─ user_id (FK → users)
  ├─ total_songs_played
  └─ most_played_artist

playlists
  ├─ id (UUID)
  ├─ owner_id (FK → users)
  ├─ name
  ├─ description
  └─ is_public

playlist_tracks
  ├─ id (UUID)
  ├─ playlist_id (FK → playlists)
  ├─ track_id (String)
  ├─ title
  ├─ artist
  └─ position

track_cache
  ├─ id (UUID)
  ├─ track_id (String unique)
  ├─ title
  ├─ artist
  ├─ metadata (JSON)
  └─ last_accessed

play_history
  ├─ id (UUID)
  ├─ guild_id (String)
  ├─ track_id (String)
  ├─ played_by (String)
  └─ played_at

queue_items (In-Memory)
  ├─ track_id
  ├─ title
  ├─ artist
  ├─ requested_by
  └─ position
```

---

## 🎵 Flujo de Reproducción

```
User: /play "Song Name"
  ↓
Search en Spotify
  ↓
Get Track metadata (title, artist, duration, URL)
  ↓
Create QueueTrack object
  ↓
Add to MusicQueue (en memoria)
  ↓
Send Response to Discord
  ↓
[Cuando se reproduce]
  ↓
Lavalink recibe petición
  ↓
Descarga de YouTube Music (ya que Spotify es audio-only)
  ↓
Transmite audio a canal de voz
  ↓
Update PlayHistory en BD
```

---

## 🔌 Integraciones Externas

### Spotify API
- **Endpoint:** https://api.spotify.com/v1
- **Auth:** OAuth 2.0 Client Credentials
- **Uso:** Búsqueda de canciones, metadatos (artist, album, duration)
- **Rate Limit:** 429 si se excede

### Lavalink Server
- **Protocol:** WebSocket JSON
- **Port:** 2333
- **Auth:** password (youshallnotpass)
- **Funciones:** 
  - Descarga de audio
  - Transmisión a Discord
  - Procesamiento de filtros

### Discord.py
- **API:** Discord REST + WebSocket
- **Auth:** Bot token
- **Eventos:** message, interaction, voice_state_update

---

## 🧪 Estrategia de Testing

### Unit Tests
```
tests/
├── test_queue_service.py      → Test MusicQueue logic
├── test_spotify_service.py    → Mock Spotify API
└── test_search_service.py     → Search functionality
```

**Ejemplo:**
```python
def test_add_track(music_queue, sample_track):
    result = music_queue.add_track(sample_track)
    assert result is True
    assert len(music_queue) == 1
```

### Integration Tests
- Probar bot con servidor Discord real (opcional)
- Probar Lavalink connection

### Load Testing
- Múltiples usuarios simultáneamente
- Max queue size bajo carga

---

## 🔐 Seguridad

### Validación de Entrada
```python
# En cada comando
@app_commands.command()
async def play(self, interaction, query: str):
    # Validar que query no esté vacío
    if not query or len(query) > 500:
        return error
    
    # Escapar caracteres especiales
    # Validar tipo de datos
```

### Control de Acceso
```python
# Por rol
@commands.check_any(
    commands.has_role("DJ"),
    commands.has_permissions(administrator=True)
)
async def admin_command(ctx):
    pass
```

### Protección de Tokens
```
# .env nunca se commitea
# DISCORD_TOKEN nunca en logs
# SPOTIFY_SECRET nunca en respuestas
```

---

## 📊 Monitoreo y Logging

### Levels
- **DEBUG:** info detallada para desarrollo
- **INFO:** eventos importantes (bot ready, commands)
- **WARNING:** situaciones inusuales
- **ERROR:** errores recoverable
- **CRITICAL:** fallos del sistema

### Ejemplo
```python
logger.info(f"▶️ Reproduciendo: {track.title}")
logger.warning(f"❌ Cola llena")
logger.exception(f"Error en /play: {e}")
```

---

## 🚀 Escalabilidad

### Actualmente
- ✅ MusicQueue en memoria (rápida)
- ✅ SQLite para desarrollo
- ✅ Spotify API con rate limiting
- ✅ Async/await para concurrencia

### Para Producción
1. **PostgreSQL** en lugar de SQLite
   - Persistencia real
   - Mejor para múltiples instancias

2. **Redis** para caché
   ```python
   # Cachear búsquedas Spotify
   # Evitar queries duplicadas
   ```

3. **Message Queue** (RabbitMQ/Kafka)
   ```
   Evento: /play
   └─→ Queue
   └─→ Worker procesa
   └─→ Responde a Discord
   ```

4. **Múltiples Bots**
   - Load balancer
   - Base de datos compartida

---

## 🔄 Ciclo de Vida del Bot

```
1. Startup
   ├─ Load settings from .env
   ├─ Connect to Database
   ├─ Load Cogs (music, playlist, etc)
   ├─ Connect to Discord
   └─ on_ready() event

2. Running
   ├─ Listen for interactions
   ├─ Process commands
   ├─ Update queue
   └─ Stream audio

3. Shutdown
   ├─ Disconnect voice clients
   ├─ Save pending data
   ├─ Close database
   └─ Disconnect from Discord
```

---

## 📈 Métricas Importantes

```python
# Qué monitorear
- Total de comandos ejecutados
- Tiempo promedio de búsqueda
- Tamaño de cola por servidor
- Errores por tipo
- Uptime del bot
- Latencia a Discord
```

---

## 🛣️ Roadmap

### MVP (Actual)
- ✅ /play (búsqueda Spotify)
- ✅ /queue
- ✅ /skip, /stop
- ✅ Logs centralizados
- ✅ Tests unitarios

### v1.0
- ⏳ Playlists guardadas
- ⏳ Historial de usuario
- ⏳ Comandos admin
- ⏳ Estadísticas
- ⏳ Sistema de permisos

### v2.0
- ⏳ Dashboard web
- ⏳ Recomendaciones
- ⏳ Integración Apple Music
- ⏳ Karaoke mode
- ⏳ Equalizer dinámico

---

## 🔗 Referencias

- Discord.py: https://discordpy.readthedocs.io/
- Lavalink: https://lavalink.dev/
- Spotify Web API: https://developer.spotify.com/documentation/web-api
- SQLAlchemy: https://docs.sqlalchemy.org/
- Async Python: https://docs.python.org/3/library/asyncio.html
