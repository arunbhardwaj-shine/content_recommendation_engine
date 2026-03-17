import whisper
import subprocess
import io
import numpy as np
import soundfile as sf
# Load once globally
_WHISPER_MODEL = whisper.load_model("medium")  # or "medium"

def extract_text_from_video(video_bytes: bytes) -> str:
    """
    MP4 bytes → full transcript string (in-memory)
    """

    # 1️⃣ Run ffmpeg with stdin/stdout pipes
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-f", "mp4",
            "-i", "pipe:0",
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            "pipe:1",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    audio_bytes, _ = process.communicate(video_bytes)
    print(f"Extracted {len(audio_bytes)} bytes of audio from video.")
    # 2️⃣ Read WAV bytes into numpy array
    audio_buffer = io.BytesIO(audio_bytes)
    audio_np, _ = sf.read(audio_buffer, dtype="float32")

    # 3️⃣ Transcribe directly from numpy array
    result = _WHISPER_MODEL.transcribe(audio_np)

    return result["text"].strip()