# HANDOFF: Market Monday Transcript Extraction → OpenClaw

## What You're Taking Over
Autonomous batch extraction of transcripts from the Earn Your Leisure "Market Monday"
YouTube playlist. Tony has set up the system and run initial test batches. Your job is
to run batches on a schedule until all episodes are done.

**Playlist:** https://www.youtube.com/playlist?list=PLXa8HXFcKT961IieWfhylPvBNeH2cO8dY
**Total episodes:** ~313 (check `data/master_list.csv` for current count)
**Project dir:** `~/.claude/skills/market-monday-transcripts/`

---

## Pre-Flight Checklist (run before starting scheduled batches)

```bash
# 1. Verify dependencies are installed
pip install yt-dlp youtube-transcript-api

# 2. Check current state of master list
python execution/03_status_report.py

# 3. If master_list.csv doesn't exist yet, build it first
python execution/01_fetch_playlist.py

# 4. Run one manual test batch to verify everything works
python execution/02_fetch_batch.py --count 3

# 5. Check output
python execution/03_status_report.py
ls transcripts/ | head -10
```

---

## How to Schedule

Use Claude Code's `/schedule` skill or cron to run:

```bash
cd /path/to/TC-claude-skills/market-monday-transcripts && python execution/02_fetch_batch.py --count 5 >> .tmp/batch.log 2>&1
```

**Recommended schedule:** Every 3 minutes
**Batch size:** 5 (adjust down to 2-3 if errors appear)

Stop when `python execution/03_status_report.py` shows 0 pending.

---

## What Normal Looks Like

Each batch run prints something like:
```
Batch run — 2026-04-23 14:32:11
Processing 5 episodes...
  EP0042: done → transcripts/EP0042_market-monday-ep-42.md
  EP0043: done → transcripts/EP0043_market-monday-ep-43.md
  EP0044: no_transcript → skipped (no captions available)
  EP0045: done → transcripts/EP0045_market-monday-ep-45.md
  EP0046: done → transcripts/EP0046_market-monday-ep-46.md
Batch complete: 4 done, 1 no_transcript, 0 errors
Progress: 46/313 done (14.7%)
```

---

## What to Do If Things Break

| Problem | Fix |
|---|---|
| `TranscriptsDisabled` error | Mark as `no_transcript`, move on — this is normal for some episodes |
| `VideoUnavailable` | Mark as `error`, note in CSV, move on |
| Lots of `ConnectionError` | YouTube may be throttling — increase interval to 5+ min, reduce batch to 2 |
| Script crashes mid-batch | CSV is saved after each episode — re-run, it will skip already-done ones |
| `master_list.csv` missing | Run `python execution/01_fetch_playlist.py` to rebuild |

---

## When You're Done

1. Run `python execution/03_status_report.py` — confirm 0 pending
2. Note any episodes with `status=error` and decide if retry is needed
3. Write session summary to memU
4. Notify Tony that extraction is complete

---

## Files You Own

- `data/master_list.csv` — update status as you go (script does this automatically)
- `transcripts/*.md` — write-only, never delete
- `.tmp/batch.log` — append-only log (create `.tmp/` if missing)
