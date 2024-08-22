import urllib.parse
import base64
import requests
import os
import json
from models import Song
from typing import List, Literal


def get_auth_link():
    auth_code_uri = os.getenv('SPOTIFY_AUTH_URI')
    redirect_uri = os.getenv('APP_URI')
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    
    if not (auth_code_uri and redirect_uri and client_id):
        raise Exception('Failed to get auth_code_uri, redirect_uri, and/or client_id from '
                        'environment vars')

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': f'{redirect_uri}/spotify-access-token',
        'scope': 'playlist-modify-private playlist-modify-public'
    }
    query_params = urllib.parse.urlencode(params)

    return f'{auth_code_uri}?{query_params}'


def get_access_token(auth_code: str, state: str | None):
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not (client_id and client_secret):
        raise Exception('Failed to get client_id and/or client_secret from environment vars')

    token_uri = os.getenv('SPOTIFY_TOKEN_URI')
    redirect_uri = os.getenv('APP_URI')

    # base64 encode client ID and secret as noted in authorization docs
    auth_str = f'{client_id}:{client_secret}'
    b64_encoded = base64.b64encode(auth_str.encode('ascii')).decode('ascii')

    headers = {
        'Authorization': f'Basic {b64_encoded}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': f'{redirect_uri}/spotify-access-token' 
    }

    response = requests.post(token_uri, headers=headers, data=body)
    content = json.loads(response.content.decode())

    if content.get('error'):
        raise Exception(f'Spotify authentication error: {content}')

    return content


def create_playlist(name: str, visibility: Literal['public', 'private'], access_token: str):
    uri = os.getenv('SPOTIFY_API_URI')
    
    # fetch user ID so we know who to make the playlist for
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{uri}/me', headers=headers)
    content = json.loads(response.content.decode())

    # create the playlist in the user's Spotify account
    user_id = content.get('id')
    headers['Content-Type'] = 'application/json'
    body = {
        'name': name,
        'public': visibility == 'public',
        'description': 'Playlist created by SoundScribe'
    }
    response = requests.post(f'{uri}/users/{user_id}/playlists', headers=headers, json=body)
    content = json.loads(response.content.decode())

    if content.get('error'):
        raise Exception(f'Error creating Spotify playlist: {content}')
    
    return content


def add_songs(playlist_id: str, songs: List[Song], access_token: str):
    pass