# Audio tagger service for @KL35Bot.
# Handles ID3 metadata tagging for MP3 files.

import io, logging
from PIL import Image
from pathlib import Path
from typing import Optional
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, ID3NoHeaderError

logger = logging.getLogger(__name__)

class AudioTagger:
    @staticmethod
    def _resize(byt: bytes) -> bytes:
        try:
            img = Image.open(io.BytesIO(byt))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=90)
            return output.getvalue()
        except Exception as e:
            logger.warning(f"Failed to resize cover art: {e}")
            return byt

    @staticmethod
    async def tag(path: Path, data: dict, cbyt: Optional[bytes] = None) -> bool:
        try:
            try:
                audio = ID3(str(path))
            except ID3NoHeaderError:
                audio = ID3()
            audio.delete()
            if data.get("title"):
                audio.add(TIT2(encoding=3, text=f"{data['title']} - {data['artists']} | {data['album']} ({data.get('year', '')})" or data['title']))
            if data.get("artists"):
                audio.add(TPE1(encoding=3, text=data["artists"]))
            if data.get("album"):
                audio.add(TALB(encoding=3, text=data["album"]))
            if data.get("year"):
                audio.add(TDRC(encoding=3, text=data["year"]))
            if cbyt:
                cover = AudioTagger._resize(cbyt)
                audio.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover))
            audio.save(str(path), v2_version=4)
            logger.info(f"Tagged: {path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to tag {path}: {e}")
            return False

    @staticmethod
    def duration(path: Path) -> int:
        try:
            audio = MP3(str(path))
            return int(audio.info.length)
        except Exception as e:
            logger.warning(f"Could not get duration for {path}: {e}")
            return 0
