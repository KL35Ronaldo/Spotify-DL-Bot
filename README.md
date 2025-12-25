# @KL35Bot - Spotify to MP3 Telegram Bot

A fully asynchronous Telegram bot that converts Spotify track links into high-quality MP3 audio files with complete metadata.

## Features

- 🎵 Convert Spotify track links to 320kbps MP3
- 🏷️ Full ID3 metadata tagging (title, artist, album, year, cover art)
- 🔍 Inline search with up to 50 results
- ⚡ Fully asynchronous for maximum performance
- 🛡️ Robust error handling and graceful shutdown

## Setup

### Prerequisites

- Python 3.10+
- FFmpeg (required by yt-dlp for audio conversion)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Spotify API Credentials (from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/KL35Ronaldo/Spotify-DL-Bot.git
cd Spotify
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file:

```env
BOT_TOKEN=your_telegram_bot_token
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

4. Run the bot:

```bash
python main.py
```

## Usage

### Direct Link

Send any Spotify track link to the bot:

```
https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
```

### Inline Search

Type in any chat:

```
@KL35Bot <your_song_name>
```

## Commands

| Command  | Description        |
| -------- | ------------------ |
| `/start` | Welcome message    |
| `/help`  | Usage instructions |
| `/about` | Bot information    |

## Deployment (Railway)

1. Push code to GitHub
2. Connect repository to Railway
3. Add environment variables in Railway dashboard:
   - `BOT_TOKEN`
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
4. Deploy!

The `railway.toml` configures automatic restarts on failure.

## Project Structure

```
Spotify/
├── bot/
│   ├── handlers/          # Command and message handlers
│   │   ├── commands.py    # /start, /help, /about
│   │   ├── spotify.py     # Spotify link processing
│   │   └── inline.py      # Inline search
│   └── services/          # Core services
│       ├── spotify_api.py # Spotify Web API client
│       ├── downloader.py  # yt-dlp audio download
│       └── tagger.py      # ID3 metadata tagging
├── config.py              # Configuration
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── Procfile               # Railway process file
└── railway.toml           # Railway config
```

## License

MIT License

Copyright (c) 2025 KL35Ronaldo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
