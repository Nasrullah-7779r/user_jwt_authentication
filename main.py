from fastapi import FastAPI
from routers import user, note, vote
from db import engine
from models import base



base.metadata.create_all(bind = engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(note.router)
app.include_router(vote.router)


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
