"""
source_whisper.py
Source C: Audio download via yt-dlp + local transcription via faster-whisper.

Downloads the audio track only (YouTube CDN — different request path from the
transcript API, not blocked from Oracle Cloud), then transcribes it locally using
faster-whisper with int8 quantization optimised for ARM64 CPU.

This is the nuclear fallback: works for any video that exists and is public,
regardless of whether it has captions. Slow (~5-15 min per episode).

Enable in config/fallback.json: "whisper": {"enabled": true, "model": "base"}

Install: pip install faster-whisper
"""

import glob
import os
import subprocess
import tempfile


def fetch(video_id, model_size="base"):
    """
    Download audio for a YouTube video and transcribe it with faster-whisper.
    Returns (text, None) on success, (None, error_str) on failure.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, "faster_whisper_not_installed"

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Download audio only
        out_template = os.path.join(tmpdir, f"{video_id}.%(ext)s")
        dl_cmd = [
            "yt-dlp",
            "-f", "bestaudio[ext=m4a]/bestaudio/best",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--output", out_template,
            url,
        ]

        try:
            result = subprocess.run(
                dl_cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            return None, "whisper:download_timeout"
        except FileNotFoundError:
            return None, "whisper:yt-dlp not found"

        audio_files = glob.glob(os.path.join(tmpdir, f"{video_id}.*"))
        audio_files = [f for f in audio_files if not f.endswith(".part")]
        if not audio_files:
            stderr = result.stderr.strip()
            return None, f"whisper:download_failed:{stderr[:80]}"

        audio_path = audio_files[0]

        # Transcribe with faster-whisper (int8 = optimised for CPU/ARM64)
        try:
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            segments, _ = model.transcribe(
                audio_path,
                language="en",
                beam_size=1,
                vad_filter=True,
            )
            lines = [seg.text.strip() for seg in segments if seg.text.strip()]
        except Exception as e:
            return None, f"whisper:transcription_failed:{str(e)[:80]}"

    if not lines:
        return None, "whisper:empty_transcription"

    chunks = [" ".join(lines[i:i + 5]) for i in range(0, len(lines), 5)]
    return "\n\n".join(chunks), None
