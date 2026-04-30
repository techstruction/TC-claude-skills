"""
source_ytdlp_subs.py
Source A: Download auto-generated VTT subtitle files via yt-dlp.

Uses a different HTTP code path than youtube-transcript-api — fetches .vtt files
directly from YouTube CDN rather than the timedtext endpoint that Oracle Cloud IPs
are blocked from. No API key required.
"""

import glob
import os
import re
import subprocess
import tempfile


def fetch(video_id):
    """
    Download auto-generated subtitles via yt-dlp and parse to clean paragraph text.
    Returns (text, None) on success, (None, error_str) on failure.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = os.path.join(tmpdir, "%(id)s")
        cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--sub-langs", "en.*",
            "--sub-format", "vtt",
            "--skip-download",
            "--no-playlist",
            "--quiet",
            "--no-warnings",
            "--output", out_template,
            url,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            return None, "ytdlp-subs:timeout"
        except FileNotFoundError:
            return None, "ytdlp-subs:yt-dlp not found"

        # Find the downloaded .vtt file
        vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
        if not vtt_files:
            stderr = result.stderr.strip()
            if "Sign in" in stderr or "blocked" in stderr.lower():
                return None, "ytdlp-subs:blocked"
            return None, "ytdlp-subs:no_vtt_file"

        vtt_path = vtt_files[0]
        with open(vtt_path, encoding="utf-8") as f:
            vtt_content = f.read()

    text = _parse_vtt(vtt_content)
    if not text:
        return None, "ytdlp-subs:empty_transcript"

    return text, None


def _parse_vtt(vtt_content):
    """
    Parse a WebVTT file into clean paragraph text.
    Strips timestamps, cue numbers, HTML tags, and duplicate lines that appear
    from overlapping captions (common in auto-generated YouTube VTTs).
    Groups into 5-line paragraph chunks to match the project's existing MD format.
    """
    lines = vtt_content.splitlines()
    cleaned = []
    seen = set()

    for line in lines:
        line = line.strip()
        # Skip blank lines, WEBVTT header, NOTE blocks, and timestamp lines
        if (not line
                or line.startswith("WEBVTT")
                or line.startswith("NOTE")
                or line.startswith("STYLE")
                or "-->" in line
                or re.match(r"^\d{2}:\d{2}:\d{2}", line)
                or re.match(r"^\d+$", line)):
            continue

        # Strip VTT inline tags: <c>, <i>, <b>, <00:00:00.000>, etc.
        line = re.sub(r"<[^>]+>", "", line)
        line = line.strip()

        if line and line not in seen:
            seen.add(line)
            cleaned.append(line)

    if not cleaned:
        return ""

    # Group into 5-line paragraph chunks
    chunks = []
    for i in range(0, len(cleaned), 5):
        chunks.append(" ".join(cleaned[i:i + 5]))

    return "\n\n".join(chunks)
