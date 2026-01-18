import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas import NormalizedLead


class CustomerLeadModel(BaseModel):
    phone: str = Field(min_length=3)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    street: Optional[str] = None
    housenumber: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = Field(default=None, pattern="^(de|at|ch)$")


class CustomerProductModel(BaseModel):
    name: str = Field(min_length=1)


class CustomerPayloadModel(BaseModel):
    lead: CustomerLeadModel
    product: CustomerProductModel
    lead_attributes: dict[str, Any] = Field(default_factory=dict)
    meta_attributes: dict[str, Any] = Field(default_factory=dict)


def load_customer_attribute_mapping(path: Path) -> dict[str, Any]:
    """
    Loads customer attribute definitions used to filter lead_attributes.
    """
    raw = path.read_text(encoding="utf-8-sig")
    return json.loads(raw)


def _is_numeric_value(value: Any) -> bool:
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value.strip())
            return True
        except Exception:
            return False
    return False


def filter_lead_attributes(payload: dict[str, Any], mapping: dict[str, Any]) -> dict[str, Any]:
    """
    Filters payload attributes to only those accepted by customer's attribute mapping rules.
    """
    out: dict[str, Any] = {}

    for key, value in payload.items():
        rule = mapping.get(key)
        if rule is None:
            continue

        attr_type = rule.get("attribute_type")
        is_numeric = bool(rule.get("is_numeric"))
        allowed = rule.get("values")

        if value is None:
            continue

        if is_numeric and not _is_numeric_value(value):
            continue

        if attr_type == "dropdown" and allowed:
            if isinstance(value, list):
                if not value:
                    continue
                if not all(isinstance(v, str) for v in value):
                    continue
                if not all(v in allowed for v in value):
                    continue
                out[key] = value
                continue

            if not isinstance(value, str):
                continue
            if value not in allowed:
                continue
            out[key] = value
            continue

        if isinstance(value, (str, int, float, bool)):
            out[key] = value

    return out


def map_to_customer_payload(lead: NormalizedLead) -> dict[str, Any]:
    """
    Builds the exact customer API payload shape: lead/product/lead_attributes/meta_attributes.
    """
    payload = CustomerPayloadModel(
        lead=CustomerLeadModel(
            phone=lead.phone,
            email=lead.email,
            first_name=lead.first_name,
            last_name=lead.last_name,
            street=lead.street,
            housenumber=lead.housenumber,
            postcode=lead.zipcode,
            city=lead.city,
            country=lead.country,
        ),
        product=CustomerProductModel(name=lead.product_name),
        lead_attributes=lead.lead_attributes,
        meta_attributes=lead.meta_attributes,
    )
    return payload.model_dump(exclude_none=True)
