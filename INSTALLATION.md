# 🎵 Music Bot Pro - Guía de Instalación

## 📋 Requisitos Previos

### Sistema
- **Python 3.11+**
- **Git**
- **PostgreSQL** (opcional, usa SQLite en dev)
- **Java 11+** (para Lavalink)

### Cuentas Necesarias
- **Discord Server** (donde crear el bot)
- **Spotify Premium Account** (para usar Spotify API)
- **Spotify Developer Account** (registrar aplicación)

---

## 🚀 Paso 1: Crear el Bot en Discord

### 1.1 Acceder a Discord Developer Portal
1. Ve a https://discord.com/developers/applications
2. Haz clic en "New Application"
3. Pon un nombre: `Music Bot Pro`
4. Acepta los términos y crea

### 1.2 Obtener Token del Bot
1. Ve a "Bot" en la izquierda
2. Haz clic en "Add Bot"
3. Haz clic en "Copy" bajo "TOKEN"
4. **Guarda este token en .env como DISCORD_TOKEN**

### 1.3 Configurar Permisos
1. Ve a "OAuth2" → "URL Generator"
2. Selecciona scopes:
   - `bot`
   - `applications.commands`
3. Selecciona permisos:
   - `Send Messages`
   - `Embed Links`
   - `Attach Files`
   - `Read Message History`
   - `Connect` (voz)
   - `Speak` (voz)
   - `Use Voice Activity`
4. Copia la URL generada y únete a un servidor de prueba

---

## 🎵 Paso 2: Configurar Spotify API

### 2.1 Registrar App en Spotify
1. Ve a https://developer.spotify.com/dashboard
2. Log in con tu cuenta Premium de Spotify
3. Haz clic en "Create an App"
4. Acepta los términos
5. Rellena el formulario y crea

### 2.2 Obtener Credenciales
1. En tu app, ve a "Settings"
2. Verás **Client ID** y **Client Secret**
3. Copia estos valores en .env:
   ```
   SPOTIFY_CLIENT_ID=tu_client_id
   SPOTIFY_CLIENT_SECRET=tu_client_secret
   ```

---

## 🔧 Paso 3: Configuración Local

### 3.1 Clonar/Descargar Proyecto
```bash
# Opción 1: Si tienes Git
git clone <tu-repo>
cd music-bot

# Opción 2: Descargar ZIP
unzip music-bot.zip
cd music-bot
```

### 3.2 Crear Archivo .env
```bash
cp .env.example .env
```

**Edita `.env` con tus valores:**
```env
# Discord
DISCORD_TOKEN=tu_token_del_bot_aqui
DISCORD_PREFIX=/

# Database (en desarrollo usa SQLite)
DATABASE_URL=sqlite:///./musicbot.db

# Spotify
SPOTIFY_CLIENT_ID=tu_client_id
SPOTIFY_CLIENT_SECRET=tu_client_secret

# Lavalink (local)
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass

# Environment
NODE_ENV=development
LOG_LEVEL=INFO
ENABLE_SPOTIFY=true
```

### 3.3 Crear Virtual Environment
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3.4 Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

## 🎼 Paso 4: Descargar e Iniciar Lavalink

Lavalink es el servidor de audio que el bot usa para reproducir música.

### 4.1 Descargar Lavalink
1. Ve a https://github.com/lavalink-devs/Lavalink/releases
2. Descarga el archivo `.jar` más reciente (ej: `Lavalink.jar`)
3. Colócalo en una carpeta dedicada (ej: `./lavalink/`)

### 4.2 Crear Archivo de Configuración
En la misma carpeta, crea `application.yml`:

```yaml
server:
  port: 2333
  address: localhost

lavalink:
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
    filters:
      volume: true
      equalizer: true
      karaoke: true
      timescale: true
      tremolo: true
      vibrato: true
      distortion: true
      rotation: true
      channelMix: true
      lowPass: true
    bufferDurationMs: 400
    youtubePlaylistLoadLimit: 6
    playerUpdateInterval: 5
    youtubeSearchLoaded: false
    gc-warnings: true

metrics:
  prometheus:
    enabled: false

logging:
  level:
    root: INFO
    lavalink: INFO
  file:
    path: ./logs/
```

