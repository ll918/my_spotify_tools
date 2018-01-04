#!/usr/bin/env python3
"""
Creates a spotify playlist then add tracks to it.

Extract_data returns a playlist name and a list of track name with the artist
name. Ex.: [(artist, track),...]
When found in spotify catalog(?), tracks are matched with their uri.
A playlist is then created and tracks with uri are added to it.
"""

import my_spotify
import extract_data

title, tracks_lst = extract_data.get_tracks_lst()

access_token = my_spotify.refresh_token()

data = my_spotify.get_spotify_track_data(title, tracks_lst, access_token)
playlist_id = my_spotify.create_playlist(title, access_token)
my_spotify.add_track_playlist(playlist_id, data, access_token)
