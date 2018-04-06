import datetime
import functions
import json

now = datetime.datetime.now()

with open('/Users/matthewpampolina/Documents/SpotifyAuto/datadump/dump/spotify_tracks_%s.json' % now.strftime('%Y-%m-%d'), 'r') as in_file:
        newdata=functions.deduplicate(in_file)

with open('/Users/matthewpampolina/Documents/SpotifyAuto/datadump/deduplicated/deduped_spotify_tracks_%s.json' % now.strftime('%Y-%m-%d'), 'w') as  out_file:
        json.dump(list(newdata), out_file)