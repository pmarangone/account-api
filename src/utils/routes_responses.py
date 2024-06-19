from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    id: str = Field(...)
    balance: float = Field(...)


class DepositResponse(BaseModel):
    destination: BalanceResponse = Field(...)


class WithdrawResponse(BaseModel):
    origin: BalanceResponse = Field(...)


class TransferResponse(BaseModel):
    origin: BalanceResponse = Field(...)
    destination: BalanceResponse = Field(...)
