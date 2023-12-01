from fastapi import FastAPI
from routers import user 
from db import engine
from models import base



base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(user.router)

