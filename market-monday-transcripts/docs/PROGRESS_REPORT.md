# Market Mondays Transcript Project - Progress Report

**Last Updated:** April 28, 2026

## What Was Accomplished

### 1. Skill Installation
- Installed `market-monday-transcripts` skill from `TC-claude-skills` repo
- Set up Python venv with dependencies: `yt-dlp`, `youtube-transcript-api`
- Created data directory structure with master playlist CSV

### 2. Transcript Extraction - Two Phases

**Phase 1: YouTube API (FAILED)**
- Initial attempts to fetch transcripts via YouTube Transcript API
- Processing 2 episodes per batch
- Got rate limited after ~80 episodes
- Error: `RequestBlocked` - YouTube blocks requests from Oracle Cloud IP

**Phase 2: Podcast RSS Feed (SUCCESS)**
- Discovered transcripts available in podcast RSS feed
- Modified script to fetch from RedCircle RSS: `https://feeds.redcircle.com/34df7015-ce8e-4451-bfa2-dd4ffe91e8b7`
- Cron job: 2 transcripts every 3 minutes
- Successfully extracted **229 transcripts**

### 3. Final Coverage
| Status | Count |
|--------|-------|
| Total episodes | 314 |
| Transcripts obtained | 229 |
| No transcript available | 85 |
| Errors | 0 |

**Episodes WITH transcripts:**
- EP38-49, 70-199, 220-293, 302-314

**Episodes WITHOUT transcripts:**
- EP001-37, 50-69 (pre-2022, before podcast had transcripts)
- EP200-219, 294-301 (not in podcast RSS)

## Transcripts Storage Location

```
~/.claude/skills/market-monday-transcripts/transcripts/
├── EP38_*.vtt    # VTT files with full timestamps
├── EP38_*.md     # Markdown wrapper
├── EP39_*.vtt
└── ... (229 files total)
```

## Lessons Learned

### 1. YouTube API Rate Limiting
- **Issue:** YouTube aggressively blocks requests from cloud provider IPs (AWS, GCP, Azure, Oracle)
- **Error:** `RequestBlocked` exception
- **Cause:** Our Oracle Cloud IP was flagged after ~80 requests
- **Recovery:** Still blocked after 24+ hours of cooldown

### 2. Podcast RSS Coverage
- **Finding:** Only ~50 most recent episodes have VTT transcripts in RedCircle feed
- **Reason:** Podcast host (RedCircle) only started including transcripts recently
- **Result:** Gap in coverage for older episodes

### 3. Transcript Source Priority
1. **Best:** Podcast RSS (if available) - clean, timestamped, no API issues
2. **Good:** YouTube (with cooldown) - but blocked from cloud IPs
3. **Paid:** Podscan API - $200/mo for full access

### 4. Request Rate Strategy
- Recommended: 1-2 episodes per request
- Cooldown: 3+ minutes between batches if using YouTube
- Avoid cloud providers if possible

## Errors to Learn From

1. **Initial batch size too large:** Tried 20+ episodes at once → triggered rate limit faster
2. **No cooldown strategy:** Should have started with longer intervals from the beginning
3. **Assumed YouTube would work:** Cloud provider IPs are automatically blocked
4. **No proxy fallback:** Could have set up proxy rotation earlier

## Alternative Options for Missing Episodes

1. **Podscan API ($200/mo)** - Would provide all transcripts programmatically
2. **Patreon membership ($4-10/mo)** - Some patron-only posts
3. **Home network run** - Run script from non-cloud IP to bypass YouTube block
4. **Manual lookup** - Individual YouTube requests spaced days apart

## Files Modified

- `execution/02_fetch_batch.py` - Rewrote for podcast RSS fetching
- `data/master_list.csv` - Updated with processing status

## Current Status

- **Cron job:** REMOVED (extraction complete)
- **Ready for use:** Yes - transcripts available in `transcripts/` directory