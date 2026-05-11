#!/usr/bin/env bash
# 05_scheduled_run.sh — Scheduled batch runner with concurrency guard + OneDrive sync
# Called by cron every 5 minutes.
# Workflow: [daily playlist refresh if stale] → [batch fetch] → [OneDrive rsync]
set -euo pipefail

SKILL_DIR="/home/ubuntu/.claude/skills/market-monday-transcripts"
VENV_PYTHON="${SKILL_DIR}/.venv/bin/python"
CSV_PATH="${SKILL_DIR}/data/master_list.csv"
REMOTE_BASE="onedrive:Backups/oracle-server/market-monday-transcripts"
LOCKFILE="${SKILL_DIR}/.tmp/scheduled_run.lock"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

cd "${SKILL_DIR}"
mkdir -p .tmp

# --- Concurrency guard via lockfile ---
# If lock exists and the PID inside it is still running, exit.
# Otherwise, claim the lock with our PID.
if [ -f "${LOCKFILE}" ]; then
    LOCK_PID=$(cat "${LOCKFILE}" 2>/dev/null || echo "")
    if [ -n "${LOCK_PID}" ] && kill -0 "${LOCK_PID}" 2>/dev/null; then
        log "Another instance (PID ${LOCK_PID}) is already running. Exiting."
        exit 0
    else
        log "Stale lockfile found (PID ${LOCK_PID} gone). Removing and continuing."
        rm -f "${LOCKFILE}"
    fi
fi
echo $$ > "${LOCKFILE}"
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
    "${VENV_PYTHON}" execution/01_fetch_playlist.py >> .tmp/playlist_refresh.log 2>&1
    log "Playlist refresh complete"
fi

# --- Check for pending episodes ---
# Use awk to check the 6th CSV field (status column) rather than grep to avoid false matches
PENDING=$(awk -F',' 'NR>1 && $6=="pending"' "${CSV_PATH}" | wc -l)
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
