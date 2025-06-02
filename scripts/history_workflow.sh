#!/bin/bash
#Wrapper script that does the following
#Adds tracks to ~/spotify/spotify_tracks.db
#Creates a temp file in ~/spotify that gets listening data
#Sends an email out with that file

echo "Inserting Tracks into ~/spotify/spotify_tracks.db"
#Add Tracks to spotify_tracks.db
~/spotify/scripts/insert_yesterdays_tracks.sh ~/spotify/spotify_tracks.db 

echo "Creating Temp Listening File"
#Create temp listening file
~/spotify/scripts/get_listening_data.sh ~/spotify/spotify_tracks.db  > ~/spotify/listening_data.txt

#echo "Sending Email out"
~/spotify/scripts/send_email.sh
