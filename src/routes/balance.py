from fastapi import APIRouter, Query

from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/balance")


@router.get("")
def read_balance(account_id: int = Query(...)):
    account_id_formatted = str(account_id)
    if db_wrapper.contains_account(account_id_formatted):
        return response.success(db_wrapper.get_current_balance(account_id_formatted))
    return response.not_found(0)
