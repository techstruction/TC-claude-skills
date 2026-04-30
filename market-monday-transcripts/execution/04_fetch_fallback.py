#!/usr/bin/env python3
"""
04_fetch_fallback.py
Phase 4: Recover transcripts for episodes that couldn't be fetched via YouTube API or RSS.

Tries three sources in priority order (per episode):
  A) ytdlp-subs   — yt-dlp auto-generated subtitle download (free, different CDN path)
  B) playwright   — headless Chromium + stealth, intercepts YouTube's transcript XHR
  C) whisper      — audio download + local faster-whisper transcription (opt-in)

Targets rows with status=no_transcript. Updates master_list.csv after each episode.
The notes column tracks which methods were tried so re-runs are idempotent.

Usage:
    python execution/04_fetch_fallback.py                        # auto, 2 episodes
    python execution/04_fetch_fallback.py --method ytdlp-subs    # Source A only
    python execution/04_fetch_fallback.py --method playwright    # Source B only
    python execution/04_fetch_fallback.py --method whisper       # Source C only
    python execution/04_fetch_fallback.py --count 1 --delay 60   # 1 ep, 60s delay
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "master_list.csv")
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")
TMP_DIR = os.path.join(BASE_DIR, ".tmp")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "fallback.json")
LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CSV_COLUMNS = [
    "episode_num", "video_id", "title", "published_date", "url",
    "status", "transcript_file", "notes", "processed_at",
]

SOURCE_ORDER = ["ytdlp-subs", "playwright", "whisper"]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "default_method": "auto",
        "default_count": 2,
        "default_delay_seconds": 30,
        "sources": {
            "ytdlp-subs": {"enabled": True},
            "playwright": {"enabled": True},
            "whisper":    {"enabled": False, "model": "base"},
        },
    }


# ---------------------------------------------------------------------------
# CSV helpers (mirrors 02_fetch_batch.py patterns)
# ---------------------------------------------------------------------------

def load_csv(path):
    if not os.path.exists(path):
        print(f"ERROR: master_list.csv not found at {path}", file=sys.stderr)
        print("Run 01_fetch_playlist.py first.", file=sys.stderr)
        sys.exit(1)
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def format_markdown(row, transcript_text, source):
    num = int(row["episode_num"])
    return (
        f"# Market Monday EP{num:04d}: {row['title']}\n\n"
        f"**Video ID:** {row['video_id']}\n"
        f"**URL:** {row['url']}\n"
        f"**Published:** {row['published_date'] or 'Unknown'}\n"
        f"**Fetched:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"**Source:** {source}\n\n"
        f"---\n\n"
        f"## Transcript\n\n"
        f"{transcript_text}\n"
    )


def save_transcript(row, transcript_text, source):
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    num = int(row["episode_num"])
    slug = slugify(row["title"])
    filename = f"EP{num:04d}_{slug}.md"
    filepath = os.path.join(TRANSCRIPTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(format_markdown(row, transcript_text, source))
    return os.path.relpath(filepath, BASE_DIR)


def log_line(line):
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(os.path.join(TMP_DIR, "fallback.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------------------
# Source dispatch
# ---------------------------------------------------------------------------

def _load_source(name):
    """Import a source module by name. Returns the module or None."""
    try:
        if name == "ytdlp-subs":
            from lib import source_ytdlp_subs as mod
        elif name == "playwright":
            from lib import source_playwright as mod
        elif name == "whisper":
            from lib import source_whisper as mod
        else:
            return None
        return mod
    except ImportError:
        return None


def try_sources(video_id, methods, config, existing_notes):
    """
    Try each method in order. Returns (text, winning_method) or (None, None).
    Skips methods already recorded as failed in existing_notes.
    """
    cfg_sources = config.get("sources", {})

    for method in methods:
        src_cfg = cfg_sources.get(method, {})

        # Skip disabled sources unless explicitly requested
        if not src_cfg.get("enabled", True):
            print(f"    [{method}] disabled in config — skipping")
            continue

        # Skip if already tried and failed
        if f"{method}:failed" in existing_notes:
            print(f"    [{method}] already tried — skipping")
            continue

        print(f"    [{method}] trying...")
        mod = _load_source(method)
        if mod is None:
            print(f"    [{method}] module unavailable — skipping")
            continue

        kwargs = {}
        if method == "whisper":
            kwargs["model_size"] = src_cfg.get("model", "base")

        try:
            text, error = mod.fetch(video_id, **kwargs)
        except Exception as e:
            error = f"{method}:exception:{str(e)[:80]}"
            text = None

        if text:
            print(f"    [{method}] SUCCESS — {len(text)} chars")
            return text, method

        print(f"    [{method}] failed: {error}")

    return None, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    config = load_config()

    parser = argparse.ArgumentParser(
        description="Phase 4: Fallback transcript recovery for no_transcript episodes"
    )
    parser.add_argument(
        "--method",
        choices=["auto", "ytdlp-subs", "playwright", "whisper"],
        default=config.get("default_method", "auto"),
        help="Which source(s) to try (auto = all enabled in priority order)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=config.get("default_count", 2),
        help="Number of episodes to process (default: 2)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=config.get("default_delay_seconds", 30),
        help="Seconds to wait between episodes (default: 30)",
    )
    args = parser.parse_args()

    methods = SOURCE_ORDER if args.method == "auto" else [args.method]

    rows = load_csv(CSV_PATH)
    candidates = [r for r in rows if r["status"] == "no_transcript"]

    if not candidates:
        print("No no_transcript episodes found. All done (or none exist)!")
        return

    # Also exclude episodes where all requested methods are already marked failed
    def all_tried(row):
        notes = row.get("notes", "")
        return all(f"{m}:failed" in notes for m in methods)

    pending = [r for r in candidates if not all_tried(r)]

    if not pending:
        print(f"All no_transcript episodes have already been tried with: {methods}")
        print("Nothing new to attempt.")
        return

    batch = pending[:args.count]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_index = {r["video_id"]: i for i, r in enumerate(rows)}

    print(f"\nFallback run — {timestamp}")
    print(f"Method: {args.method}  |  Processing {len(batch)} episode(s)...")
    print(f"Target pool: {len(pending)} no_transcript episodes remaining\n")
    log_line(f"\n--- Fallback run {timestamp} | method={args.method} ---")

    stats = {"done": 0, "failed": 0}

    for ep_idx, row in enumerate(batch):
        ep_num = row["episode_num"].zfill(4)
        title_short = row["title"][:55]
        print(f"EP{ep_num}: {title_short}")

        existing_notes = row.get("notes", "")
        text, winning_method = try_sources(
            row["video_id"], methods, config, existing_notes
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        idx = row_index[row["video_id"]]

        if text:
            rel_path = save_transcript(row, text, winning_method)
            rows[idx]["status"] = "done"
            rows[idx]["transcript_file"] = rel_path
            rows[idx]["notes"] = f"source:{winning_method}"
            rows[idx]["processed_at"] = now
            stats["done"] += 1
            msg = f"  → done via {winning_method}: {rel_path}"
        else:
            # Append this run's failures to existing notes
            failed_tags = " ".join(
                f"{m}:failed" for m in methods
                if f"{m}:failed" not in existing_notes
            )
            new_notes = (existing_notes + " " + failed_tags).strip()
            rows[idx]["notes"] = new_notes
            rows[idx]["processed_at"] = now
            stats["failed"] += 1
            msg = f"  → all methods failed — noted in CSV"

        print(msg)
        log_line(f"EP{ep_num} {row['video_id']}: {msg.strip()}")
        save_csv(rows, CSV_PATH)

        # Delay between episodes (skip after the last one)
        if ep_idx < len(batch) - 1 and args.delay > 0:
            print(f"  (waiting {args.delay}s...)")
            time.sleep(args.delay)

    # Final summary
    total_no_transcript = sum(1 for r in rows if r["status"] == "no_transcript")
    total_done = sum(1 for r in rows if r["status"] == "done")
    total = len(rows)

    summary = (
        f"\nFallback complete: {stats['done']} recovered, {stats['failed']} still failed"
    )
    progress = (
        f"Overall: {total_done}/{total} done | "
        f"{total_no_transcript} no_transcript remaining"
    )
    print(summary)
    print(progress)
    log_line(summary)
    log_line(progress)

    if total_no_transcript == 0:
        print("\nAll episodes have transcripts!")
    else:
        print(f"\nNext: run again, or switch method if one source is blocked.")


if __name__ == "__main__":
    main()
