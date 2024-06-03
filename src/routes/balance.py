from fastapi import APIRouter

from src.utils.db import db_wrapper
from src.utils import response

router = APIRouter(prefix="/balance")


@router.get("/{account_id}")
def read_balance(account_id: str):
    if db_wrapper.contains_account(account_id):
        return response.success(db_wrapper.get_current_balance(account_id))
    return response.not_found(0)