### 4.3 Iniciar Lavalink
```bash
# En otra terminal, ve a la carpeta de Lavalink
cd lavalink
java -jar Lavalink.jar
```

Deberías ver:
```
[main] INFO Lavalink - Lavalink started in XX seconds
[main] INFO Lavalink - Listening on localhost:2333
```

---

## 5️⃣ Paso 5: Inicializar Base de Datos

En una nueva terminal (con el venv activado):

```bash
python scripts/setup_db.py
```

Deberías ver:
```
2024-01-20 10:30:15 | INFO | Inicializando BD...
2024-01-20 10:30:16 | INFO | ✅ Base de datos inicializada
```

---

## 🤖 Paso 6: Ejecutar el Bot

En una nueva terminal:

```bash
# Asegúrate de que el venv esté activado
python src/main.py
```

Deberías ver:
```
2024-01-20 10:30:20 | INFO | 🚀 Iniciando Music Bot en modo development...
2024-01-20 10:30:22 | INFO | 🤖 Bot conectado como MusicBot#1234
2024-01-20 10:30:22 | INFO | 📊 Conectado a 1 servidor(es)
```

---

## 🧪 Paso 7: Probar el Bot

En tu servidor de Discord:

```
/play Bohemian Rhapsody Queen
```

Deberías ver un embed con la canción agregada a la cola.

Otros comandos:
- `/queue` - Ver cola
- `/skip` - Siguiente canción
- `/stop` - Detener
- `/shuffle` - Mezclar

---

## 🐳 Alternativa: Ejecutar con Docker

Si tienes Docker instalado:

```bash
docker-compose up -d
```

Esto levanta:
- Bot
- PostgreSQL
- Lavalink

Todo en contenedores.

---

## 🧪 Ejecutar Tests

```bash
make test
# o
pytest -v
```

---

## 📊 Estructura del Proyecto

```
music-bot/
├── src/
│   ├── main.py              # Punto de entrada
│   ├── bot.py               # Cliente Discord
│   ├── config/
│   │   ├── settings.py      # Variables de entorno
│   │   └── database.py      # SQLAlchemy setup
│   ├── cogs/
│   │   └── music.py         # Comandos de música
│   ├── services/
│   │   ├── spotify_service.py
│   │   └── queue_service.py
│   ├── models/
│   │   └── __init__.py      # ORM models
│   └── middleware/
│       └── logger.py        # Logging
├── tests/
│   ├── conftest.py
│   └── test_queue_service.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

---

## 🔧 Troubleshooting

### Error: "discord.DiscordException: Cannot connect to gateway"
- **Solución:** Verifica que DISCORD_TOKEN sea correcto

### Error: "Lavalink connection refused"
- **Solución:** Asegúrate que Lavalink está corriendo en otra terminal

### Error: "PostgreSQL: Connection refused"
- **Solución:** Usa SQLite en desarrollo: `DATABASE_URL=sqlite:///./musicbot.db`

### Error: "Spotify API error"
- **Solución:** Verifica SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET

---

## 📚 Próximos Pasos

1. **Agregar más cogs:**
   - Playlist management
   - Admin commands
   - Stats y analytics

2. **Mejorar calidad de audio:**
   - Configurar filtros en Lavalink
   - Optimizar bitrate

3. **Desplegar en producción:**
   - Usar PostgreSQL en lugar de SQLite
   - Configurar Sentry para error tracking
   - Usar Railway o DigitalOcean para hosting

4. **Agregar más fuentes de música:**
   - SoundCloud
   - Apple Music
   - Deezer

---

## 🆘 Soporte

- **Documentación:** Ver archivos .md en el proyecto
- **Issues:** Reportar en GitHub
- **Discord.py Docs:** https://discordpy.readthedocs.io/
- **Lavalink Docs:** https://lavalink.dev/

---

## 📝 License

MIT License - Siéntete libre de usar, modificar y distribuir

¡Que disfrutes tu Music Bot! 🎵
