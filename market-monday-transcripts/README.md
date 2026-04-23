# Market Monday Transcript Extraction

Extracts full transcripts from every episode of the Earn Your Leisure **Market Monday**
YouTube playlist and saves each as a structured Markdown file.

**Playlist:** https://www.youtube.com/playlist?list=PLXa8HXFcKT961IieWfhylPvBNeH2cO8dY
**Episodes:** ~313 (and growing)
**Output:** One `.md` file per episode in `transcripts/`
**Progress tracking:** `data/master_list.csv` — master checklist updated after every episode

---

## Quick Start (5 minutes to first transcript)

```bash
# 1. Install dependencies (no API key needed, works headless)
pip install yt-dlp youtube-transcript-api

# 2. Build the master list (run once)
python execution/01_fetch_playlist.py

# 3. Check what was found
python execution/03_status_report.py

# 4. Fetch your first batch
python execution/02_fetch_batch.py --count 5

# 5. See the output
ls transcripts/
python execution/03_status_report.py
```

---

## Requirements

| Dependency | Purpose | Install |
|---|---|---|
| `yt-dlp` | Fetch playlist metadata (video IDs, titles, dates) | `pip install yt-dlp` |
| `youtube-transcript-api` | Fetch transcripts headlessly, no browser needed | `pip install youtube-transcript-api` |
| Python 3.8+ | Runtime | — |

No API keys. No browser. No authentication. Works on any server.

---

## Directory Structure

```
market-monday-transcripts/
  README.md                   # This file — start here
  SKILL.md                    # Claude Code skill definition
  MASTERPLAN.md               # Full architecture and design rationale
  CLAUDE.md                   # Project rules and operating principles
  DECISIONS.md                # Why specific tools and approaches were chosen
  HANDOFF.md                  # Instructions for handing off to OpenClaw
  .gitignore                  # Excludes transcripts/, data/, .tmp/
  execution/
    01_fetch_playlist.py      # Phase 1: build master_list.csv (run once)
    02_fetch_batch.py         # Phase 2: fetch N transcripts, save MDs
    03_status_report.py       # Anytime: check progress
  data/                       # Created by 01_ — gitignored
    master_list.csv           # Master checklist (source of truth)
  transcripts/                # Output MD files — gitignored (too large)
    EP0001_title-slug.md
    EP0002_...
  .tmp/                       # Logs — gitignored
    batch.log
```

---

## Step-by-Step Usage

### Phase 1 — Build the Master List (once)

```bash
python execution/01_fetch_playlist.py
```

- Downloads playlist metadata using `yt-dlp` (no video download, just IDs/titles/dates)
- Creates `data/master_list.csv` with all episodes, status set to `pending`
- Takes ~30–60 seconds for 300+ episodes
- **Safe to re-run** — appends new episodes without overwriting existing progress

**Expected output:**
```
Fetching playlist metadata from YouTube...
Found 313 videos in playlist.
Master list saved: data/master_list.csv
  Total episodes: 313
  New this run:   313
```

---

### Phase 2 — Fetch Transcripts in Batches

```bash
# Default: fetch next 5 pending episodes
python execution/02_fetch_batch.py

# Custom batch size
python execution/02_fetch_batch.py --count 10

# Start from a specific episode number
python execution/02_fetch_batch.py --count 5 --start-from 50
```

- Reads `data/master_list.csv`, picks the next N with `status=pending`
- Fetches each transcript via YouTube's transcript API
- Saves to `transcripts/EP{num:04d}_{slug}.md`
- Updates CSV after **each episode** (safe to interrupt and resume)

**Expected output:**
```
Batch run — 2026-04-23 10:04:12
Processing 5 episodes...

  EP0004: Market Turmoil — What You Need To Do Right Now
    → done: transcripts/EP0004_market-turmoil-what-you-need-to-do-right-now.md
  EP0005: Is The Market Crash Over… Or Just Getting Started?
    → done: transcripts/EP0005_is-the-market-crash-over-or-just-getting-started.md
  EP0006: The Next Market Crash? Nvidia's Future, Oil To $100?
    → done: transcripts/EP0006_the-next-market-crash-nvidias-future-oil-to-100.md
  EP0007: Iran War Market Manipulation? 🚨 Oil Chaos & How to Profit
    → no_transcript (no captions available)
  EP0008: The Iran War🚨, Oil Spikes, & AI Layoffs
    → done: transcripts/EP0008_the-iran-war-oil-spikes-ai-layoffs.md

Batch complete: 4 done, 1 no_transcript, 0 errors
Overall progress: 8/313 processed (305 pending)
```

