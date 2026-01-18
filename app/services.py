from pathlib import Path
from typing import Any, Optional
import logging
import re

from app.schemas import NormalizedLead
from app.customer_mapping import filter_lead_attributes, load_customer_attribute_mapping, map_to_customer_payload
from app.http_client import post_json
from app.settings import settings

logger = logging.getLogger("app.services")

_MAPPING_PATH = Path(__file__).resolve().parent / "resources" / "customer_attribute_mapping.json"
_CUSTOMER_ATTR_MAPPING: dict[str, Any] | None = None


def _get_customer_attr_mapping() -> dict[str, Any]:
    global _CUSTOMER_ATTR_MAPPING
    if _CUSTOMER_ATTR_MAPPING is not None:
        return _CUSTOMER_ATTR_MAPPING

    try:
        _CUSTOMER_ATTR_MAPPING = load_customer_attribute_mapping(_MAPPING_PATH)
        return _CUSTOMER_ATTR_MAPPING
    except FileNotFoundError:
        logger.error("Customer attribute mapping file missing path=%s", str(_MAPPING_PATH))
        _CUSTOMER_ATTR_MAPPING = {}
        return _CUSTOMER_ATTR_MAPPING
    except Exception:
        logger.exception("Failed to load customer attribute mapping path=%s", str(_MAPPING_PATH))
        _CUSTOMER_ATTR_MAPPING = {}
        return _CUSTOMER_ATTR_MAPPING


def _split_street_and_number(address_line1: str) -> tuple[str, Optional[str]]:
    addr = address_line1.strip()
    if not addr:
        return "", None
    m = re.match(r"^(.*?)(?:\s+(\d+[a-zA-Z]?))?$", addr)
    if not m:
        return addr, None
    street = (m.group(1) or "").strip()
    number = (m.group(2) or "").strip() or None
    return street or addr, number


def _pick_product_name(payload: dict[str, Any]) -> str:
    product = payload.get("product")
    if isinstance(product, dict):
        name = product.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()

    for k in ("product_name", "productName", "existing_product_name", "existingProductName", "product"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()

    return "solar"


def _extract_meta_attributes(payload: dict[str, Any]) -> dict[str, Any]:
    src = payload.get("meta_attributes")
    if isinstance(src, dict):
        return {k: v for k, v in src.items() if v is not None}

    keys = (
        "landingpage_url",
        "unique_id",
        "utm_campaign",
        "utm_content",
        "utm_medium",
        "utm_placement",
        "utm_source",
        "utm_term",
        "ip",
        "browser",
        "optin",
        "optin_wording",
        "optin_wording_2",
    )
    out: dict[str, Any] = {}
    for k in keys:
        v = payload.get(k)
        if v is not None:
            out[k] = v
    return out


def extract_normalized_lead(payload: dict[str, Any]) -> NormalizedLead:
    """
    Extracts the minimum required fields from an arbitrary lead payload and validates them.
    """
    lead_block = payload.get("lead") if isinstance(payload.get("lead"), dict) else {}
    product_block = payload.get("product") if isinstance(payload.get("product"), dict) else {}

    customer_mapping = _get_customer_attr_mapping()

    lead_attributes_raw = payload.get("lead_attributes") if isinstance(payload.get("lead_attributes"), dict) else {}
    meta_attributes = payload.get("meta_attributes") if isinstance(payload.get("meta_attributes"), dict) else {}

    lead_attributes = filter_lead_attributes(lead_attributes_raw, customer_mapping)

    house_owner_value = lead_attributes_raw.get("house_owner")
    if house_owner_value is None:
        house_owner_value = payload.get("house_owner")

    data = {
        "first_name": lead_block.get("first_name") or "",
        "last_name": lead_block.get("last_name") or "",
        "email": lead_block.get("email") or "",
        "phone": lead_block.get("phone") or "",
        "zipcode": lead_block.get("postcode") or lead_block.get("zipcode") or "",
        "house_owner": bool(house_owner_value) if house_owner_value is not None else False,
        "street": lead_block.get("street") or "",
        "housenumber": lead_block.get("housenumber"),
        "city": lead_block.get("city"),
        "country": lead_block.get("country") or "de",
        "product_name": (product_block.get("name") or "").strip() or "solar",
        "lead_attributes": lead_attributes,
        "meta_attributes": {k: v for k, v in meta_attributes.items() if v is not None},
    }
    return NormalizedLead(**data)


def evaluate_lead_rules(lead: NormalizedLead) -> tuple[bool, Optional[str]]:
    zipcode_ok = lead.zipcode.startswith("66")
    if not zipcode_ok:
        return False, "zipcode_not_allowed"
    if lead.house_owner is not True:
        return False, "not_house_owner"
    return True, None



async def forward_to_customer(lead: NormalizedLead) -> tuple[bool, Optional[int]]:
    """
    Sends accepted leads to the fake customer endpoint.
    """
    if not settings.send_to_customer:
        return True, None

    url = f"{settings.customer_base_url}/lead/receive/fake/{settings.user_id}/"
    headers = {"Authorization": f"Bearer {settings.bearer_token}"}
    payload = map_to_customer_payload(lead)

    try:
        resp = await post_json(url=url, headers=headers, payload=payload, timeout=settings.request_timeout_seconds)
        ok = 200 <= resp.status_code < 300
        return ok, resp.status_code
    except Exception:
        logger.exception("Customer API request failed")
        return False, None
