from pydantic import BaseModel
from typing import List
from datetime import date

class Song(BaseModel):
    name: str
    artists: List[str]
    release_date: date
    spotify_uri: str | None

class SongsResponse(BaseModel):
    songs: List[Song]