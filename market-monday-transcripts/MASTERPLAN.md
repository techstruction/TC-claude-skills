# MASTERPLAN: Market Monday Transcript Extraction

## Goal
Extract full transcripts from all episodes of the Earn Your Leisure "Market Monday" YouTube playlist
and save each as a structured Markdown file. Use a master CSV as a checklist to track progress,
enabling batch runs and autonomous scheduling via OpenClaw.

**Playlist:** https://www.youtube.com/playlist?list=PLXa8HXFcKT961IieWfhylPvBNeH2cO8dY
**Est. episodes:** 313 (as of April 2026)
**Output format:** One `.md` file per episode in `transcripts/`

---

## Architecture

```
market-monday-transcripts/
  SKILL.md                  # Claude reads before executing this skill
  MASTERPLAN.md             # This file
  CLAUDE.md                 # Project constitution
  HANDOFF.md                # Handoff doc for OpenClaw
  DECISIONS.md              # Decision log
  execution/
    01_fetch_playlist.py    # Phase 1: build master_list.csv from playlist
    02_fetch_batch.py       # Phase 2: fetch N transcripts, update CSV, save MDs
    03_status_report.py     # Anytime: print progress summary
  data/
    master_list.csv         # Master checklist (created by 01_, updated by 02_)
  transcripts/              # EP0001_title-slug.md, EP0002_..., etc.
```

---

## Phases

### Phase 1 — Build Master List (run once)
Run `execution/01_fetch_playlist.py` to:
1. Pull all video IDs, titles, and publish dates from the playlist using `yt-dlp`
2. Write `data/master_list.csv` with columns:
   `episode_num, video_id, title, published_date, url, status, transcript_file, notes, processed_at`
3. All episodes start with `status=pending`

### Phase 2 — Batch Transcript Extraction (repeating)
Run `execution/02_fetch_batch.py --count 5` to:
1. Read `master_list.csv`
2. Pick the next N episodes with `status=pending` (in order)
3. For each episode:
   - Fetch transcript via `youtube_transcript_api` (headless, no browser needed)
   - Save to `transcripts/EP{num:04d}_{slug}.md`
   - Update CSV: `status=done`, `transcript_file=<path>`, `processed_at=<timestamp>`
   - On failure: `status=error`, `notes=<error message>`
4. Print summary and save CSV

### Phase 3 — Status Check (anytime)
Run `execution/03_status_report.py` to see:
- Total | Done | Pending | Errors
- Next up (next 5 pending episodes)
- ETA at current batch rate

---

## Scheduling Strategy

**On MBP (Tony, interactive):**
- Test runs manually: `python execution/02_fetch_batch.py --count 5`
- Verify output quality before handing off

**On OpenClaw (autonomous):**
- Schedule via cron or Claude Code's `/schedule` skill
- Suggested interval: every 3 minutes, batch size 3-5
- Run until `master_list.csv` shows 0 pending
- Check `03_status_report.py` after each run

**Rate limiting:**
- YouTube's transcript API is generous but not unlimited
- Batch size 5 every 3 minutes = ~100 episodes/hour = ~3 hours total
- If errors spike, reduce to batch size 2 and increase interval to 5 minutes

---

## Output Format (per episode)

```markdown
# Market Monday EP0001: {Title}

**Video ID:** {video_id}
**URL:** https://www.youtube.com/watch?v={video_id}
**Published:** {date}
**Fetched:** {timestamp}

---

## Transcript

{Full transcript text, one paragraph per speaker block}
```

---

## Dependencies

```bash
pip install yt-dlp youtube-transcript-api
```

`yt-dlp` — playlist metadata (video IDs, titles, dates)
`youtube-transcript-api` — transcript fetching (headless, no browser, no API key)

---

## Known Constraints

- Some episodes may have no transcript (auto-captions disabled by creator)
  → Mark as `status=no_transcript` in CSV, note in `notes` column
- Episode count may grow — re-run `01_fetch_playlist.py` to append new episodes
- Do NOT re-run `01_fetch_playlist.py` if `master_list.csv` already has progress
  → It appends new entries, never overwrites existing rows

---

## Success Criteria

- [ ] `master_list.csv` contains all episodes
- [ ] All `status=done` or `status=no_transcript` (nothing pending)
- [ ] Each done episode has a valid `.md` file in `transcripts/`
- [ ] Error rate < 5%
