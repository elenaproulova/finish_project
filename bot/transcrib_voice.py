from gtts import gTTS
import os
import tempfile
import subprocess
from typing import Optional, Tuple
from faster_whisper import WhisperModel

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

import speech_recognition as sr

def transcribe_voice(filename):
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language="en-US")  # или другой язык
    except Exception as e:
        text = "Извините, я не смог распознать голос."
    return text

def _run_ffmpeg(cmd: list) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError("FFmpeg error: " + proc.stderr.decode("utf-8", "ignore")[:800])


def transcribe_audio_file(
    input_path: str,
    *,
    model: Optional[WhisperModel] = None,
    model_size: str = "small",
    device: str = "cpu",          # "cpu" или "cuda"
    compute_type: str = "int8",   # на GPU обычно "float16"
    language: Optional[str] = "ru",
    ffmpeg_path: str = "ffmpeg",
    beam_size: int = 5,
    return_segments: bool = False
):
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    own_model = False
    if model is None:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        own_model = True

    try:
        with tempfile.TemporaryDirectory() as td:
            wav_path = os.path.join(td, "audio.wav")
            _run_ffmpeg([
                ffmpeg_path, "-y",
                "-i", input_path,
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                wav_path
            ])

            segments, info = model.transcribe(
                wav_path,
                language=language,
                beam_size=beam_size,
                vad_filter=True
            )

            text = " ".join(s.text.strip() for s in segments).strip()
            if return_segments:
                # Вернём ещё сегменты с таймкодами
                seg_list = [
                    {"start": s.start, "end": s.end, "text": s.text}
                    for s in model.transcribe(wav_path, language=language, beam_size=beam_size, vad_filter=True)[0]
                ]
                return text, seg_list, info

            return text
    finally:
        if own_model:
            try:
                del model
            except Exception:
                pass

whisper = WhisperModel("small", device="cpu", compute_type="int8")

text = transcribe_audio_file(
    "tts.mp3",
    model=whisper,
    language="en",
    ffmpeg_path=r"C:\ffmpeg\bin\ffmpeg.exe"  # или просто "ffmpeg", если в PATH
)
print(text)
