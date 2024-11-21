from pydantic import BaseModel, Field


class AccountSchema(BaseModel):
    id: str = Field(...)
    balance: int = Field(...)
