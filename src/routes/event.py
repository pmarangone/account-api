from fastapi import APIRouter, Body, HTTPException

from src.models.event import EventSchema
from src.models.errors import NonExist
from src.utils.db import db_wrapper
from src.utils import response
from src.utils.routes_responses import (
    BalanceResponse,
    DepositResponse,
    TransferResponse,
    WithdrawResponse,
)
from src.core.event import EventService

router = APIRouter(prefix="/event")


@router.post("/pg")
def event(event: EventSchema = Body(...)):
    try:
        event_service = EventService()
        response_data = event_service.process_transaction(event)
        return response.success(response_data)

    except NonExist as e:
        print("e", e)  # TODO
        return response.not_found(0)

    except Exception as e:
        print("e", e)  # TODO
        return response.bad_request(e)


@router.post("")
def event(event: EventSchema = Body(...)):
    match event.type:
        case "deposit":
            try:
                current_balance = db_wrapper.deposit(event.destination, event.amount)
                if current_balance:
                    data = DepositResponse(
                        destination=BalanceResponse(
                            id=event.destination, balance=current_balance
                        )
                    )
                    return response.created(data)
            except HTTPException as e:
                return response.bad_request(e)

        case "withdraw":
            try:
                current_balance = db_wrapper.withdraw(event.origin, event.amount)
                if current_balance:
                    data = WithdrawResponse(
                        origin=BalanceResponse(id=event.origin, balance=current_balance)
                    )
                    return response.created(data)
                else:
                    # Enhancement: if account exists and balance is less than amount
                    # returns a proper response
                    return response.not_found(0)
            except HTTPException as e:
                return response.bad_request(e)

        case "transfer":
            is_success = db_wrapper.transfer(
                event.origin, event.destination, event.amount
            )
            if is_success:
                origin_current_balance = db_wrapper.get_current_balance(event.origin)
                destination_current_balance = db_wrapper.get_current_balance(
                    event.destination
                )
                data = TransferResponse(
                    origin=BalanceResponse(
                        id=event.origin, balance=origin_current_balance
                    ),
                    destination=BalanceResponse(
                        id=event.destination, balance=destination_current_balance
                    ),
                )
                return response.created(data)
            else:
                return response.not_found(0)
        case _:
            return response.bad_request(f"Type '{event.type}' does not exist")

    return response.bad_request("")
