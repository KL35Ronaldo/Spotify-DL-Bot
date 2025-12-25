# Spotify API service for @KL35Bot.
# Handles authentication and metadata retrieval from Spotify Web API.

from config import Config
from typing import Optional
import re, asyncio, logging, aiohttp, spotipy
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger(__name__)
nameit = lambda x: re.sub(r'\s{2,}', ' ', re.sub(r"\(.*?\".*?\".*?\)|\- From \".*?\"", "", x)).strip()

def albumit(x: str) -> str:
    ret = ''
    match = re.search(r".*?\"(.*?)\".*?", x)
    ret = match.group(1).strip() if match else x
    return re.sub(r'\s{2,}', ' ', re.sub(r'\(.*?\)', '', ret)).strip()

class SpotifyAPI:
    def __init__(self):
        self._sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
            ),
            requests_timeout=Config.API_TIMEOUT,
        )
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=Config.API_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    def id(url: str) -> Optional[str]:
        if url.startswith("spotify:track:"):
            return url.split(":")[-1]
        match = re.search(r"open\.spotify\.com/track/([a-zA-Z0-9]+)", url)
        if match:
            return match.group(1)
        return None

    async def info(self, tid: str) -> Optional[dict]:
        try:
            loop = asyncio.get_event_loop()
            track = await loop.run_in_executor(None, self._sp.track, tid)
            if not track:
                return None
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            date = track["album"].get("release_date", "")
            year = date.split("-")[0] if date else ""
            thumb = ""
            if track["album"]["images"]:
                thumb = track["album"]["images"][0]["url"]
            return {
                "id": tid,
                "title": nameit(track["name"]),
                "artists": artists,
                "artist_list": [a["name"] for a in track["artists"]],
                "album": albumit(track["album"]["name"]),
                "year": year,
                "duration": track["duration_ms"],
                "url": track["external_urls"]["spotify"],
                "thumb": thumb,
                "isrc": track.get("external_ids", {}).get("isrc", ""),
            }
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify API error for track {tid}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching track {tid}: {e}")
        return None

    async def search(self, query: str, limit: int = 10) -> list[dict]:
        tracks = []
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, lambda: self._sp.search(q=query, type="track", limit=limit)
            )
            for item in results.get("tracks", {}).get("items", []):
                artists = ", ".join([a["name"] for a in item["artists"]])
                date = item["album"].get("release_date", "")
                year = date.split("-")[0] if date else ""
                thumb = ""
                if item["album"]["images"]:
                    thumb = item["album"]["images"][0]["url"]
                tracks.append({
                    "id": item["id"],
                    "title": nameit(item["name"]),
                    "artists": artists,
                    "album": albumit(item["album"]["name"]),
                    "year": year,
                    "duration": item["duration_ms"],
                    "url": item["external_urls"]["spotify"],
                    "thumb": thumb
                })
        except spotipy.SpotifyException as e:
            logger.error(f"Spotify search error for '{query}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error searching '{query}': {e}")
        return tracks

    async def thumb(self, url: str) -> Optional[bytes]:
        if not url:
            return None
        try:
            session = await self._get()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
        except Exception as e:
            logger.error(f"Error downloading album art: {e}")
        return None

_spotify_api: Optional[SpotifyAPI] = None

def api() -> SpotifyAPI:
    global _spotify_api
    if _spotify_api is None:
        _spotify_api = SpotifyAPI()
    return _spotify_api
