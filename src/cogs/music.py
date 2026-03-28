"""
Music Cog - Comandos principales de reproducción de música
"""
import discord
from discord.ext import commands
from discord import app_commands
from middleware.logger import logger
from services.spotify_service import spotify_service
from services.queue_service import MusicQueue, QueueTrack, QueueMode
from typing import Optional
import asyncio

class Music(commands.Cog):
    \"\"\"Comandos de música\"\"\"
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    def get_queue(self, guild_id: int) -> MusicQueue:
        \"\"\"Obtener o crear queue para un servidor\"\"\"
        if guild_id not in self.bot.music_queues:
            self.bot.music_queues[guild_id] = MusicQueue()
        return self.bot.music_queues[guild_id]
    
    @app_commands.command(name="play", description="Reproducir una canción de Spotify")
    @app_commands.describe(query="Nombre de la canción, artista o URL de Spotify")
    async def play(
        self,
        interaction: discord.Interaction,
        query: str
    ):
        \"\"\"Reproducir una canción\"\"\"
        await interaction.response.defer()
        
        try:
            # Validar que el usuario esté en un canal de voz
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send(
                    "❌ Debes estar en un canal de voz para reproducir música",
                    ephemeral=True
                )
                return
            
            logger.info(f"🔍 Buscando: {query}")
            
            # Buscar en Spotify
            tracks = await spotify_service.search_track(query, limit=1)
            
            if not tracks:
                await interaction.followup.send(
                    f"❌ No se encontró la canción '{query}'",
                    ephemeral=True
                )
                return
            
            track = tracks[0]
            
            # Crear QueueTrack
            queue_track = QueueTrack(
                track_id=track.id,
                title=track.title,
                artist=track.artist,
                duration_ms=track.duration_ms,
                source="spotify",
                requested_by=str(interaction.user.id),
                url=track.url,
                image_url=track.image_url
            )
            
            # Agregar a la cola
            queue = self.get_queue(interaction.guild.id)
            queue.add_track(queue_track)
            
            # Crear embed de respuesta
            embed = discord.Embed(
                title="✅ Canción agregada",
                description=f"**{track.title}** por {track.artist}",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=track.image_url)
            embed.add_field(name="Duración", value=f"{track.duration_ms // 60000}:{(track.duration_ms % 60000) // 1000:02d}")
            embed.add_field(name="Posición en cola", value=f"#{len(queue)}")
            embed.set_footer(text=f"Agregado por {interaction.user}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"✅ Track agregado: {track.title}")
            
        except Exception as e:
            logger.exception(f"❌ Error en /play: {e}")
            await interaction.followup.send(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="queue", description="Ver la cola de reproducción")
    async def queue_command(self, interaction: discord.Interaction):
        \"\"\"Ver la cola\"\"\"
        await interaction.response.defer()
        
        try:
            queue = self.get_queue(interaction.guild.id)
            
            if not queue.queue:
                embed = discord.Embed(
                    title="📭 Cola vacía",
                    description="No hay canciones en la cola",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Mostrar canción actual
            embed = discord.Embed(
                title="🎵 Cola de reproducción",
                color=discord.Color.blue()
            )
            
            if queue.current_track:
                embed.add_field(
                    name="▶️ Reproduciendo ahora",
                    value=f"**{queue.current_track.title}** por {queue.current_track.artist}",
                    inline=False
                )
            
            # Mostrar próximas 10 canciones
            queue_items = queue.get_queue(limit=10)
            queue_text = ""
            for i, track in enumerate(queue_items, 1):
                duration = f"{track.duration_ms // 60000}:{(track.duration_ms % 60000) // 1000:02d}"
                queue_text += f"{i}. **{track.title}** por {track.artist} `{duration}`\\n"
            
            if queue_text:
                embed.add_field(
                    name="📋 Siguientes canciones",
                    value=queue_text,
                    inline=False
                )
            
            # Estadísticas
            stats = queue.get_stats()
            embed.add_field(
                name="📊 Estadísticas",
                value=f"Total en cola: {stats['queue_size']}\\nDuración total: {stats['total_duration']}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"❌ Error en /queue: {e}")
            await interaction.followup.send(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="skip", description="Saltar a la siguiente canción")
    async def skip(self, interaction: discord.Interaction):
        \"\"\"Saltar canción\"\"\"
        await interaction.response.defer()
        
        try:
            queue = self.get_queue(interaction.guild.id)
            next_track = queue.skip()
            
            if not next_track:
                embed = discord.Embed(
                    title="⏹️ No hay más canciones",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="⏭️ Canción saltada",
                description=f"Ahora reproduciendo: **{next_track.title}** por {next_track.artist}",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=next_track.image_url)
            
            await interaction.followup.send(embed=embed)
            logger.info(f"⏭️ Track saltado: {next_track.title}")
            
        except Exception as e:
            logger.exception(f"❌ Error en /skip: {e}")
            await interaction.followup.send(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="stop", description="Detener la reproducción")
    async def stop(self, interaction: discord.Interaction):
        \"\"\"Detener música\"\"\"
        await interaction.response.defer()
        
        try:
            queue = self.get_queue(interaction.guild.id)
            queue.clear()
            
            embed = discord.Embed(
                title="⏹️ Reproducción detenida",
                color=discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed)
            logger.info(f"⏹️ Reproducción detenida en {interaction.guild.name}")
            
        except Exception as e:
            logger.exception(f"❌ Error en /stop: {e}")
            await interaction.followup.send(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="shuffle", description="Mezclar la cola")
    async def shuffle(self, interaction: discord.Interaction):
        \"\"\"Mezclar cola\"\"\"
        await interaction.response.defer()
        
        try:
            queue = self.get_queue(interaction.guild.id)
            queue.shuffle()
            
            embed = discord.Embed(
                title="🔀 Cola mezclada",
                description=f"Se reorganizaron {len(queue)} canciones",
                color=discord.Color.blue()
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.exception(f"❌ Error en /shuffle: {e}")
            await interaction.followup.send(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    \"\"\"Setup function para cargar el cog\"\"\"
    await bot.add_cog(Music(bot))
    logger.info("✅ Music cog cargado")
