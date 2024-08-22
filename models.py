from pydantic import BaseModel
from typing import List

class Song(BaseModel):
    name: str
    artist: str

class SongsResponse(BaseModel):
    songs: List[Song]