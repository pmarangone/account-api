from fastapi import FastAPI
from .routes import balance, event
from .utils.db import db_wrapper
from .utils import response


app = FastAPI()
app.include_router(balance.router)
app.include_router(event.router)


@app.get("/")
def read_root():
    return {"v0.1"}


@app.post("/reset")
def reset():
    db_wrapper.db.reset()
    return response.OK()
