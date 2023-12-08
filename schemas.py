
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel


class UserIn(BaseModel):
    name:str
    email:str
    password:str

class UserOut(BaseModel):
    id:int
    name:str
    email:str
    created_at:datetime

class UserInForToken(BaseModel):
        id:int
        name:str


class UserInForUpdate(BaseModel):
        email:str
        password:str
        

pst_timezone = timezone(timedelta(hours=5))

class NoteIn(BaseModel):
        title: str
        description: str
        created_at: datetime = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(pst_timezone)

class NoteOut(BaseModel):
        title: str
        description: str
        owner_id: int
        created_at: datetime
                
class TokensForRefresh(BaseModel):
        refresh_token: str
        access_token: str

class VoteIn(BaseModel):
        note_id: int
        voter_id: int
                                