#!/bin/bash

TO="matt.pampolina@gmail.com"
DATE=$(date +%Y-%m-%d)
SUBJECT="Listening History for $DATE"
BODY="Please find attached your listening history data for $DATE."
ATTACHMENT="$HOME/spotify/listening_data.txt"

echo "$BODY" | mutt -s "$SUBJECT" -a "$ATTACHMENT" -- "$TO"

