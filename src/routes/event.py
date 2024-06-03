from fastapi import APIRouter, Body

from src.models.event import EventSchema
from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/event")


@router.post("/")
def event(event: EventSchema = Body(...)):
    is_success = False
    match event.type:
        # TODO: handle invalid values types
        case "deposit":
            is_success = db_wrapper.deposit(event.destination, event.amount)
        case "withdraw":
            is_success = db_wrapper.withdraw(event.origin, event.amount)
        case "transfer":
            is_success = db_wrapper.transfer(
                event.origin, event.destination, event.amount
            )
        case _:
            return response.bad_request(f"Type '{event.type}' does not exist")

    # TODO: handle responses correctly
    return response.success("") if is_success else response.bad_request("")
