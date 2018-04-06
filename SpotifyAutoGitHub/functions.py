import requests
import datetime
import json
import collections
import os

now = datetime.datetime.now()

# Get access token
def access_token():
    client_id = 'c56b7a85beea41a28dfbe0f23676c1a8'
    client_secret = '35f67d7219d74a63a17adfd54ce9e4ff'

    body_params = {'grant_type' : 'refresh_token',
                'refresh_token' : 'AQCEYXvDNTQWsrvYOAlBlYmELTfrTWO4SzcIdiW7Xl3viw-iu1s3-D04QcXSI0UQkQEnn8Ck7tCAVBvNdxahuchAbHf3epMt00RA58kuPbg5nqVtCjMG9ZK5wPsw4jsH9eM'}
                

    url = 'https://accounts.spotify.com/api/token'
    response = requests.post(url, 
                             data = body_params, 
                             auth = (client_id, client_secret))
    
    response_dict = json.loads(response.content)
    accessToken = response_dict.get('access_token')

    #print(accessToken)

    return accessToken
    
# Get most recent songs and append the response
# to a new json file every day
def download_data():
    now = datetime.datetime.now()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d-%U')
    

    path = '/Users/matthewpampolina/Documents/SpotifyAuto/datadump/raw/week_%s' % now.strftime('%U')
    if not os.path.exists(path):
        os.mkdir(path)


    filename = '/Users/matthewpampolina/Documents/SpotifyAuto/datadump/raw/week_%s/spotify_tracks_%s.json' % (now.strftime('%U'), current_time)
    
    accesToken = access_token()
    headers = {'Authorization': 'Bearer ' + accesToken }
    payload = {'limit': 50}

    url = 'https://api.spotify.com/v1/me/player/recently-played'
    response = requests.get(url, headers = headers,
                            params = payload)
    data = response.json()

    with open(filename, 'a') as f:
        json.dump(data['items'], f)
        f.write('\n')
        

# This function takes a list of track uri's 
# to replace songs in my morning playlist
# and returns the status code of the put request.
def replace_tracks(tracks):
    
    url = 'https://api.spotify.com/v1/users/1170891844/playlists/6a2QBfOgCqFQLN08FUxpj3/tracks'
    accesToken = access_token()
    headers = {'Authorization': 'Bearer ' + accesToken,
               'Content-Type':'application/json'}
    data = {"uris": ','.join(tracks)}

    response = requests.put(url, headers = headers,
                            params = data)
                            
    return response.status_code
        
# Cleaner function to get rid of redundancy
def deduplicate(file):
    result =[]
    
    for line in file:
        data = json.loads(line)
        result.extend(data)
    
    result = {i['played_at']:i for i in result}.values()
    return result

#Parse json so it can easily be converted to a dataframe
def parse_json(file): 
    results = []
    track_cols = ['name','uri','explicit','duration_ms','type','id']

    for item in file:
        
        d_time = {'played_at' : item['played_at']}
        
        for key in item.keys(): 
            if (key == 'track'):
                track = item[key]
                d_arts = collections.defaultdict(list)
                
                for i in track['artists']: 
                    for k, v in i.items(): 
                        if (k in ['id','name']):
                            d_arts['artist_' + k].append(v)
                            
                track_sub = { k: track[k] for k in track_cols }
                
                for k,v in track_sub.items():
                    if (k in ['id','name']):
                        track_sub['track_' + k] = track_sub.pop(k)
            
        d = dict(track_sub, **d_arts)
        d.update(d_time)

        results.append(d)
                     
    return results

#parse depulicated data 
def parser():
    results = []
    with open('/Users/matthewpampolina/Documents/SpotifyAuto/datadump/deduplicated/deduped_spotify_tracks_%s.json' % now.strftime('%Y-%m-%d-%U'), 'r') as in_file:
        data = json.load(in_file)
        parsed = parse_json(data)
        results.extend(parsed)
    with open('/Users/matthewpampolina/Documents/SpotifyAuto/datadump/parsed/parsed_spotify_tracks_%s.json' % now.strftime('%Y-%m-%d-%U'), 'w') as out_file:
        json.dump(results, out_file)


def duperday():
    with open('/Users/matthewpampolina/Documents/SpotifyAuto/datadump/dump/spotify_tracks_%s.json' % now.strftime('%Y-%m-%d'), 'r') as in_file:
        newdata=deduplicate(in_file)

    with open('/Users/matthewpampolina/Documents/SpotifyAuto/datadump/deduplicated/deduped_spotify_tracks_%s.json' % now.strftime('%Y-%m-%d'), 'w') as  out_file:
        json.dump(list(newdata), out_file)

    