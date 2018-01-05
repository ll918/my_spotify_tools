"""
Manage spotify playlists.

https://beta.developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
https://beta.developer.spotify.com/documentation/general/guides/scopes/
https://beta.developer.spotify.com/documentation/web-api/reference/search/search/
https://beta.developer.spotify.com/documentation/general/guides/working-with-playlists/
https://beta.developer.spotify.com/documentation/web-api/reference/playlists/replace-playlists-tracks/

https://beta.developer.spotify.com/documentation/web-api/#response-status-codes
"""
import json
import os
import urllib.parse
from base64 import b64encode
from pprint import pprint

import common

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
code = os.getenv('CODE')
rtoken = os.getenv('REFRESH_TOKEN')
redirect_uri = 'http://localhost/'
user_id = os.getenv('USER_ID')


def get_user_authorization_and_code():
    """
    Authorization Code Flow
    https://beta.developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
    User logs in and authorizes access
    For now callback info (authorisation code)manually retrieved from browser.
    """

    authorize_endpoint = 'https://accounts.spotify.com/authorize'
    scope = 'user-read-private%20playlist-modify-private'
    authorize_url = ''.join([authorize_endpoint,
                             '?client_id=', client_id,
                             '&response_type=code',
                             '&redirect_uri=', redirect_uri,
                             '&scope=', scope])
    # '&show_dialog=true'])
    print(authorize_url)


def get_original_tokens_with_code():
    # get access and refresh tokens with code

    endpoint = 'https://accounts.spotify.com/api/token'
    auth_header = b64encode(
        (client_id + ':' + client_secret).encode('ascii')).decode('ascii')
    headers = {'Authorization': 'Basic ' + auth_header}
    payload = {'grant_type': 'authorization_code', 'code': code,
               'redirect_uri': redirect_uri}

    r = common.post_request(endpoint, headers, payload)
    if r.status_code == 200:
        d = r.json()
        print(d)
    return


def refresh_token():
    # get fresh access token

    endpoint = 'https://accounts.spotify.com/api/token'
    auth_header = b64encode(
        (client_id + ':' + client_secret).encode('ascii')).decode('ascii')
    headers = {'Authorization': 'Basic ' + auth_header}
    payload = {'grant_type': 'refresh_token',
               'refresh_token': rtoken}
    r = common.post_request(endpoint, headers, payload)
    # if r.status_code == 200:
    d = r.json()
    return d['access_token']


def get_spotify_track_data(title, data, token):
    """
    Try to match tracks with their spotify id.

    json.dumps gets better match in cases where artist name or track name
    includes non alphanumeric characters.
    """

    if data:
        search_endpoint = 'https://api.spotify.com/v1/search?'
        tracks_data = {}
        not_found = []
        for i in data:
            artist = urllib.parse.quote_plus(i[0])
            track = urllib.parse.quote_plus(i[1])
            query = ''.join(
                ['q=', 'artist:"', json.dumps(artist), '"+', 'track:"',
                 json.dumps(track), '"&type=track&limit=1'])
            url = search_endpoint + query
            r = common.get_request(url, {'Authorization': 'Bearer ' + token})
            if r.status_code == 200:
                d = r.json()
                if d['tracks']['total'] > 0:
                    album_info = d['tracks']['items'][0]
                    album_name = album_info['album']['name']
                    album_id = album_info['album']['id']
                    album_url = album_info['album']['external_urls']['spotify']

                    artist_info = album_info['artists'][0]
                    artist_name = artist_info['name']
                    artist_id = artist_info['id']
                    artist_url = artist_info['external_urls']['spotify']

                    track_name = album_info['name']
                    track_id = album_info['id']
                    track_uri = album_info['uri']
                    track_url = album_info['external_urls']['spotify']

                    tracks_data[track_id] = {'track_name': track_name,
                                             'track_url': track_url,
                                             'track_uri': track_uri,
                                             'album': {'album_id': album_id,
                                                       'album_name': album_name,
                                                       'album_url': album_url},
                                             'artist': {'artist_id': artist_id,
                                                        'artist_name': artist_name,
                                                        'artist_url': artist_url}}
                else:
                    not_found.append(i)

            else:
                print('There was a problem with the request')
                print(r)

    if tracks_data:
        common.save_to_json(tracks_data, './json/' + title + '_data.json')
        print(len(tracks_data), 'tracks identified')
        print()
    if not_found:
        common.save_to_json(not_found, './json/' + title + '_not_found.json')
        print(len(not_found), 'unidentified tracks')
        pprint(not_found)
        print()
    return tracks_data


def create_playlist(title, token):
    """
    Creates a new empty playlist.

    https://beta.developer.spotify.com/documentation/web-api/reference/playlists/create-playlist/
    POST https://api.spotify.com/v1/users/{user_id}/playlists
    playlist-modify-private
    """

    endpoint = ''.join(['https://api.spotify.com/v1/users/', user_id,
                        '/playlists'])
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json'}
    payload = json.dumps({'name': title, 'public': 'false'})

    r = common.post_request(endpoint, headers, payload)
    playlist_id = ''
    if r.status_code == 201:
        d = r.json()
        playlist_id = d['id']
        print('Playlist', title, 'created')
    else:
        print(r)
        print(r.status_code)

    return playlist_id


def add_track_playlist(playlist_id, d, token):
    """
    Add tracks to a spotify playlist
    """

    endpoint = ''.join(['https://api.spotify.com/v1/users/', user_id,
                        '/playlists/', playlist_id, '/tracks'])
    headers = {'Authorization': 'Bearer ' + token,
               'Content-Type': 'application/json'}
    tracks_uri = []
    for k, v in d.items():
        tracks_uri.append(v['track_uri'])
    payload = json.dumps({"uris": tracks_uri})
    r = common.post_request(endpoint, headers, payload)
    if r.status_code == 201:
        print('tracks added to playlist')
    else:
        print('There was a problem with the request')
        print(r)
    return

# get_user_authorization_and_code()
# get_original_tokens_with_code()
# refresh_token()
