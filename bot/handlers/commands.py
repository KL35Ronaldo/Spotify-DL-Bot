# Command handlers for @KL35Bot.
# Handles /start, /help, and /about commands.

import logging
from config import Config
from telegram import Update

logger = logging.getLogger(__name__)

class Text:
    START = f"""
🎵 **Welcome to {Config.BOT_NAME}!**

I convert Spotify track links into high-quality MP3 files with complete metadata.

**How to use:**
• Send me any Spotify track link
• Use inline mode: `{Config.BOT_NAME} song name`

**Commands:**
/help - Usage instructions
/about - About this bot

Just send a Spotify link to get started! 🎧
"""

    HELP = f"""
📖 **How to Use {Config.BOT_NAME}**

**Method 1: Direct Link**
Simply send a Spotify track link:
`https://open.spotify.com/track/...`

**Method 2: Inline Search**
Type in any chat:
`{Config.BOT_NAME} song name or artist`

Select a result and I'll send the audio!

**Supported Links:**
• `https://open.spotify.com/track/...`
• `spotify:track:...`

**Note:** 
• Only single tracks are supported
• Files are converted to 320kbps MP3
• Maximum file size: 50MB (Telegram limit)
"""

    ABOUT = f"""
ℹ️ **About {Config.BOT_NAME}**

**Version:** {Config.BOT_VERSION}
**Bot Username:** {Config.BOT_NAME}

**Features:**
• Spotify track to MP3 conversion
• High-quality 320kbps audio
• Complete ID3 metadata tagging
• Album artwork embedding
• Inline search support

**Powered by:**
• python-telegram-bot
• Spotify Web API
• yt-dlp

Made with ❤️ for music lovers
"""

async def start(update: Update, _) -> None:
    await update.message.reply_text(Text.START, parse_mode="Markdown", disable_web_page_preview=True)

async def helpp(update: Update, _) -> None:
    await update.message.reply_text(Text.HELP, parse_mode="Markdown", disable_web_page_preview=True)

async def about(update: Update, _) -> None:
    await update.message.reply_text(Text.ABOUT, parse_mode="Markdown", disable_web_page_preview=True)
