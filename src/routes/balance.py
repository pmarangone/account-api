from fastapi import APIRouter, Query

from src.repositories.account import AccountRepository
from src.services.event import EventService
from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/balance")


@router.get("/pg")
def read_balance_sql(account_id: int = Query(...)):
    account_repository = AccountRepository()
    event_service = EventService(account_repository)
    response_data = event_service.get_account_balance(str(account_id))
    return response_data


@router.get("")
def read_balance(account_id: int = Query(...)):
    # Why did I have a map<str, int> instead of map<int,int>
    account_id_formatted = str(account_id)
    if db_wrapper.contains_account(account_id_formatted):
        return response.success(db_wrapper.get_current_balance(account_id_formatted))
    return response.not_found(0)
