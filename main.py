# @KL35Bot - Spotify to MP3 Telegram Bot
# Main entry point with graceful shutdown and error handling.

import shutil
import sys, signal, asyncio
from typing import Optional
from telegram import Update
from telegram.ext import (
    filters,
    Application,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler
)
from config import Config, logger
from bot.services.spotify_api import api
from bot.handlers.spotify import spotify
from bot.handlers.inline import inline, chosen
from bot.handlers.commands import start, helpp, about

app: Optional[Application] = None

async def error_handler(update: object, context) -> None:
    logger.error(f"Exception while handling update: {context.error}", exc_info=context.error)
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("❌ An unexpected error occurred. Please try again later.")
    except Exception:
        pass

async def post_init(_) -> None:
    logger.info(f"{Config.BOT_NAME} initialized successfully")

async def post_shutdown(_) -> None:
    logger.info("Shutting down...")
    try:
        await api().close()
    except Exception as e:
        logger.warning(f"Error closing Spotify session: {e}")
    try:
        shutil.rmtree('__pycache__')
        shutil.rmtree('bot/__pycache__')
        shutil.rmtree('bot/services/__pycache__')
        shutil.rmtree('bot/handlers/__pycache__')
    except Exception as e:
        logger.warning(f"Error cleaning up: {e}")
    logger.info("Cleanup complete")


def signal_handler(signum, _) -> None:
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    if app and app.running:
        asyncio.create_task(app.stop())
    else:
        sys.exit(0)

def create_application() -> Application:
    application = (
        Application.builder()
        .token(Config.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .concurrent_updates(True)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", helpp))
    application.add_handler(CommandHandler("about", about))
    spotify_filter = filters.TEXT & filters.Regex(r"(https?://)?open\.spotify\.com/track/[a-zA-Z0-9]+|spotify:track:[a-zA-Z0-9]+")
    application.add_handler(MessageHandler(spotify_filter, spotify))
    application.add_handler(InlineQueryHandler(inline))
    application.add_handler(ChosenInlineResultHandler(chosen))
    application.add_error_handler(error_handler)
    return application

def main() -> None:
    global app
    logger.info(f"Starting {Config.BOT_NAME} v{Config.BOT_VERSION}...")
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    except (ValueError, OSError):
        pass
    app = create_application()
    logger.info("Bot is now running. Press Ctrl+C to stop.")
    try:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
