import asyncio
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.consume_messages import consume_messages

from .routes import balance, event
from .utils.db import db_wrapper
from .utils import response
from contextlib import asynccontextmanager


# Lifespan function to start background task with improved stop mechanism
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     stop_event = asyncio.Future()
#     task = asyncio.create_task(consume_messages(stop_event))
#     try:
#         yield
#     finally:
#         stop_event.set_result(True)  # Signal the task to stop
#         task.cancel()
#         try:
#             await task
#         except asyncio.CancelledError:
#             pass
#         await asyncio.gather(task, return_exceptions=True)


app = FastAPI()
app.include_router(balance.router)
app.include_router(event.router)


# Customize validation exception handler
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     # Response must be an array since more than one field could be invalid
#     errors = [{"msg": err["msg"]} for err in exc.errors()]
#     return JSONResponse(status_code=422, content=errors)


@app.get("/")
def read_root():
    return {"v0.1"}


@app.post("/reset")
def reset():
    db_wrapper.db.reset()
    return response.OK()
