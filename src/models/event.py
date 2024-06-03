from pydantic import BaseModel, Field
from typing import Optional


class EventSchema(BaseModel):
    type: str = Field(...)
    amount: int = Field(...)
    destination: str = None
    origin: str = None
