
from datetime import datetime
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
        