from fastapi import APIRouter, Body

from src.models.event import EventSchema
from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/event")


@router.post("")
def event(event: EventSchema = Body(...)):
    match event.type:
        # TODO: handle invalid values types
        case "deposit":
            is_success = db_wrapper.deposit(event.destination, event.amount)
            if is_success:
                current_balance = db_wrapper.get_current_balance(event.destination)
                data = {
                    "destination": {"id": event.destination, "balance": current_balance}
                }
                return response.created(data)
        case "withdraw":
            is_success = db_wrapper.withdraw(event.origin, event.amount)
            if is_success:
                current_balance = db_wrapper.get_current_balance(event.origin)
                data = {"origin": {"id": event.origin, "balance": current_balance}}
                return response.created(data)
            else:
                # Enhancement: if account exists and balance is less than amount
                # returns a proper response
                return response.not_found(0)

        case "transfer":
            is_success = db_wrapper.transfer(
                event.origin, event.destination, event.amount
            )
            if is_success:
                origin_current_balance = db_wrapper.get_current_balance(event.origin)
                destination_current_balance = db_wrapper.get_current_balance(
                    event.destination
                )
                data = {
                    "origin": {"id": event.origin, "balance": origin_current_balance},
                    "destination": {
                        "id": event.destination,
                        "balance": destination_current_balance,
                    },
                }
                return response.created(data)
            else:
                return response.not_found(0)
        case _:
            return response.bad_request(f"Type '{event.type}' does not exist")

    return response.bad_request("")
