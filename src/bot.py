"""
Discord Bot Client - Inicialización y configuración principal
"""
import discord
from discord.ext import commands
from config.settings import settings
from middleware.logger import logger
from config.database import init_db, close_db
from typing import Optional

class MusicBot(commands.Bot):
    """Cliente de Discord personalizado para el music bot"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.voice_states = True
        intents.guild_voice_states = True
        
        super().__init__(
            command_prefix=settings.discord_prefix,
            intents=intents,
            help_command=None,  # Comando help personalizado
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="🎵 Música • /help"
            )
        )
        
        # Atributos del bot
        self.music_queues = {}  # {guild_id: MusicQueue}
        self.voice_clients = {}  # {guild_id: VoiceClient}
        self.currently_playing = {}  # {guild_id: Track}
        
        logger.info("✅ MusicBot cliente creado")
    
    async def setup_hook(self):
        """Hook que se ejecuta antes de que el bot esté listo"""
        logger.info("🔧 Ejecutando setup_hook...")
        
        # Inicializar base de datos
        await init_db()
        
        # Cargar cogs (comandos)
        await self.load_cogs()
        
        logger.info("✅ Setup completado")
    
    async def load_cogs(self):
        """Cargar todos los cogs (módulos de comandos)"""
        import importlib
        from pathlib import Path
        
        cogs_dir = Path(__file__).parent / "cogs"
        
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
            
            module_name = f"cogs.{cog_file.stem}"
            try:
                module = importlib.import_module(module_name)
                logger.info(f"📦 Cargando cog: {module_name}")
            except Exception as e:
                logger.exception(f"❌ Error cargando cog {module_name}: {e}")
    
    async def on_ready(self):
        """Evento disparado cuando el bot está listo"""
        logger.info(f"🤖 Bot conectado como {self.user}")
        logger.info(f"📊 Conectado a {len(self.guilds)} servidor(es)")
        logger.info(f"👥 Total de usuarios: {sum(len(guild.members) for guild in self.guilds)}")
    
    async def on_guild_join(self, guild: discord.Guild):
        """Evento disparado cuando el bot se une a un servidor"""
        logger.info(f"✅ Bot agregado al servidor: {guild.name} (ID: {guild.id})")
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Evento disparado cuando el bot se elimina de un servidor"""
        logger.info(f"❌ Bot removido del servidor: {guild.name} (ID: {guild.id})")
        
        # Limpiar recursos del servidor
        if guild.id in self.music_queues:
            del self.music_queues[guild.id]
        if guild.id in self.voice_clients:
            del self.voice_clients[guild.id]
        if guild.id in self.currently_playing:
            del self.currently_playing[guild.id]
    
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """Evento disparado cuando cambia el estado de voz de alguien"""
        # Si el bot es desconectado, limpiar queue
        if member.id == self.user.id and after.channel is None:
            guild_id = member.guild.id
            if guild_id in self.music_queues:
                del self.music_queues[guild_id]
            if guild_id in self.voice_clients:
                del self.voice_clients[guild_id]
            logger.info(f"🔌 Bot desconectado de {member.guild.name}")
    
    async def close(self):
        """Cerrar el bot y limpiar recursos"""
        logger.info("🛑 Cerrando bot...")
        
        # Desconectar de todos los canales de voz
        for voice_client in self.voice_clients.values():
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
        
        # Cerrar base de datos
        from config.database import close_db
        await close_db()
        
        await super().close()
        logger.info("✅ Bot cerrado")

def create_bot() -> MusicBot:
    """Factory function para crear la instancia del bot"""
    return MusicBot()
