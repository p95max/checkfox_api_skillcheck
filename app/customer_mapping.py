from typing import Any
from pydantic import BaseModel, Field, EmailStr


class CustomerLead(BaseModel):
    firstName: str = Field(min_length=1)
    lastName: str = Field(min_length=1)
    email: EmailStr
    phone: str = Field(min_length=3)
    postalCode: str = Field(min_length=4)
    isHouseOwner: bool
    addressLine1: str = Field(min_length=1)


def map_to_customer_payload(normalized: dict[str, Any]) -> dict[str, Any]:
    """
    Transforms normalized lead fields to the customer's expected schema.
    """
    customer = CustomerLead(
        firstName=normalized["first_name"],
        lastName=normalized["last_name"],
        email=normalized["email"],
        phone=normalized["phone"],
        postalCode=normalized["zipcode"],
        isHouseOwner=normalized["house_owner"],
        addressLine1=normalized["address_line1"],
    )
    return customer.model_dump()