---

### Check Progress (anytime)

```bash
# Standard report
python execution/03_status_report.py

# Show next 10 pending (default is 5)
python execution/03_status_report.py --next 10

# Show error details
python execution/03_status_report.py --errors
```

**Expected output:**
```
==================================================
  Market Monday Transcript Progress
==================================================
  [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20.1%

  Total episodes : 313
  Done           : 57
  No transcript  : 6
  Pending        : 250
  Errors         : 0
==================================================

  Next 5 pending:
    EP0064: Earnings Season Breakdown & What It Means For Your Portfolio
    ...

  ETA at default rate (5 eps/3min): ~25 min
```

---

## Output Format

Each transcript is saved as a Markdown file:

```markdown
# Market Monday EP0001: Tim Cook Leaves Apple! | Market Crash Coming?

**Video ID:** LDQYAZQgAjg
**URL:** https://www.youtube.com/watch?v=LDQYAZQgAjg
**Published:** 2026-04-07
**Fetched:** 2026-04-23 10:04:14

---

## Transcript

For me, entrepreneurship has always been the way. Investing is important
because it's the only way you are going to be able to be rich and wealthy
for your family.

[music] We can close the wealth gap by working together. Market Mondays
is the biggest investment show ever...
```

---

## Master List CSV Schema

`data/master_list.csv` columns:

| Column | Description |
|---|---|
| `episode_num` | Playlist position (1-based) — used for file naming |
| `video_id` | YouTube video ID |
| `title` | Full episode title |
| `published_date` | YYYY-MM-DD (from YouTube metadata) |
| `url` | Full YouTube watch URL |
| `status` | `pending` / `done` / `error` / `no_transcript` / `skipped` |
| `transcript_file` | Relative path to saved `.md` file |
| `notes` | Error message or other notes |
| `processed_at` | Timestamp of last processing attempt |

---

## Running as a Scheduled Job

To run autonomously until all episodes are done:

**Shell loop (quick and simple):**
```bash
while python3 -c "
import csv
rows = list(csv.DictReader(open('data/master_list.csv')))
exit(0 if any(r['status']=='pending' for r in rows) else 1)
"; do
  python execution/02_fetch_batch.py --count 5
  sleep 180   # 3 minutes between batches
done
echo "All done!"
```

**Cron job (every 3 minutes):**
```cron
*/3 * * * * cd /path/to/market-monday-transcripts && python execution/02_fetch_batch.py --count 5 >> .tmp/batch.log 2>&1
```

**Via Claude Code `/schedule` skill:**
- Open this project in Claude Code
- Run `/schedule` and describe: "Run `python execution/02_fetch_batch.py --count 5` every 3 minutes until all 313 episodes are done"

**Recommended settings:**
- Batch size: 5 (safe default) — increase to 10 if no errors after 30 batches
- Interval: 3 minutes
- Total time at defaults: ~3 hours for all 313 episodes

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `No captions available` → `no_transcript` | Creator disabled transcripts | Normal — skip and continue |
| `VideoUnavailable` → `error` | Video was deleted or made private | Mark as error, continue |
| Lots of connection errors | YouTube rate limiting | Reduce batch to 2, increase interval to 5 min |
| Script crashes mid-batch | Any exception | CSV is saved per episode — just re-run |
| `master_list.csv` missing | Deleted or first run | Run `01_fetch_playlist.py` |
| New episodes added to playlist | Playlist grew | Re-run `01_fetch_playlist.py` — it appends only |
| Wrong Python version | Needs 3.8+ | `python3 --version` to check |

---

## Handing Off to OpenClaw

See `HANDOFF.md` for the complete pre-flight checklist and scheduling instructions
tailored for autonomous operation on a headless server.

---

## Design Decisions

See `DECISIONS.md` for the full rationale. Key choices:

- **`youtube-transcript-api`** for transcripts — headless, no browser, no API key
- **`yt-dlp`** for playlist metadata — handles pagination, no auth needed
- **CSV** for progress tracking — human-readable, no database, easy to inspect
- **No LLM calls during batch runs** — raw transcripts only, zero token cost
- **Save CSV after each episode** — safe to interrupt at any point
