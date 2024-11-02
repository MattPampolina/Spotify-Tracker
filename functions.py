import spotipy
import json
import datetime
import os
import pytz
from datetime import datetime
from datetime import date
from spotipy.oauth2 import SpotifyOAuth

# Set timezone to Eastern Time using 'America/New_York'
eastern = pytz.timezone('America/New_York')
current_time = datetime.now(eastern).strftime('%Y-%m-%d')


# Define the folder and filenames
folder = 'data'
masterFile = 'master_spotify_tracks_%s.json' % current_time
masterFilePath = os.path.join(folder, masterFile)
tempFile = 'temp_spotify_tracks_%s.json' % current_time
tempFilePath = os.path.join(folder, tempFile)

#Creates temp file to download data to
def createTempFile():
    print(f"Checking if {tempFile} exists in '{folder}' folder.")
    # Check if the folder exists, create it if not
    if not os.path.isdir(folder):
        os.makedirs(folder)
        print(f"Folder '{folder}' created.")

    # Check if the file exists in the folder
    if not os.path.isfile(tempFilePath):
        data = []
        with open(tempFilePath, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"{tempFile} created successfully in '{folder}' folder.")
    else:
        print(f"The file {tempFile} already exists in '{folder}' folder.")

#Adds Spotify Tracks to Temp File
def tempDownload():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="c56b7a85beea41a28dfbe0f23676c1a8",
                                                client_secret="c3fc573709ea476d964717fff71330f2",
                                                redirect_uri="http://localhost:8888/callback",
                                                scope="user-read-recently-played",
                                                open_browser=False))

    results = sp.current_user_recently_played(limit=50)

    # Open file for writing
    with open(tempFilePath, 'w') as outFile:
        # Write JSON string to file
        new_items = []
        for item in results['items']:
            new_item = {
                'track_name': item['track']['name'],
                'track_artist': item['track']['artists'][0]['name'],
                'album_name': item['track']['album']['name'],
                'track_number': item['track']['track_number'],
                'album_tracks': item['track']['album']['total_tracks'],
                'played_at': item['played_at'],
                'duration_ms': item['track']['duration_ms'],
                'album_id': item['track']['album']['id'],
                'track_id': item['track']['id'],

                }
            new_items.append(new_item)
        json.dump(new_items, outFile, indent=2)

#Adds tracks to master file if it doesn't exist there already
def addToMaster():
    print(f"Adding Tracks to {masterFile}")
    # Load new tracks from temp.json
    with open(tempFilePath, "r") as temp_file:
        new_tracks = json.load(temp_file)

    # Load existing data if master_spotify_tracks_.json exists
    if os.path.exists(masterFilePath):
        with open(masterFilePath, "r") as master_file:
            master_data = json.load(master_file)
    else:
        master_data = []

    # Extract existing played_at timestamps for comparison
    existing_played_at = {track["played_at"] for track in master_data}

    # Add new tracks only if the played_at timestamp is not in master_data
    for track in new_tracks:
        #Extract date part of played_at_eastern
        played_at_eastern_date = track["played_at_eastern"][:10] 
        
        #Check if the track was played today in Eastern Time and is not already in master_data
        if played_at_eastern_date == current_time and track["played_at"] not in existing_played_at:
            master_data.append(track)

    # Write the updated data back to master_json.json
    with open(masterFilePath, "w") as master_file:
        json.dump(master_data, master_file, indent=4)

    print(f"New tracks added to {masterFile} (if not already present).")

    try:
        os.remove(tempFilePath)
        print(f"{tempFile} deleted successfully.")
    except OSError as error:
        print(f"Error: {tempFile} - {error.strerror}.")

# Function to convert UTC to Eastern Time
def convert_to_eastern(utc_time_str):
    # Define UTC and Eastern time zones
    utc_zone = pytz.utc
    eastern_zone = pytz.timezone("America/New_York")
    
    # Parse the UTC time string
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc_time = utc_zone.localize(utc_time)
    
    # Convert to Eastern Time
    eastern_time = utc_time.astimezone(eastern_zone)
    return eastern_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

#Adds Eastern  Time To Master File
def convertEasternTime():   
    print(f"Adding Eastern times to {masterFile}")
    with open(masterFilePath, 'r') as inFile:
        data = json.load(inFile)

    # Process the data and add 'played_at_eastern' field
    for track in data:
        track["played_at_eastern"] = convert_to_eastern(track["played_at"])

    with open(masterFilePath, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    
    print(f"Added Eastern times to {masterFile}")

#Adds Eastern  Time To Master File
def convertEasternTimeTemp():   
    print(f"Adding Eastern times to {tempFile}")
    with open(tempFilePath, 'r') as inFile:
        data = json.load(inFile)

    # Process the data and add 'played_at_eastern' field
    for track in data:
        track["played_at_eastern"] = convert_to_eastern(track["played_at"])

    with open(tempFilePath, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    
    print(f"Added Eastern times to {tempFilePath}")


#keep
def addDatePlayed():
    
    with open(masterFilePath, 'r') as inFile:
        tracks = json.load(inFile)

    for track in tracks:
        played_at_eastern = track["played_at_eastern"]
        date_str = played_at_eastern.split("T")[0]
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        track["played_at_date"] = date.isoformat()

    with open(masterFilePath, 'w') as outFile:
        json.dump(tracks, outFile, indent=4)
