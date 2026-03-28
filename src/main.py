"""
Main - Punto de entrada del Music Bot
"""
import asyncio
import signal
import sys
from bot import create_bot
from middleware.logger import logger
from config.settings import settings

# Crear instancia del bot
bot = create_bot()

async def main():
    """Función principal"""
    
    # Manejador de señales para shutdown limpio
    def handle_signal(sig, frame):
        logger.info(f"📡 Señal {sig} recibida, cerrando bot...")
        asyncio.create_task(bot.close())
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        logger.info(f"🚀 Iniciando Music Bot en modo {settings.node_env}...")
        await bot.start(settings.discord_token)
    except Exception as e:
        logger.exception(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⌨️  Interrupción del teclado")
    except Exception as e:
        logger.exception(f"❌ Error: {e}")
        sys.exit(1)
