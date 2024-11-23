from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder

from src.database.account_repository import account_repository
from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/balance")


@router.get("/pg")
def read_balance_sql(account_id: int = Query(...)):
    account_data = account_repository.get_account(str(account_id))
    try:
        if account_data:
            return response.success(account_data["balance"])
        return response.not_found(0)
    except Exception as e:
        # TODO: log e
        return response.bad_request(e)


@router.get("")
def read_balance(account_id: int = Query(...)):
    # Why did I have a map<str, int> instead of map<int,int>
    account_id_formatted = str(account_id)
    if db_wrapper.contains_account(account_id_formatted):
        return response.success(db_wrapper.get_current_balance(account_id_formatted))
    return response.not_found(0)
