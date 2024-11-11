from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder

from src.database.account_manager import account_manager
from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/balance")


@router.get("/test")
def read_balance_sql(account_id: int = Query(...)):
    account_id = account_manager.get_account(str(account_id))

    if account_id:
        return response.success(jsonable_encoder(account_id))
    return response.not_found(0)


@router.get("")
def read_balance(account_id: int = Query(...)):
    # Why did I have a map<str, int> instead of map<int,int>
    account_id_formatted = str(account_id)
    if db_wrapper.contains_account(account_id_formatted):
        return response.success(db_wrapper.get_current_balance(account_id_formatted))
    return response.not_found(0)
