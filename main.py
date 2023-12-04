from fastapi import FastAPI
from routers import user 
from db import engine
from models import base



base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(user.router)

@app.get('/')
def start():
    return [
        {
        "for register":"go at /register"
        },
        {
            "for token":"go at /token"
        },
        {
            "for access":"go at /test/user_id"
        }
    ]
