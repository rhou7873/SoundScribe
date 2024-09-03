from openai import OpenAI
import os
import json
from models import Song
from datetime import datetime


class LLMEngine():
    
    def __init__(self):
        self.__CLIENT = OpenAI()
        self.__MODEL = os.getenv('OPENAI_MODEL')

    def get_song_recommendations(self, text_input: str, size: int):
        INPUT = (f'generate me a playlist of {size} songs that captures the feeling of this sentence: {text_input}. '
                'provide me the name (denoted with field "name"), artist (denoted with field "artists"), and release '
                r'date in %Y-%m-%d format (denoted with field "release_date") of those songs in json format and say nothing else. '
                'comma-separate when a song has multiple artists')
        llm_response = self.__get_llm_response(INPUT)
        llm_response = llm_response[7:-3]  # strip off JSON markdown
        songs_json = json.loads(llm_response)
        songs = []

        for song in songs_json:
            name = song['name']
            artist_str = str(song['artists'])
            release_date = datetime.strptime(song['release_date'], r'%Y-%m-%d')
            artists = [str.strip(artist) for artist in artist_str.split(',')]
            songs.append(Song(name=name, artists=artists, release_date=release_date, spotify_uri=None))

        return songs

    def __get_llm_response(self, input: str):
        completion = self.__CLIENT.chat.completions.create(
            model=self.__MODEL,
            messages=[
                {'role': 'user', 'content': input}
            ]
        )
        return completion.choices[0].message.content

