from pydantic import BaseModel, Field


class AccountSchema(BaseModel):
    account_id: str = Field(...)
    balance: float = Field(...)
