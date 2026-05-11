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

## How It Runs (Automated)

A CRON job fires every Monday at 10 PM and handles the full workflow automatically:

```
0 22 * * 1 /home/ubuntu/.claude/skills/market-monday-transcripts/execution/05_scheduled_run.sh \
           >> /home/ubuntu/.claude/skills/market-monday-transcripts/.tmp/scheduled_run.log 2>&1
```

`05_scheduled_run.sh` does the following in sequence:
1. **Concurrency guard** — exits immediately if another instance is already running (flock-based, race-free)
2. **Daily masterlist refresh** — runs `01_fetch_playlist.py` if `master_list.csv` is older than 23 hours, picking up any new EYL episodes automatically
3. **Early exit if nothing to do** — if 0 pending episodes, the script exits cleanly without running anything
4. **Batch fetch** — runs `02_fetch_batch.py --count 5` to process the next 5 pending episodes
5. **OneDrive rsync** — syncs `transcripts/` and `master_list.csv` to `onedrive:Backups/oracle-server/market-monday-transcripts/`

**You don't need to do anything to keep this running.** New EYL Market Monday episodes are auto-detected within 24 hours of release and processed within 5 minutes of detection.

### Manual override (run a batch right now)
```bash
cd /home/ubuntu/.claude/skills/market-monday-transcripts
.venv/bin/python execution/02_fetch_batch.py --count 5
```

### Check progress
```bash
cd /home/ubuntu/.claude/skills/market-monday-transcripts
.venv/bin/python execution/03_status_report.py
```

### Check scheduler log
```bash
tail -50 /home/ubuntu/.claude/skills/market-monday-transcripts/.tmp/scheduled_run.log
```

### Trigger a manual playlist refresh (check for new episodes now)
```bash
cd /home/ubuntu/.claude/skills/market-monday-transcripts
.venv/bin/python execution/01_fetch_playlist.py
```

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
