from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers import notify, user, note, vote
from db import engine
from models import base
from fastapi.middleware.cors import CORSMiddleware

templates = Jinja2Templates(directory="templates")

base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(note.router)
app.include_router(vote.router)
app.include_router(notify.router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/', response_class=HTMLResponse)
def start(request: Request):
     return templates.TemplateResponse("index.html", {"request": request})

@app.get('/vote', response_class=HTMLResponse)
def upvote_devote(request: Request):
     return templates.TemplateResponse("vote.html", {"request": request})



# @app.get('/')
# def start():
#     return [
#         {
#         "for register":"go at /register"
#         },
#         {
#             "for token":"go at /token"
#         },
#         {
#             "for access":"go at /test/user_id"
#         }
#     ]



# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)
