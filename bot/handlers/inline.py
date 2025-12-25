# Inline query handler for @KL35Bot.
# Handles inline search and chosen result processing.

import uuid, logging
from config import Config
from telegram import (
    Update,
    InputMediaPhoto,
    InputMediaAudio,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputTextMessageContent,
    InlineQueryResultArticle
)
from bot.handlers.spotify import cap
from telegram.ext import ContextTypes
from bot.services.spotify_api import api
from telegram.constants import ChatAction
from bot.services.tagger import AudioTagger
from bot.services.downloader import AudioDownloader, DownloadError

logger = logging.getLogger(__name__)
dur = lambda ms: f"{(ms//1000)//60}:{(ms//1000)%60:02d}"
res = lambda s: InlineQueryResultArticle(
    id=str(uuid.uuid4()),
    title="No tracks found",
    description=f"No results for '{s}'",
    input_message_content=InputTextMessageContent(f"🔍 No tracks found for: {s}"),
    thumbnail_url="https://te.legra.ph/file/3ed71fa60172e09e96794.jpg"
)

async def inline(update: Update, _) -> None:
    query = update.inline_query
    if not query:
        return
    search = query.query.strip()
    if len(search) < 3:
        return
    try:
        tracks = await api().search(search, limit=50)
        if not tracks:
            await query.answer([res(search)], cache_time=60)
            return
        results = []
        for track in tracks:
            results.append(InlineQueryResultArticle(
                id=track["id"],
                title=track["title"] + f' ({track.get("year", "")})',
                description=f"{track['artists']} • {track['album']} • {dur(track.get("duration", 0))}",
                thumbnail_url=track.get("thumb"),
                input_message_content=InputTextMessageContent(f"🎵 **{track['title']}**\n👤 {track['artists']}\n💿 {track['album']} ({track.get('year', '')})\n\n⏳ Processing...", "Markdown"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏳ Processing...", callback_data="none")]])
            ))
        await query.answer(results[:50], cache_time=300)
    except Exception as e:
        logger.error(f"Inline query error: {e}", exc_info=True)

async def chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    res = update.chosen_inline_result
    if not res:
        logger.warning("Inline result not found.")
        return
    tid, imid, user = res.result_id, res.inline_message_id, res.from_user
    if not imid:
        logger.warning("Inline message ID not found.")
        await context.bot.send_message(user.id, "❌ Inline message ID not found.")
        return
    data = await api().info(tid)
    if not data:
        await context.bot.edit_message_text(inline_message_id=imid, text="❌ Track not found on Spotify.")
        return
    try:
        await context.bot.edit_message_media(
            media=InputMediaPhoto(
                media=data.get('thumb'),
                caption=f"🎵 **{data['title']}**\n👤 {data['artists']}\n💿 {data['album']} ({data.get('year', '')})\n\n⏳ Downloading...",
                parse_mode="Markdown"
            ),
            inline_message_id=imid,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏳ Downloading...", callback_data="none")]])
        )
    except Exception:
        pass
    downloader = AudioDownloader()
    try:
        path = await downloader.download(data)
    except DownloadError as e:
        await context.bot.edit_message_caption(inline_message_id=imid, caption=f"❌ Download failed: {str(e)}")
        return
    if not path or not path.exists():
        await context.bot.edit_message_caption(inline_message_id=imid, caption="❌ Download failed. Please try again.")
        return
    uid = f"{tid}_{user.id}"
    fpath = Config.TEMP_DIR / f"{uid}.mp3"
    if path != fpath:
        if fpath.exists():
            fpath.unlink(True)
        path.rename(fpath)
    await AudioTagger.tag(fpath, data, await api().thumb(data.get("thumb", "")))
    fid = None
    try:
        duration = AudioTagger.duration(fpath)
        if not duration and data:
            duration = data.get("duration", 0) // 1000
        title = f"{data.get("title", "audio")} - {data.get("artists", "Unknown")} | {data.get("album", "Unknown")} ({data.get("year", "")})"
        with open(fpath, 'rb') as ff:
            fid = await context.bot.send_audio(
                chat_id=Config.TEMP_STORAGE,
                audio=ff,
                duration=duration,
                performer=data.get('artists', 'Unknown'),
                title=title,
                filename=title + ".mp3",
                thumbnail=await api().thumb(data.get("thumb", ""))
            )
        await context.bot.edit_message_media(
            media=InputMediaAudio(
                media=fid.audio.file_id,
                caption=cap(data) if data else "🎵 Here is your requested song!",
                parse_mode="Markdown"
            ),
            inline_message_id=imid,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Spotify", url=data.get("url", ""))]])
        )
        logger.info(f"Delivered and deleted temp audio: {uid}")
    except Exception as e:
        logger.error(f"Failed to deliver temp audio: {e}", exc_info=True)
        await context.bot.edit_message_caption(inline_message_id=imid, caption="❌ Failed to deliver audio. Please try again.")
    finally:
        try:
            fpath.unlink(True)
            await fid.delete()
            logger.info(f"Deleted temp audio: {uid}")
        except Exception:
            pass
