from pydantic import BaseModel, Field


class EventSchema(BaseModel):
    type: str = Field(...)
    amount: float = Field(...)
    destination: str = None
    origin: str = None


class AccountSchema(BaseModel):
    id: str = Field(...)
    balance: int = Field(...)


class NonExist(Exception):
    pass
