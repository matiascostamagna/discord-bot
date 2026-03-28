# Music Bot Pro - Estructura del Proyecto

```
music-bot/
├── src/
│   ├── main.py                    # Punto de entrada
│   ├── bot.py                     # Instancia del cliente Discord
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Variables de entorno y configuración
│   │   ├── database.py            # SQLAlchemy setup
│   │   └── lavalink.py            # Config de Lavalink
│   ├── cogs/                      # Comandos modularizados
│   │   ├── __init__.py
│   │   ├── music.py               # /play, /stop, /skip, /pause, /resume
│   │   ├── queue.py               # /queue, /shuffle, /loop
│   │   ├── playlist.py            # /playlist save/load/delete
│   │   ├── admin.py               # Comandos admin
│   │   └── stats.py               # Estadísticas y datos
│   ├── services/
│   │   ├── __init__.py
│   │   ├── music_service.py       # Lógica de reproducción
│   │   ├── queue_service.py       # Gestión inteligente de cola
│   │   ├── spotify_service.py     # Integración Spotify
│   │   ├── search_service.py      # Búsqueda unificada
│   │   └── playlist_service.py    # Manejo de playlists
│   ├── models/                    # SQLAlchemy ORM
│   │   ├── __init__.py
│   │   ├── base.py                # Base model con timestamps
│   │   ├── user.py                # Usuario de Discord
│   │   ├── queue.py               # Queue item
│   │   ├── playlist.py            # Playlist guardada
│   │   ├── track.py               # Canción en caché
│   │   └── stats.py               # Estadísticas
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py       # Manejo global de errores
│   │   ├── logger.py              # Sistema de logs
│   │   └── voice_check.py         # Validación de canal de voz
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── constants.py           # Constantes del bot
│   │   ├── helpers.py             # Funciones auxiliares
│   │   ├── formatters.py          # Formateo de mensajes
│   │   └── validators.py          # Validaciones
│   └── events/
│       ├── __init__.py
│       ├── ready.py               # Bot ready event
│       ├── interaction.py         # Slash commands
│       └── errors.py              # Manejo de errores globales
├── migrations/                    # Alembic migrations
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│       └── 001_initial.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures pytest
│   ├── test_music_service.py
│   ├── test_queue_service.py
│   ├── test_spotify_service.py
│   └── test_search_service.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── setup_db.py                # Inicializar BD
│   └── seed_data.py               # Datos de prueba
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── Makefile
└── README.md
```

## Instalación

```bash
# 1. Clonar y entrar al directorio
git clone <tu-repo>
cd music-bot

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Inicializar base de datos
python scripts/setup_db.py

# 6. Descargar e iniciar Lavalink (en otra terminal)
java -jar Lavalink.jar

# 7. Ejecutar bot
python src/main.py
```

## Stack Tecnológico

- **Bot Framework:** discord.py 2.4.0
- **Audio:** Lavalink + Wavelink (profesional)
- **APIs Externas:** Spotify, YouTube
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Logging:** Loguru
- **Testing:** Pytest + asyncio
- **Deployment:** Docker + PM2/systemd
