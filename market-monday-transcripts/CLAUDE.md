# Market Monday Transcript Extraction — Project Constitution

## What This Is
A skill + execution system to extract all transcripts from the Earn Your Leisure
"Market Monday" YouTube playlist and save them as structured Markdown files.

## Playlist
https://www.youtube.com/playlist?list=PLXa8HXFcKT961IieWfhylPvBNeH2cO8dY

## Working Directory
`TC-claude-skills/market-monday-transcripts/`

## Core Rules

1. **Never overwrite progress** — `data/master_list.csv` is the source of truth.
   Before running `01_fetch_playlist.py`, check if the file exists. If it does,
   it will append new episodes — not reset existing ones.

2. **Status values are strict:**
   - `pending` — not yet attempted
   - `done` — transcript saved successfully
   - `error` — fetch failed (see `notes` column for reason)
   - `no_transcript` — video has no available transcript
   - `skipped` — intentionally skipped

3. **Always run `03_status_report.py` before and after a batch** so you know where you are.

4. **Batch size default is 5.** Don't go above 10 per run to avoid rate limiting.

5. **Transcript files go in `transcripts/` only.** Naming: `EP{num:04d}_{slug}.md`
   where slug is the title lowercased, spaces replaced with hyphens, special chars stripped.

## How to Run a Session

```bash
# First time only: build master list
python execution/01_fetch_playlist.py

# Check status
python execution/03_status_report.py

# Run a batch
python execution/02_fetch_batch.py --count 5

# Repeat until done
```

## Handoff Target
OpenClaw — see HANDOFF.md for autonomous scheduling instructions.
