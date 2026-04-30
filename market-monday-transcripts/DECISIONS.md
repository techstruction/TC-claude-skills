# Decisions Log

## 2026-04-23 — Initial Design

### D1: Use `youtube-transcript-api` instead of `autocli` for transcript fetching
**Decision:** Primary transcript fetcher is the `youtube-transcript-api` Python library.
**Why:** autocli requires Chrome open (browser mode) — not viable for headless OpenClaw.
`youtube-transcript-api` is headless, no API key, no browser, works on any server.
**Trade-off:** autocli would work on MBP during testing but fails on handoff target.
Consistency matters more than using the existing autocli skill here.

### D2: Use `yt-dlp` for playlist metadata
**Decision:** `yt-dlp --flat-playlist` to enumerate all episodes and their metadata.
**Why:** No playlist command in autocli for YouTube. yt-dlp is the standard tool for this,
handles pagination, and returns structured data cleanly.
**Alternative considered:** YouTube Data API v3 — rejected because it requires an API key
and has quota limits. yt-dlp needs nothing.

### D3: CSV as master checklist (not SQLite, not Google Sheets)
**Decision:** `data/master_list.csv` is the progress tracker.
**Why:** Simple, human-readable, version-controllable, no dependencies.
OpenClaw can read/write it easily. Easy to inspect in any spreadsheet app.
**Trade-off:** Not concurrent-safe (single writer). Acceptable since batch runs are sequential.

### D4: Batch size 5, interval 3 minutes (default recommendation)
**Decision:** Default batch of 5 episodes per run, scheduled every 3 minutes.
**Why:** Conservative rate to avoid YouTube throttling. 5 × 20 batches/hour = 100/hr.
313 episodes ÷ 100/hr ≈ 3.1 hours total. Low risk of API abuse.
**Adjustable:** If no errors after 20 batches, can increase to 10/batch.

### D5: Episode numbering based on playlist order, not publish date
**Decision:** `episode_num` is the index in the playlist (1-based), not a parsed episode number.
**Why:** Episode titles don't always contain a reliable episode number. Playlist order is authoritative.
Transcript files are named `EP{num:04d}_{slug}.md` using this index.

### D7: yt-dlp subtitle download as Source A for fallback (Phase 4)
**Decision:** First fallback attempts `yt-dlp --write-auto-sub` to download VTT subtitle files.
**Why:** yt-dlp fetches subtitle files from YouTube's CDN (`googlevideo.com`) — a different request
path than the `timedtext` transcript API endpoint that Oracle Cloud IPs are blocked from.
No API key, no install beyond yt-dlp which is already present. Costs nothing to try first.
**Trade-off:** May still be blocked on some IPs; if so, falls through to Source B.

### D8: Playwright + stealth as Source B — no third-party API
**Decision:** Build our own headless Chromium automation rather than using paid services
(supadata.ai, noteGPT.io, turboscribe.ai etc.).
**Why:** All those services do the same thing under the hood: headless browser + stealth mode
triggers YouTube's internal `/youtubei/v1/get_transcript` XHR and captures the JSON.
Building it ourselves means no API keys, no freemium limits, no third-party dependency.
Playwright + playwright-stealth on ARM64 is fully supported.
**Trade-off:** ~400MB RAM per browser instance; ~30-40s per episode vs instant API call.
Acceptable given we run 1-2 at a time on a scheduled interval.

### D9: faster-whisper over openai-whisper for Source C
**Decision:** Use `faster-whisper` (CTranslate2 backend) with `int8` quantization.
**Why:** int8 quantization is significantly faster on ARM64 CPU with no CUDA.
Lower memory footprint than float32. Same transcription quality for the `base` model.
Disabled by default because it's CPU-heavy; user opts in via `config/fallback.json`.
**Trade-off:** Slightly reduced accuracy vs float32 — acceptable for this use case.

### D6: No Claude API calls during batch runs
**Decision:** The batch runner scripts do not call Claude or any LLM.
**Why:** Goal is "don't consume a lot of tokens." Transcripts are fetched raw and saved as-is.
Claude can be used later to summarize or process transcripts in a separate workflow.
