from pydantic import BaseModel, Field, field_validator


class EventSchema(BaseModel):
    type: str = Field(...)
    amount: float = Field(...)
    destination: str = None
    origin: str = None

    @field_validator("amount")
    def amount_must_be_greater_than_zero(cls, value):
        if value <= 0:
            raise ValueError("Amount must be greater than zero")
        return value
