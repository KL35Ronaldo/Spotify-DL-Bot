# Audio downloader service for @KL35Bot.
# Uses yt-dlp to search and download audio from YouTube.

from pathlib import Path
from config import Config
from typing import Optional
import asyncio, logging, yt_dlp
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=10)

class DownloadError(Exception):
    """Raised when audio download fails."""
    pass

class AudioDownloader:
    def __init__(self):
        self.temp_dir = Config.TEMP_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _query(self, data: dict) -> str:
        title = data.get("title", "")
        artists = data.get("artists", "")
        isrc = data.get("isrc", "")
        if isrc:
            return f"{title} {artists} {isrc}"
        return f"{title} {artists} audio"

    def _download(self, query: str, path: Path) -> Optional[Path]:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(path.with_suffix(".%(ext)s")),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": Config.AUDIO_FORMAT,
                "preferredquality": Config.AUDIO_BITRATE,
            }],
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
            "noplaylist": True,
            "default_search": "ytsearch1",
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([query])
            mp3_path = path.with_suffix(".mp3")
            if mp3_path.exists():
                return mp3_path
            for ext in [".m4a", ".webm", ".opus"]:
                alt_path = path.with_suffix(ext)
                if alt_path.exists():
                    return alt_path
        except Exception as e:
            logger.error(f"yt-dlp download error: {e}")
        return None

    async def download(self, data: dict) -> Optional[Path]:
        queries = list(dict.fromkeys([
            self._query(data),
            f"{data.get('title', '')} {data.get('artists', '').split(',')[0]} audio",
        ]))
        track_id = data.get("id", "audio")
        path = self.temp_dir / track_id
        for query in queries:
            logger.info(f"Attempting download with query: {query}")
            try:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(_executor, self._download, query, path),
                    timeout=Config.DOWNLOAD_TIMEOUT,
                )
                if result and result.exists():
                    logger.info(f"Successfully downloaded: {result}")
                    return result
                files = list(self.temp_dir.glob(f"{track_id}.*"))
                if files:
                    logger.info(f"Found match via glob: {files[0]}")
                    return files[0]
                logger.warning(f"No results found for query: {query}. Trying next...")
            except asyncio.TimeoutError:
                logger.error(f"Download timeout for: {query}")
                continue
            except Exception as e:
                logger.error(f"Download attempt failed for '{query}': {e}")
                continue
        raise DownloadError(f"Download failed after trying {len(queries)} queries.")

    @staticmethod
    def delete(path: Path):
        try:
            if path and path.exists():
                path.unlink()
                logger.debug(f"Cleaned up: {path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")
