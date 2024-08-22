from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query
from typing import List, Literal
from models import Song, SongsResponse
import llm
import spotify


app = FastAPI(title='SoundScribe API')


@app.get('/',
         include_in_schema=False)
def root():
    return {'message': 'Hit root endpoint'}


@app.get('/song-recommendations',
         summary='Get playlist of song recommendations',
         description='Returns list of `size` songs in JSON format based on give `text_input`',
         response_model=SongsResponse)
def get_song_recommendations(text_input: str, size: int = Query(gt=0, le=300)):
    """Returns list of `size` songs in JSON format based on given `text_input`"""
    song_recommendations = llm.get_song_recommendations(text_input, size)
    return SongsResponse(songs=song_recommendations)


@app.get('/spotify-auth-link',
         summary='Get Spotify login link',
         description='Returns login link to initiate authorization for specific Spotify user account')
def get_auth_code():
    """Returns login link to initiate authorization for specific Spotify user account"""
    login_link = spotify.get_auth_link()
    return {'link': login_link}


@app.get('/spotify-access-token',
         summary='Get Spotify access token',
         description='Returns Spotify access token (automatically triggered by user login)')
def get_spotify_access_token(code: str | None = None, error: str | None = None, 
                             state: str | None = None):
    """Returns Spotify access token (automatically triggered by user login)"""
    if error:
        return {'error': error}
    access_token_response = spotify.get_access_token(auth_code=code, state=state)
    return access_token_response


@app.post('/spotify-playlist',
          summary='Generate Spotify playlist',
          description='Generate and get link to Spotify playlist of `songs`')
def create_spotify_playlist(name: str, visibility: Literal['public', 'private'], access_token: str, 
                            songs: List[Song]):
    """Generate Spotify playlist of `songs`"""
    if not access_token:
        raise Exception('Access token is None')
    
    playlist_data = spotify.create_playlist(name=name, visibility=visibility, 
                                            access_token=access_token)
    songs_added_successfully = spotify.add_songs(playlist_id=playlist_data['id'], songs=songs, 
                                                 access_token=access_token)
    
    if songs_added_successfully:
        return {'message': 'success', 'playlist': playlist_data}
    
    return {'message': 'failure'}