# proxy_service/models.py
from pydantic import BaseModel
from typing import Optional

class QueryResult(BaseModel):
    code:     str
    status:   int
    progress: Optional[int]
    detail:   Optional[dict]

class CharacterListItem(BaseModel):
    character_name: str

class CharacterDetail(CharacterListItem):
    filename:    str
    upload_time: str
    size:        int
    width:       int
    height:      int
    duration:    float
