from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field


class RawLead(BaseModel):
    payload: dict[str, Any]


class NormalizedLead(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    phone: str = Field(min_length=3)
    zipcode: str = Field(min_length=4)
    house_owner: bool
    address_line1: str = Field(min_length=1)
    city: Optional[str] = None


class IngestResult(BaseModel):
    accepted: bool
    forwarded: bool
    reason: Optional[str] = None
    customer_status_code: Optional[int] = None
