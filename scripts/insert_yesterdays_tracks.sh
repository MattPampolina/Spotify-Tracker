#!/bin/bash

# Get yesterday's date in multiple formats
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
YEAR=$(date -d "yesterday" +%Y)
MONTH=$(date -d "yesterday" +%m)
FILENAME="master_spotify_tracks_${YESTERDAY}.json"

# Paths
JSON_FILE=~/spotify/data/$YEAR/$MONTH/$FILENAME
DB_FILE=~/spotify/spotify_tracks.db
TABLE_NAME="tracks"
LOG_DIR=~/spotify/logs
LOG_FILE="$LOG_DIR/insertlog_$YESTERDAY.log"

mkdir -p "$LOG_DIR"

# Escape helper for SQL
sqlite3_escape() {
    echo "$1" | sed "s/'/''/g"
}

# Check file
if [ ! -f "$JSON_FILE" ]; then
    echo "[$(date)] No JSON file found for $YESTERDAY at $JSON_FILE" | tee -a "$LOG_FILE"
    exit 0
fi

echo "[$(date)] Starting insert from $JSON_FILE" | tee "$LOG_FILE"

# Create table if needed
sqlite3 "$DB_FILE" <<EOF
CREATE TABLE IF NOT EXISTS $TABLE_NAME (
    track_name TEXT,
    track_artist TEXT,
    album_name TEXT,
    track_number INTEGER,
    album_tracks INTEGER,
    played_at TEXT,
    duration_ms INTEGER,
    album_id TEXT,
    track_id TEXT,
    played_at_eastern TEXT PRIMARY KEY,
    date_plated TEXT
);
EOF

INSERTED=0
SKIPPED=0

# Use process substitution to avoid subshell
while read -r row; do
    track_name=$(echo "$row" | jq -r '.track_name')
    track_artist=$(echo "$row" | jq -r '.track_artist')
    album_name=$(echo "$row" | jq -r '.album_name')
    track_number=$(echo "$row" | jq -r '.track_number')
    album_tracks=$(echo "$row" | jq -r '.album_tracks')
    played_at=$(echo "$row" | jq -r '.played_at')
    duration_ms=$(echo "$row" | jq -r '.duration_ms')
    album_id=$(echo "$row" | jq -r '.album_id')
    track_id=$(echo "$row" | jq -r '.track_id')
    played_at_eastern=$(echo "$row" | jq -r '.played_at_eastern')
    date_plated=$(echo "$played_at_eastern" | cut -d'T' -f1)

    esc_track_name=$(sqlite3_escape "$track_name")
    esc_track_artist=$(sqlite3_escape "$track_artist")
    esc_album_name=$(sqlite3_escape "$album_name")

    SQL=$(cat <<EOF
INSERT OR IGNORE INTO $TABLE_NAME (
    track_name, track_artist, album_name, track_number, album_tracks,
    played_at, duration_ms, album_id, track_id,
    played_at_eastern, date_plated
) VALUES (
    '$esc_track_name',
    '$esc_track_artist',
    '$esc_album_name',
    $track_number,
    $album_tracks,
    '$played_at',
    $duration_ms,
    '$album_id',
    '$track_id',
    '$played_at_eastern',
    '$date_plated'
);
SELECT changes();
EOF
    )

    CHANGES=$(sqlite3 "$DB_FILE" <<EOF
BEGIN;
$SQL
COMMIT;
EOF
)

    if [ "$CHANGES" -eq 1 ]; then
        echo "[INSERTED] $track_name by $track_artist at $played_at_eastern" >> "$LOG_FILE"
        ((INSERTED++))
    else
        echo "[SKIPPED]  $track_name by $track_artist at $played_at_eastern (already exists)" >> "$LOG_FILE"
        ((SKIPPED++))
    fi
done < <(jq -c '.[]' "$JSON_FILE")

echo "[$(date)] Finished processing $JSON_FILE" >> "$LOG_FILE"
echo "[SUMMARY] Inserted: $INSERTED | Skipped: $SKIPPED" >> "$LOG_FILE"

