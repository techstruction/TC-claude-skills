#!/usr/bin/env bash
# 05_scheduled_run.sh — Scheduled batch runner with concurrency guard + OneDrive sync
# Called by cron every 5 minutes.
# Workflow: [daily playlist refresh if stale] → [batch fetch] → [OneDrive rsync]
set -euo pipefail

SKILL_DIR="/home/ubuntu/.claude/skills/market-monday-transcripts"
VENV_PYTHON="${SKILL_DIR}/.venv/bin/python"
CSV_PATH="${SKILL_DIR}/data/master_list.csv"
REMOTE_BASE="onedrive:Backups/oracle-server/market-monday-transcripts"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

cd "${SKILL_DIR}"
mkdir -p .tmp

# Rotate log if over 1MB
LOG_FILE="${SKILL_DIR}/.tmp/scheduled_run.log"
if [ -f "${LOG_FILE}" ] && [ "$(stat -c%s "${LOG_FILE}")" -gt 1048576 ]; then
    mv "${LOG_FILE}" "${LOG_FILE}.1"
fi

# --- Concurrency guard: max 1 instance at a time (flock, race-free) ---
LOCKFILE="${SKILL_DIR}/.tmp/scheduled_run.lock"
exec 9>"${LOCKFILE}"
if ! flock -n 9; then
    log "Another instance is already running. Exiting."
    exit 0
fi
trap 'rm -f "${LOCKFILE}"' EXIT

# --- Daily masterlist refresh ---
# Refresh if master_list.csv doesn't exist or is older than 23 hours (82800 seconds)
REFRESH_NEEDED=false
if [ ! -f "${CSV_PATH}" ]; then
    REFRESH_NEEDED=true
    log "master_list.csv missing — rebuilding playlist"
else
    NOW=$(date +%s)
    FILE_MTIME=$(date -r "${CSV_PATH}" +%s)
    AGE=$(( NOW - FILE_MTIME ))
    if [ "${AGE}" -gt 82800 ]; then
        REFRESH_NEEDED=true
        log "master_list.csv is stale (${AGE}s old) — refreshing playlist"
    fi
fi

if [ "${REFRESH_NEEDED}" = "true" ]; then
    if ! "${VENV_PYTHON}" execution/01_fetch_playlist.py >> .tmp/playlist_refresh.log 2>&1; then
        log "ERROR: Playlist refresh failed — see .tmp/playlist_refresh.log. Skipping batch."
        exit 1
    fi
    log "Playlist refresh complete"
fi

# --- Check for pending episodes ---
# Use Python's csv module (RFC 4180-aware) to count pending rows; awk with -F',' breaks on
# quoted fields that contain commas (e.g. episode titles like "STOCKS AT ALL-TIME HIGHS… 1,400%…")
PENDING=$("${VENV_PYTHON}" -c "
import csv, sys
with open(sys.argv[1]) as f:
    print(sum(1 for r in csv.DictReader(f) if r.get('status')=='pending'))
" "${CSV_PATH}")
if [ "${PENDING}" -eq 0 ]; then
    log "No pending episodes. Nothing to do."
    exit 0
fi

log "Found ${PENDING} pending episode(s). Starting batch..."

# --- Run batch ---
"${VENV_PYTHON}" execution/02_fetch_batch.py --count 5

# --- rsync transcripts to OneDrive ---
log "Syncing transcripts to OneDrive..."
rclone sync \
    "${SKILL_DIR}/transcripts/" \
    "${REMOTE_BASE}/transcripts/" \
    --stats-one-line \
    >> .tmp/rsync.log 2>&1
log "Transcript sync complete"

log "Syncing master_list.csv to OneDrive..."
rclone copyto \
    "${CSV_PATH}" \
    "${REMOTE_BASE}/data/master_list.csv" \
    >> .tmp/rsync.log 2>&1
log "master_list.csv sync complete"

log "Scheduled run finished."
