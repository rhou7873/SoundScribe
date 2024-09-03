import urllib.parse
import base64
import requests
import os
import json
from models import Song
from typing import List, Literal


class SpotifyEngine():

    def __init__(self):
        self.__AUTH_CODE_URI = os.getenv('SPOTIFY_AUTH_URI')
        self.__APP_URI = os.getenv('APP_URI')
        self.__TOKEN_URI = os.getenv('SPOTIFY_TOKEN_URI')
        self.__API_URI = os.getenv('SPOTIFY_API_URI')
        self.__CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
        self.__CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

        if not (self.__AUTH_CODE_URI, self.__APP_URI, self.__TOKEN_URI, 
                self.__API_URI, self.__CLIENT_ID, self.__CLIENT_SECRET):
            raise Exception('Error getting environment variables for Spotify engine')

    def get_auth_link(self):
        params = {
            'client_id': self.__CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': f'{self.__APP_URI}/spotify-access-token',
            'scope': 'playlist-modify-private playlist-modify-public'
        }
        query_params = urllib.parse.urlencode(params)

        return f'{self.__AUTH_CODE_URI}?{query_params}'

    def get_access_token(self, auth_code: str, state: str | None):
        # base64 encode client ID and secret as noted in authorization docs
        auth_str = f'{self.__CLIENT_ID}:{self.__CLIENT_SECRET}'
        b64_encoded = base64.b64encode(auth_str.encode('ascii')).decode('ascii')

        headers = {
            'Authorization': f'Basic {b64_encoded}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': f'{self.__APP_URI}/spotify-access-token' 
        }

        response = requests.post(self.__TOKEN_URI, headers=headers, data=body)
        content = json.loads(response.content.decode())

        if content.get('error'):
            raise Exception(f'Spotify authentication error: {content}')

        return content

    def create_playlist(self, name: str, visibility: Literal['public', 'private'], access_token: str):
        # fetch user ID so we know who to make the playlist for
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(f'{self.__API_URI}/me', headers=headers)
        content = json.loads(response.content.decode())

        # create the playlist in the user's Spotify account
        user_id = content.get('id')
        headers['Content-Type'] = 'application/json'
        body = {
            'name': name,
            'public': visibility == 'public',
            'description': 'Playlist created by SoundScribe'
        }
        response = requests.post(f'{self.__API_URI}/users/{user_id}/playlists', headers=headers, json=body)
        content = json.loads(response.content.decode())

        if content.get('error'):
            raise Exception(f'Error creating Spotify playlist: {content}')
        
        return content

    def add_songs(self, playlist_id: str, songs: List[Song], access_token: str):
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        song_uris = []

        for song in songs:
            if song.spotify_uri is None:
                raise Exception(f'Song "{song.name}" has spotify_uri that\'s None')
            song_uris.append(song.spotify_uri)

        song_uris_str = ','.join(song_uris)
        params = {
            'uris': song_uris_str
        }
        response = requests.post(f'{self.__API_URI}/playlists/{playlist_id}/tracks', headers=headers, params=params)
        content = json.loads(response.content.decode())

        if content.get('error'):
            raise Exception(f'Error trying to add tracks: {content}')
        
        return song_uris

    def __search_song(self):
        pass

    