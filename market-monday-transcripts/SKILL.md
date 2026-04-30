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

---

## Phase 4: Fallback Recovery (for `no_transcript` episodes)

85 episodes couldn't be reached via YouTube API (Oracle Cloud IP blocked) or podcast RSS
(pre-2022 episodes). Phase 4 uses three alternative sources with no external API keys.

### Install (Source B + C)
```bash
pip install playwright playwright-stealth
playwright install chromium          # ~150MB ARM64 Chromium

pip install faster-whisper           # Source C only — opt-in
```

### Quick Commands
```bash
# Step 1: Try yt-dlp subtitle download first (free, fast, different CDN path)
python execution/04_fetch_fallback.py --method ytdlp-subs --count 2

# Step 2: Try Playwright browser automation (our own supadata-like implementation)
python execution/04_fetch_fallback.py --method playwright --count 1

# Step 3: Whisper — enable in config/fallback.json first, then:
python execution/04_fetch_fallback.py --method whisper --count 1

# Auto mode (tries all enabled sources per episode, in order)
python execution/04_fetch_fallback.py --count 2

# With longer delay between episodes (recommended for playwright)
python execution/04_fetch_fallback.py --method playwright --count 2 --delay 60
```

### Fallback Source Priority
| Source | Method | API Key | Speed | Notes |
|--------|--------|---------|-------|-------|
| A | `ytdlp-subs` | None | Fast | Different CDN path — try first |
| B | `playwright` | None | ~30s/ep | Headless Chrome + stealth mode |
| C | `whisper` | None | ~10min/ep | Audio download + local transcription |

### Scheduling (post-test)
- If ytdlp-subs works: `--count 2` every 5 min → done in ~3.5 hrs
- If blocked, use playwright: `--count 2` every 10 min → done in ~7 hrs
- Whisper as last resort: `--count 1` every 45 min → done in ~64 hrs

### Log Files
| File | Purpose |
|---|---|
| `.tmp/fallback.log` | Append-only fallback run log |
| `config/fallback.json` | Source enable/disable, default settings |
