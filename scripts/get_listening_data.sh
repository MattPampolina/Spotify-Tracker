#!/usr/bin/env bash
#
# stats.sh — Spotify listening stats from sqlite DB (calendar‐based May 2025 & 2025,
# plus most‐played artists with total seconds)
# Usage: ./stats.sh /path/to/spotify_tracks.db

DB="$1"
YEAR=2025
MONTH=05

# Name of the column holding track length in seconds.
# If yours is in ms, set e.g. DURATION_COL="ms_played/1000"
#DURATION_COL="duration_seconds"
DURATION_COL="duration_ms/1000"

if [[ -z "$DB" ]]; then
  echo "Usage: $0 /path/to/spotify_tracks.db"
  exit 1
fi

# Helper to run a query and pretty-print it
run_q() {
  local sql="$1"
  sqlite3 -header -column "$DB" "$sql" \
    | sed -E ':start; s/([0-9])([0-9]{3})([^0-9]|$)/\1,\2\3/; t start'
}

# Precompute calendar boundaries via SQLite
MONTH_START="${YEAR}-${MONTH}-01"
MONTH_END=$(sqlite3 "$DB" "SELECT date('${MONTH_START}','+1 month','-1 day');")
YEAR_START="${YEAR}-01-01"
YEAR_END=$(sqlite3 "$DB" "SELECT date('${YEAR_START}','+1 year','-1 day');")

echo
echo "▶ Songs listened *yesterday* ($(date -d 'yesterday' +%Y-%m-%d)):"
run_q "SELECT COUNT(*) AS plays,         
	SUM(duration_ms)/1000.0 AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
 
       FROM tracks
       WHERE date_plated = date('now','localtime','-1 day');"

echo
echo "▶ Songs listened in the *last 7 days* ($(date -d '7 days ago' +%Y-%m-%d) → $(date +%Y-%m-%d)):"
run_q "SELECT COUNT(*) AS plays,
	SUM(duration_ms)/1000.0 AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
       FROM tracks
       WHERE date_plated BETWEEN date('now','localtime','-7 days') AND date('now','localtime','-1 day');"

echo
echo "▶ Songs listened in *May 2025* (${MONTH_START} → ${MONTH_END}):"
run_q "SELECT COUNT(*) AS plays,
	SUM(duration_ms)/1000.0 AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
       FROM tracks
       WHERE date_plated BETWEEN date('${MONTH_START}')
                             AND date('${MONTH_START}','+1 month','-1 day');"

echo
echo "▶ Songs listened in *2025* (${YEAR_START} → ${YEAR_END}):"
run_q "SELECT COUNT(*) AS plays,
	SUM(duration_ms)/1000.0 AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
       FROM tracks
       WHERE date_plated BETWEEN date('${YEAR_START}')
                             AND date('${YEAR_START}','+1 year','-1 day');"

echo
echo "▶ Top 10 tracks in *May 2025*:"
run_q "SELECT track_name || ' — ' || track_artist AS track,
              COUNT(*)               AS plays
       FROM tracks
       WHERE date_plated BETWEEN date('${MONTH_START}')
                             AND date('${MONTH_START}','+1 month','-1 day')
       GROUP BY track_name, track_artist
       ORDER BY plays DESC
       LIMIT 10;"

echo
echo "▶ Top 10 tracks in *2025*:"
run_q "SELECT track_name || ' — ' || track_artist AS track,
              COUNT(*)               AS plays
       FROM tracks
       WHERE date_plated BETWEEN date('${YEAR_START}')
                             AND date('${YEAR_START}','+1 year','-1 day')
       GROUP BY track_name, track_artist
       ORDER BY plays DESC
       LIMIT 10;"

#
# ——— Most‐played artist with total seconds ———
#
echo
echo "▶ Most played artist in the *last 7 days* ($(date -d '7 days ago' +%Y-%m-%d) → $(date +%Y-%m-%d)):"
run_q "SELECT track_artist          AS artist,
              COUNT(*)               AS plays,
              SUM(${DURATION_COL})   AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
       FROM tracks
       WHERE date_plated BETWEEN date('now','localtime','-7 days')
                             AND date('now','localtime')
       GROUP BY track_artist
       ORDER BY plays DESC
       LIMIT 1;"

echo
echo "▶ Most played artist in *May 2025* (${MONTH_START} → ${MONTH_END}):"
run_q "SELECT track_artist          AS artist,
              COUNT(*)               AS plays,
              SUM(${DURATION_COL})   AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
       FROM tracks
       WHERE date_plated BETWEEN date('${MONTH_START}')
                             AND date('${MONTH_START}','+1 month','-1 day')
       GROUP BY track_artist
       ORDER BY plays DESC
       LIMIT 1;"

echo
echo "▶ Most played artist in *2025* (${YEAR_START} → ${YEAR_END}):"
run_q "SELECT track_artist          AS artist,
              COUNT(*)               AS plays,
              SUM(${DURATION_COL})   AS total_seconds,
          printf(
            '%02d:%02d:%02d',
            (SUM(duration_ms)/1000)   / 3600,
            ((SUM(duration_ms)/1000) % 3600) / 60,
            (SUM(duration_ms)/1000)   % 60
          )                                    AS total_time_hms
       FROM tracks
       WHERE date_plated BETWEEN date('${YEAR_START}')
                             AND date('${YEAR_START}','+1 year','-1 day')
       GROUP BY track_artist
       ORDER BY plays DESC
       LIMIT 1;"

echo
