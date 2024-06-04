from pydantic import BaseModel, Field


class EventSchema(BaseModel):
    type: str = Field(...)
    amount: int = Field(...)
    destination: str = None
    origin: str = None
