import spotipy
import json
import datetime
import os
import pytz
from datetime import datetime
from datetime import date
from spotipy.oauth2 import SpotifyOAuth

current_time = datetime.now().strftime('%Y-%m-%d')
masterFile = '/Users/matthew/Documents/VisualStudioCode/SpotifyAPI/dump/master_spotify_tracks_%s.json' % current_time
tempFile = '/Users/matthew/Documents/VisualStudioCode/SpotifyAPI/dump/temp_spotify_tracks_%s.json' % current_time
today = date.today()

#keep
def createMasterFile():
    if not os.path.exists(masterFile):
        with open(masterFile, "w") as f:
            data = []
            json.dump(data, f)
            print(f"Created new file: {masterFile}")
    else:
        print(f"File {masterFile} already exists.")
#keep
def tempDownload():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="c56b7a85beea41a28dfbe0f23676c1a8",
                                                client_secret="c3fc573709ea476d964717fff71330f2",
                                                redirect_uri="http://google.com/",
                                                scope="user-read-recently-played"))

    results = sp.current_user_recently_played(limit=50)

    # Convert JSON object to a string
    json_string = json.dumps(results)

    # Open file for writing
    with open(tempFile, 'a') as outFile:
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

#keep
def addToMaster():
    with open(masterFile, 'r') as inFile:
        masterSet = json.load(inFile)
    
    with open(tempFile, 'r') as inFile:
        new_tracks = json.load(inFile)    

    # Check if "played_at" exists in any item in the "master" list
    played_at_set = set([item['played_at'] for item in masterSet])
    for item in new_tracks:
        if item['played_at'] not in played_at_set:
            masterSet.append(item)
            played_at_set.add(item['played_at'])

    # Print the updated "master" list
    #print(json.dumps(masterSet, indent=4))

    # Write the updated "master" list to a file
    with open(masterFile, 'w') as outfile:
        json.dump(masterSet, outfile, indent=4)
    
    try:
        os.remove(tempFile)
        print("File deleted successfully.")
    except OSError as error:
        print(f"Error: {tempFile} - {error.strerror}.")

#keep
def convertEasternTime():
    
    with open(masterFile, 'r') as inFile:
        data = json.load(inFile)

    # Convert timestamp to Eastern Time and add "played_at_eastern" field to each entry
    for entry in data:
        # Convert timestamp to datetime object
        timestamp = datetime.fromisoformat(entry["played_at"][:-1])
        utc_timezone = pytz.timezone('UTC')
        timestamp = utc_timezone.localize(timestamp)

        # Convert to Eastern Time
        eastern_timezone = pytz.timezone('US/Eastern')
        eastern_time = timestamp.astimezone(eastern_timezone)

        # Add "played_at_eastern" field to entry
        entry["played_at_eastern"] = eastern_time.isoformat()

    with open(masterFile, 'w') as outfile:
        json.dump(data, outfile, indent=4)

#keep
def addDatePlayed():
    
    with open(masterFile, 'r') as inFile:
        tracks = json.load(inFile)

    for track in tracks:
        played_at_eastern = track["played_at_eastern"]
        date_str = played_at_eastern.split("T")[0]
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        track["played_at_date"] = date.isoformat()

    #print(tracks)

    with open(masterFile, 'w') as outFile:
        json.dump(tracks, outFile, indent=4)

def filterTracksByDate():
    with open(masterFile, 'r') as inFile:
        tracks = json.load(inFile)
    
    filtered_entries = [entry for entry in tracks if entry["played_at_date"] == str(today)]

    print(filtered_entries)

    with open(masterFile, 'w') as outFile:
        json.dump(filtered_entries, outFile, indent=4)
