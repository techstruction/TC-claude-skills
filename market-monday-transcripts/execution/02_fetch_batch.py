#!/usr/bin/env python3
"""
02_fetch_batch.py
Phase 2: Fetch transcripts for the next N pending episodes and save as Markdown.

Updates master_list.csv after each episode (safe to interrupt and re-run).

Usage:
    python execution/02_fetch_batch.py               # fetch 5 (default)
    python execution/02_fetch_batch.py --count 10    # fetch 10
    python execution/02_fetch_batch.py --count 3 --start-from 50  # start at ep 50
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        CouldNotRetrieveTranscript,
    )
except ImportError:
    print("ERROR: youtube-transcript-api not installed.", file=sys.stderr)
    print("Run: pip install youtube-transcript-api", file=sys.stderr)
    sys.exit(1)

# v1.x uses instance-based API
_yt_api = YouTubeTranscriptApi()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "master_list.csv")
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")
TMP_DIR = os.path.join(BASE_DIR, ".tmp")

CSV_COLUMNS = [
    "episode_num", "video_id", "title", "published_date", "url",
    "status", "transcript_file", "notes", "processed_at",
]


def slugify(text):
    """Convert title to a safe filename slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def load_csv(csv_path):
    if not os.path.exists(csv_path):
        print(f"ERROR: master_list.csv not found at {csv_path}", file=sys.stderr)
        print("Run 01_fetch_playlist.py first.", file=sys.stderr)
        sys.exit(1)
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_csv(rows, csv_path):
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def fetch_transcript(video_id):
    """Fetch transcript text. Returns (text, None) or (None, error_type)."""
    try:
        # v1.x: instance-based, returns FetchedTranscript (iterable of dicts)
        fetched = _yt_api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        entries = list(fetched)
        # Group into ~5-entry chunks to form natural paragraphs
        # v1.x: entries are FetchedTranscriptSnippet objects with .text attribute
        chunks = []
        current = []
        for entry in entries:
            current.append(entry.text.strip())
            if len(current) >= 5:
                chunks.append(" ".join(current))
                current = []
        if current:
            chunks.append(" ".join(current))
        return "\n\n".join(chunks), None
    except TranscriptsDisabled:
        return None, "no_transcript"
    except NoTranscriptFound:
        # Try any available language as fallback
        try:
            transcript_list = _yt_api.list(video_id)
            transcript = transcript_list.find_generated_transcript(
                [t.language_code for t in transcript_list]
            )
            entries = list(transcript.fetch())
            text = " ".join(e.text.strip() for e in entries)
            return text, None
        except Exception:
            return None, "no_transcript"
    except VideoUnavailable:
        return None, "video_unavailable"
    except CouldNotRetrieveTranscript:
        return None, "no_transcript"
    except Exception as e:
        return None, f"error: {str(e)[:120]}"


def format_markdown(row, transcript_text):
    """Format a transcript as a Markdown document."""
    num = int(row["episode_num"])
    return f"""# Market Monday EP{num:04d}: {row['title']}

**Video ID:** {row['video_id']}
**URL:** {row['url']}
**Published:** {row['published_date'] or 'Unknown'}
**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Transcript

{transcript_text}
"""


def save_transcript(row, transcript_text):
    """Save transcript to transcripts/ dir. Returns the file path."""
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    num = int(row["episode_num"])
    slug = slugify(row["title"])
    filename = f"EP{num:04d}_{slug}.md"
    filepath = os.path.join(TRANSCRIPTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(format_markdown(row, transcript_text))
    return os.path.relpath(filepath, BASE_DIR)


def log_line(line):
    """Append a line to .tmp/batch.log."""
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(os.path.join(TMP_DIR, "batch.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(description="Fetch a batch of Market Monday transcripts")
    parser.add_argument("--count", type=int, default=5, help="Number of episodes to fetch (default: 5)")
    parser.add_argument("--start-from", type=int, default=None, help="Start from this episode number")
    args = parser.parse_args()

    rows = load_csv(CSV_PATH)

    # Find pending rows in order
    pending = [r for r in rows if r["status"] == "pending"]
    if args.start_from:
        pending = [r for r in pending if int(r["episode_num"]) >= args.start_from]

    if not pending:
        print("No pending episodes found. All done!")
        return

    batch = pending[:args.count]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\nBatch run — {timestamp}")
    print(f"Processing {len(batch)} episodes...\n")
    log_line(f"\n--- Batch run {timestamp} ---")

    # Build index for fast row lookup
    row_index = {r["video_id"]: i for i, r in enumerate(rows)}

    stats = {"done": 0, "no_transcript": 0, "error": 0}

    for row in batch:
        ep_num = row["episode_num"].zfill(4)
        title_short = row["title"][:60]
        print(f"  EP{ep_num}: {title_short}")

        transcript_text, error_type = fetch_transcript(row["video_id"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        idx = row_index[row["video_id"]]

        if transcript_text:
            rel_path = save_transcript(row, transcript_text)
            rows[idx]["status"] = "done"
            rows[idx]["transcript_file"] = rel_path
            rows[idx]["notes"] = ""
            rows[idx]["processed_at"] = now
            stats["done"] += 1
            msg = f"    → done: {rel_path}"
        elif error_type == "no_transcript":
            rows[idx]["status"] = "no_transcript"
            rows[idx]["notes"] = "No captions available"
            rows[idx]["processed_at"] = now
            stats["no_transcript"] += 1
            msg = f"    → no_transcript (no captions available)"
        else:
            rows[idx]["status"] = "error"
            rows[idx]["notes"] = error_type
            rows[idx]["processed_at"] = now
            stats["error"] += 1
            msg = f"    → error: {error_type}"

        print(msg)
        log_line(f"EP{ep_num} {row['video_id']}: {msg.strip()}")

        # Save CSV after each episode so interruption doesn't lose progress
        save_csv(rows, CSV_PATH)

    total_done = sum(1 for r in rows if r["status"] == "done")
    total_no_transcript = sum(1 for r in rows if r["status"] == "no_transcript")
    total_pending = sum(1 for r in rows if r["status"] == "pending")
    total = len(rows)

    summary = (
        f"\nBatch complete: {stats['done']} done, "
        f"{stats['no_transcript']} no_transcript, "
        f"{stats['error']} errors"
    )
    progress = f"Overall progress: {total_done + total_no_transcript}/{total} processed ({total_pending} pending)"

    print(summary)
    print(progress)
    log_line(summary)
    log_line(progress)

    if total_pending == 0:
        print("\nAll episodes processed!")
    else:
        print(f"\nNext: run again to continue, or check status with 03_status_report.py")


if __name__ == "__main__":
    main()
