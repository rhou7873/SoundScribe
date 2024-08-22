from openai import OpenAI
import os
import json
from models import Song


client = OpenAI()


def get_song_recommendations(text_input: str, size: int):
    INPUT = (f'generate me a playlist of {size} songs that captures the feeling of this sentence: {text_input}. '
             'provide me the name (denoted with field "name") and artist (denoted with field "artist") '
             'of those songs in json format and say nothing else')
    llm_response = get_llm_response(INPUT)
    llm_response = llm_response[7:-3]  # strip off JSON markdown
    songs_json = json.loads(llm_response)
    songs = [Song(name=song['name'], artist=song['artist']) for song in songs_json]
    return songs


def get_llm_response(input: str):
    completion = client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL'),
        messages=[
            {'role': 'user', 'content': input}
        ]
    )
    return completion.choices[0].message.content

