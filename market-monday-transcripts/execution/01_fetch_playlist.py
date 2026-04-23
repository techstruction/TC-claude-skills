#!/usr/bin/env python3
"""
01_fetch_playlist.py
Phase 1: Build master_list.csv from the Market Monday YouTube playlist.

Run once to initialize. Safe to re-run — appends new episodes, never overwrites
rows that already have progress (status != pending).

Usage:
    python execution/01_fetch_playlist.py
"""

import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLXa8HXFcKT961IieWfhylPvBNeH2cO8dY"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "master_list.csv")

CSV_COLUMNS = [
    "episode_num",
    "video_id",
    "title",
    "published_date",
    "url",
    "status",
    "transcript_file",
    "notes",
    "processed_at",
]


def load_existing(csv_path):
    """Return dict of video_id -> row for any already-tracked episodes."""
    existing = {}
    if not os.path.exists(csv_path):
        return existing
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing[row["video_id"]] = row
    return existing


def fetch_playlist_videos():
    """Use yt-dlp to get all video IDs, titles, and dates from the playlist."""
    print(f"Fetching playlist metadata from YouTube...")
    print(f"URL: {PLAYLIST_URL}")
    print("This may take 30-60 seconds for a large playlist...\n")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(upload_date)s",
        "--no-warnings",
        PLAYLIST_URL,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: yt-dlp failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        video_id = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ""
        raw_date = parts[2].strip() if len(parts) > 2 else ""

        # Format date as YYYY-MM-DD if available
        pub_date = ""
        if raw_date and len(raw_date) == 8:
            pub_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"

        videos.append({
            "video_id": video_id,
            "title": title,
            "published_date": pub_date,
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })

    return videos


def make_row(episode_num, video, existing_row=None):
    """Build a CSV row, preserving existing progress if present."""
    if existing_row:
        # Keep existing progress, just update episode_num if it changed
        existing_row["episode_num"] = str(episode_num)
        return existing_row

    return {
        "episode_num": str(episode_num),
        "video_id": video["video_id"],
        "title": video["title"],
        "published_date": video["published_date"],
        "url": video["url"],
        "status": "pending",
        "transcript_file": "",
        "notes": "",
        "processed_at": "",
    }


def write_csv(rows, csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    existing = load_existing(CSV_PATH)
    had_existing = bool(existing)

    if had_existing:
        done_count = sum(1 for r in existing.values() if r["status"] != "pending")
        print(f"Found existing master_list.csv with {len(existing)} episodes ({done_count} with progress).")
        print("Will append any new episodes. Existing progress is preserved.\n")

    videos = fetch_playlist_videos()

    if not videos:
        print("ERROR: No videos returned from playlist. Check the URL and yt-dlp install.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(videos)} videos in playlist.")

    rows = []
    new_count = 0
    for i, video in enumerate(videos, start=1):
        existing_row = existing.get(video["video_id"])
        if not existing_row:
            new_count += 1
        rows.append(make_row(i, video, existing_row))

    write_csv(rows, CSV_PATH)

    print(f"\nMaster list saved: {CSV_PATH}")
    print(f"  Total episodes: {len(rows)}")
    print(f"  New this run:   {new_count}")
    if had_existing:
        print(f"  Existing rows:  {len(existing)} (progress preserved)")
    print("\nNext step: python execution/03_status_report.py")


if __name__ == "__main__":
    main()
