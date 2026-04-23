#!/usr/bin/env python3
"""
03_status_report.py
Print a progress summary of the Market Monday transcript extraction.

Usage:
    python execution/03_status_report.py
    python execution/03_status_report.py --errors    # show error details
    python execution/03_status_report.py --next 10   # show next N pending
"""

import argparse
import csv
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "master_list.csv")


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


def main():
    parser = argparse.ArgumentParser(description="Show Market Monday transcript extraction progress")
    parser.add_argument("--errors", action="store_true", help="Show error details")
    parser.add_argument("--next", type=int, default=5, metavar="N", help="Show next N pending episodes (default: 5)")
    args = parser.parse_args()

    rows = load_csv(CSV_PATH)

    by_status = {}
    for row in rows:
        s = row["status"]
        by_status.setdefault(s, []).append(row)

    total = len(rows)
    done = len(by_status.get("done", []))
    no_transcript = len(by_status.get("no_transcript", []))
    pending = len(by_status.get("pending", []))
    errors = len(by_status.get("error", []))
    processed = done + no_transcript

    bar_width = 40
    filled = int(bar_width * processed / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_width - filled)
    pct = 100 * processed / total if total > 0 else 0

    print(f"\n{'='*50}")
    print(f"  Market Monday Transcript Progress")
    print(f"{'='*50}")
    print(f"  [{bar}] {pct:.1f}%")
    print(f"")
    print(f"  Total episodes : {total}")
    print(f"  Done           : {done}")
    print(f"  No transcript  : {no_transcript}")
    print(f"  Pending        : {pending}")
    print(f"  Errors         : {errors}")
    print(f"{'='*50}")

    if pending > 0:
        # ETA estimate: base on last processed_at timestamps if available
        next_pending = [r for r in rows if r["status"] == "pending"][:args.next]
        print(f"\n  Next {min(args.next, len(next_pending))} pending:")
        for r in next_pending:
            print(f"    EP{r['episode_num'].zfill(4)}: {r['title'][:65]}")

    if args.errors and errors > 0:
        print(f"\n  Error details:")
        for r in by_status.get("error", []):
            print(f"    EP{r['episode_num'].zfill(4)} ({r['video_id']}): {r['notes']}")

    if pending == 0 and errors == 0:
        print(f"\n  All episodes processed! Extraction complete.")
    elif pending == 0 and errors > 0:
        print(f"\n  All pending done. {errors} episodes need retry (run with --errors to see).")
    else:
        # Rough ETA at 5 eps/3min rate
        batches_remaining = (pending / 5)
        eta_minutes = batches_remaining * 3
        if eta_minutes < 60:
            eta_str = f"~{eta_minutes:.0f} min"
        else:
            eta_str = f"~{eta_minutes/60:.1f} hr"
        print(f"\n  ETA at default rate (5 eps/3min): {eta_str}")

    print()


if __name__ == "__main__":
    main()
