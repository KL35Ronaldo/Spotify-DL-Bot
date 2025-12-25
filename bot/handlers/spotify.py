# Spotify link handler for @KL35Bot.
# Processes Spotify track URLs and sends audio files.

import re, logging
from pathlib import Path
from config import Config
from typing import Optional
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from bot.services.tagger import AudioTagger
from bot.services.spotify_api import api, SpotifyAPI
from bot.services.downloader import AudioDownloader, DownloadError
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

def cap(data: dict) -> str:
    caption = f"🎵 **{data.get("title", "Unknown")}**\n"
    caption += f"👤 {data.get("artists", "Unknown Artist")}\n"
    caption += f"💿 {data.get("album", "Unknown Album")}"
    if data.get("year", ""):
        caption += f" ({data.get("year", "")})"
    if data.get("spotify_url", ""):
        caption += f"\n\n🔗 [Spotify]({data.get("spotify_url", "")})"
    return caption

async def process(update: Update, _, tid: str) -> None:
    msg = update.effective_message
    if not msg:
        return
    sts = await msg.reply_text("⏳ Processing your request...")
    path: Optional[Path] = None
    spotify = api()
    try:
        data = await spotify.info(tid)
        if not data:
            await sts.edit_text("❌ Track not found on Spotify.")
            return
        await sts.edit_text(f"⏳ Downloading: {data['title']}...")
        downloader = AudioDownloader()
        try:
            path = await downloader.download(data)
        except DownloadError as e:
            await sts.edit_text(f"❌ Download failed: {str(e)}")
            return
        if not path or not path.exists():
            await sts.edit_text("❌ Download failed. Please try again.")
            return
        mb = path.stat().st_size / (1024 * 1024)
        if mb > Config.MAX_FILE_SIZE_MB:
            await sts.edit_text(f"❌ File too large ({mb:.1f}MB). Telegram limit is {Config.MAX_FILE_SIZE_MB}MB.")
            AudioDownloader.delete(path)
            return
        await sts.edit_text("⏳ Tagging audio...")
        cover = await spotify.thumb(data.get("thumb", ""))
        await AudioTagger.tag(path, data, cover)
        duration = AudioTagger.duration(path)
        if duration == 0:
            duration = data.get("duration", 0) // 1000
        caption = cap(data)
        title = f"{data.get("title", "audio")} - {data.get("artists", "Unknown")} | {data.get("album", "Unknown Album")}"
        if data.get("year", ""):
            title += f" ({data.get("year", "")})"
        file = title + ".mp3"
        safe = re.sub(r'[<>:"/\\|?*]', "-", file)
        await sts.edit_text("⏳ Uploading to Telegram...")
        await update.effective_chat.send_action(ChatAction.UPLOAD_VOICE)
        with open(path, "rb") as audio:
            await msg.reply_audio(
                audio=audio,
                caption=caption,
                parse_mode="Markdown",
                title=file.replace(".mp3", ""),
                performer=data.get("artists").split(",")[0] or "Unknown",
                duration=duration,
                thumbnail=cover,
                filename=safe,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Spotify", url=data.get("url", ""))]])
            )
        await sts.delete()
        logger.info(f"Successfully sent: {safe}")
    except Exception as e:
        logger.error(f"Error processing track {tid}: {e}", exc_info=True)
        try:
            await sts.edit_text("❌ An error occurred while processing your request. Please try again.")
        except Exception:
            pass
    finally:
        if path:
            AudioDownloader.delete(path)

async def spotify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg or not msg.text:
        return
    text = msg.text.strip()
    tid = SpotifyAPI.id(text)
    if not tid:
        await msg.reply_text("❌ Could not extract track ID from link.")
        return
    await process(update, context, tid)
