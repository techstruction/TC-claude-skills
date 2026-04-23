---
name: market-monday-transcripts
description: Extract transcripts from the Earn Your Leisure "Market Monday" YouTube playlist (313 episodes). Use when asked to fetch, batch-process, or check progress on Market Monday transcript extraction. Manages a CSV master checklist and saves each episode as a Markdown file.
---

# Market Monday Transcript Extraction Skill

Batch-extracts YouTube transcripts from the Earn Your Leisure Market Monday playlist
and saves them as structured Markdown files. Uses a CSV master checklist to track progress
across sessions. Designed for handoff to OpenClaw for autonomous scheduling.

**Playlist:** https://www.youtube.com/playlist?list=PLXa8HXFcKT961IieWfhylPvBNeH2cO8dY

## When to Use This Skill

- User asks to "fetch Market Monday transcripts" or "check transcript progress"
- User wants to run a batch or schedule autonomous extraction
- User asks about episode status, errors, or the master list
- Handing off to OpenClaw for scheduled runs

## Quick Commands

```bash
# Build master list (first time only)
python execution/01_fetch_playlist.py

# Check progress
python execution/03_status_report.py

# Run a batch (default: 5 episodes)
python execution/02_fetch_batch.py --count 5

# Run smaller batch
python execution/02_fetch_batch.py --count 2

# Start from a specific episode number
python execution/02_fetch_batch.py --count 5 --start-from 50
```

## Phase Guide

### Phase 1: Initialize (one time)
1. `cd TC-claude-skills/market-monday-transcripts`
2. `pip install yt-dlp youtube-transcript-api`
3. `python execution/01_fetch_playlist.py`
4. Verify: `python execution/03_status_report.py`

### Phase 2: Run Batches (repeat until done)
1. `python execution/02_fetch_batch.py --count 5`
2. Check output in `transcripts/`
3. `python execution/03_status_report.py`
4. Repeat or schedule

### Phase 3: Hand Off to OpenClaw
Read `HANDOFF.md` and follow the pre-flight checklist before scheduling.

## Data Files

| File | Purpose |
|---|---|
| `data/master_list.csv` | Master checklist — source of truth |
| `transcripts/EP{num:04d}_{slug}.md` | Output transcript files |
| `.tmp/batch.log` | Append-only batch run log |

## CSV Status Values

| Status | Meaning |
|---|---|
| `pending` | Not yet attempted |
| `done` | Transcript saved |
| `error` | Fetch failed (see notes column) |
| `no_transcript` | No captions available for this video |
| `skipped` | Intentionally skipped |

## Dependencies

```bash
pip install yt-dlp youtube-transcript-api
```

No API key needed. No browser needed. Works headless on any server.

## Architecture Notes

- Read `MASTERPLAN.md` for full design rationale
- Read `DECISIONS.md` for why specific tools were chosen
- Read `HANDOFF.md` before giving OpenClaw autonomous access
