import pytz
import spotipy
import json
import os
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth

# Time Variables
eastern = pytz.timezone('America/New_York')
current_time = datetime.now(eastern).strftime('%Y-%m-%d')
year = datetime.now(eastern).strftime("%Y")
month = datetime.now(eastern).strftime("%m")

# Define the folder and filenames
base_directory = '~/spotify/data'
year_folder = os.path.join(base_directory, year)
month_folder = os.path.join(year_folder, month)

masterFile = 'master_spotify_tracks_%s.json' % current_time
masterFilePath = os.path.join(month_folder, masterFile)
tempFile = 'temp_spotify_tracks_%s.json' % current_time
tempFilePath = os.path.join(base_directory, tempFile)

def runWorkFlow():
    print("*****Script Started At:", get_eastern_time(), "*****")
    create_year_month_subfolder()
    results = spoitfyDownload()
    results = trimData(results)
    results = addEasternTimeStamp(results)
    #writeJsonToFile(tempFilePath, results)
    addToMasterFile(results)

    print("*****Script Ended At:", get_eastern_time(), "*****")

# Helper Function to convert UTC to Eastern Time
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

# Helper Function Writes json to a file
def writeJsonToFile(filePath, json_data):
    with open(filePath, 'w') as jsonFile:
        json.dump(json_data, jsonFile, indent = 4)
    print(f"Wrote data to {filePath}")

# Helper Function that extracts json from a file
def loadJsonFromFile(filePath):
    file = filePath

    # Loads data into json file if exists else initalizes it
    if os.path.exists(file):
        with open(file, "r") as inFile:
            data = json.load(inFile)
    else:
        data = []
    
    #print(f"JSON taken from {file}")
    return data

# Helper Function Sorts Tracks based on a key
def sortTracks(json_data, flag):
    sorted_tracks = sorted(
        json_data,
        key=lambda x: datetime.fromisoformat(x[flag]),
        reverse=True
    )
    print(f"Sorted tracks by {flag}")
    return sorted_tracks

# Returns Current Eastern Time in 24 hour format
def get_eastern_time():
    # Get current time in Eastern Time
    eastern_time = datetime.now(eastern)
    
    # Format time in 24-hour format
    formatted_time = eastern_time.strftime("%H:%M:%S")
    return formatted_time

# Creates Subfolder Structure
def create_year_month_subfolder():
    #print("Checking if folders exist")

    # Create year folder if it doesn't exist
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)
        print(f"Created year folder: {year_folder}")
    else:
        print(f"Folder {year_folder} exists")
    
    # Create month folder if it doesn't exist
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)
        print(f"Created month folder: {month_folder}")
    else:
        print(f"Folder {month_folder} exists")

# API Call to Download User Data
def spoitfyDownload():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="c56b7a85beea41a28dfbe0f23676c1a8",
                                                client_secret="c3fc573709ea476d964717fff71330f2",
                                                redirect_uri="http://localhost:8888/callback",
                                                scope="user-read-recently-played",
                                                open_browser=False))
    
    results = sp.current_user_recently_played(limit=50)
    print("API call successful- downloaded user tracks")
    return results

# Trim API Results
def trimData(json_data):
    results = json_data
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
    
    #print(new_items)
    print("Trimmed API results")
    return new_items

# Add East Time to JSON
def addEasternTimeStamp(json_data):
    data = json_data

    for track in data:
        track["played_at_eastern"] = convert_to_eastern(track["played_at"])
    
    #print(data)
    print("Added eastern time played at flag")
    return data

# Adds Results to Master File if it is not a dup and is the curr day
def addToMasterFile(json_data):
    new_tracks = json_data
    add_count = 0
    

    master_data = loadJsonFromFile(masterFilePath)
    # Extract existing played_at timestamps for comparison
    existing_played_at = {track["played_at"] for track in master_data}
    
    # Add new tracks only if the played_at timestamp is not in master_data
    for track in new_tracks:
        #Extract date part of played_at_eastern
        played_at_eastern_date = track["played_at_eastern"][:10] 

        #Check if the track was played today in Eastern Time and is not already in master_data
        if played_at_eastern_date == current_time and track["played_at"] not in existing_played_at:
            add_count += 1
            master_data.append(track)
    
    master_data = sortTracks(master_data, 'played_at_eastern')

    # Write the updated data back to master_json.json
    writeJsonToFile(masterFilePath, master_data)

    total_count = len(master_data)
    print(f"{add_count} track(s) were added in this run")
    print(f"There are {total_count} track(s) in {masterFile}")


    
