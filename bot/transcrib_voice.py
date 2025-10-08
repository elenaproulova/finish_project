import os
import tempfile
import subprocess
from typing import Optional
from gtts import gTTS

def tts_gtts_voice_opus_bytes(
    text: str,
    lang: str = "ru",
    slow: bool = False,
    tld: str = "com",           # можно "ru" для иного акцента
    bitrate: str = "48k",       # битрейт Opus для голосового
) -> bytes:

    if not text or not text.strip():
        raise ValueError("Пустой текст для озвучивания")

    with tempfile.TemporaryDirectory() as td:
        mp3_path = os.path.join(td, "in.mp3")
        ogg_path = os.path.join(td, "out.ogg")

        # 1) gTTS -> MP3
        tts = gTTS(text=text.strip(), lang=lang, slow=slow, tld=tld)
        tts.save(mp3_path)

        # 2) MP3 -> OGG/Opus (mono)
        # Telegram voice = контейнер OGG + кодек Opus, mono-канал
        cmd = [
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-c:a", "libopus",
            "-b:a", bitrate,
            "-ac", "1",           # mono
            ogg_path
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {proc.stderr.decode('utf-8', 'ignore')[:600]}")

        with open(ogg_path, "rb") as f:
            return f.read()

from gtts import gTTS
import tempfile, os
from typing import Optional

def tts_gtts_mp3_bytes(
    text: str,
    lang: str = "ru",
    slow: bool = False,
    tld: str = "com",
    save_path: Optional[str] = None
) -> bytes:
    """
    Озвучивает текст через gTTS, сохраняет MP3 на диск и возвращает байты файла.
    Если save_path не указан, сохраняет в ./tts.mp3
    """
    if not text or not text.strip():
        raise ValueError("Пустой текст для озвучивания")

    out = os.path.abspath(save_path or "tts.mp3")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    tts = gTTS(text=text.strip(), lang=lang, slow=slow, tld=tld)  # требуется интернет
    tts.save(out)

    with open(out, "rb") as f:
        data = f.read()
    return data
