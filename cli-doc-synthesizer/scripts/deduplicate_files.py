#!/usr/bin/env python3
"""
deduplicate_files.py

When Chrome downloads the same file twice (e.g., due to a retry), it creates
both 'filename.txt' and 'filename (1).txt'. This script deduplicates by keeping
the most recently modified version of each base name and copying to an output dir.

Usage:
    python deduplicate_files.py <input_dir> <output_dir>

Example:
    python deduplicate_files.py ~/Downloads/netapp_raw ~/work/netapp_raw_deduped
"""

import sys
import os
import shutil
import re
from pathlib import Path


def get_base_name(filename: str) -> str:
    """Strip Chrome's ' (N)' suffix from a filename stem."""
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    base_stem = re.sub(r'\s*\(\d+\)$', '', stem)
    return base_stem + suffix


def deduplicate(input_dir: str, output_dir: str) -> None:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group files by base name
    groups: dict[str, list[Path]] = {}
    for f in input_path.iterdir():
        if f.is_file():
            base = get_base_name(f.name)
            groups.setdefault(base, []).append(f)

    copied = 0
    for base_name, files in sorted(groups.items()):
        # Keep the most recently modified version
        best = max(files, key=lambda f: f.stat().st_mtime)
        dest = output_path / base_name
        shutil.copy2(best, dest)
        if len(files) > 1:
            dupes = [f.name for f in files if f != best]
            print(f"  Kept: {best.name}  (dropped: {', '.join(dupes)})")
        else:
            print(f"  Copied: {best.name}")
        copied += 1

    print(f"\nDone: {copied} unique files written to {output_path}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python deduplicate_files.py <input_dir> <output_dir>")
        sys.exit(1)
    deduplicate(sys.argv[1], sys.argv[2])
