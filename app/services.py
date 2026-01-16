from typing import Any, Optional
import logging
from app.schemas import NormalizedLead
from app.customer_mapping import map_to_customer_payload
from app.http_client import post_json
from app.settings import settings

logger = logging.getLogger("app.services")


def extract_normalized_lead(payload: dict[str, Any]) -> NormalizedLead:
    """
    Extracts the minimum required fields from an arbitrary lead payload and validates them.
    """
    data = {
        "first_name": payload.get("first_name") or payload.get("firstname") or payload.get("firstName") or "",
        "last_name": payload.get("last_name") or payload.get("lastname") or payload.get("lastName") or "",
        "email": payload.get("email") or "",
        "phone": payload.get("phone") or payload.get("mobile") or "",
        "zipcode": payload.get("zipcode") or payload.get("zip") or payload.get("postal_code") or payload.get("postalCode") or "",
        "house_owner": payload.get("house_owner")
        if payload.get("house_owner") is not None
        else payload.get("isHouseOwner")
        if payload.get("isHouseOwner") is not None
        else payload.get("owner")
        if payload.get("owner") is not None
        else False,
        "address_line1": payload.get("address_line1") or payload.get("address") or payload.get("street") or "",
        "city": payload.get("city"),
    }
    return NormalizedLead(**data)


def evaluate_lead_rules(lead: NormalizedLead) -> tuple[bool, Optional[str]]:
    zipcode_ok = lead.zipcode.startswith("66")
    if not zipcode_ok:
        return False, "zipcode_not_allowed"
    if lead.house_owner is not True:
        return False, "not_house_owner"
    return True, None


def is_authorized(authorization_header: Optional[str], expected_token: str) -> bool:
    """
    Validates Bearer token from the Authorization header.
    """
    if not authorization_header:
        return False
    if not authorization_header.startswith("Bearer "):
        return False
    token = authorization_header.removeprefix("Bearer ").strip()
    return token == expected_token



async def forward_to_customer(lead: NormalizedLead) -> tuple[bool, Optional[int]]:
    """
    Sends accepted leads to the fake customer endpoint.
    """
    if not settings.send_to_customer:
        return True, None

    url = f"{settings.customer_base_url}/lead/receive/fake/{settings.user_id}/"
    headers = {"Authorization": f"Bearer {settings.bearer_token}"}
    payload = map_to_customer_payload(lead.model_dump())

    try:
        resp = await post_json(url=url, headers=headers, payload=payload, timeout=settings.request_timeout_seconds)
        ok = 200 <= resp.status_code < 300
        return ok, resp.status_code
    except Exception:
        logger.exception("Customer API request failed")
        return False, None

