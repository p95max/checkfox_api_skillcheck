import logging
from typing import Any

from fastapi import FastAPI, Response, Header, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.logging_conf import configure_logging
from app.schemas import IngestResult
from app.services import extract_normalized_lead, evaluate_lead_rules, forward_to_customer
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services import is_authorized
from app.settings import settings

configure_logging(settings.log_level)
logger = logging.getLogger("app")

app = FastAPI(title=settings.app_name)
bearer = HTTPBearer(auto_error=False)


class LeadIn(BaseModel):
    payload: dict[str, Any] = Field(
        default_factory=dict,
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "johndoe123@example.com",
                "phone": "+491234",
                "zipcode": "66123",
                "house_owner": True,
                "address_line1": "Weststr. 1",
                "city": "Chemnitz",
            }
        },
    )



@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")

@app.get("/health", include_in_schema=True)
async def health() -> Response:
    return Response(status_code=200)

def require_token(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> None:
    if creds is None or creds.scheme.lower() != "bearer" or creds.credentials != settings.bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")


@app.post("/api/v1/leads/ingest", response_model=IngestResult, dependencies=[Depends(require_token)])
async def ingest_lead(body: LeadIn) -> IngestResult:
    try:
        lead = extract_normalized_lead(body.payload)
    except Exception:
        logger.exception("Lead validation failed")
        return IngestResult(accepted=False, forwarded=False, reason="lead_validation_failed")

    accepted, reason = evaluate_lead_rules(lead)
    if not accepted:
        logger.info("Lead rejected reason=%s zipcode=%s email=%s", reason, lead.zipcode, lead.email)
        return IngestResult(accepted=False, forwarded=False, reason=reason)

    forwarded_ok, status_code = await forward_to_customer(lead)
    if not forwarded_ok and settings.send_to_customer:
        logger.error("Lead accepted but forwarding failed status_code=%s email=%s", status_code, lead.email)
        return IngestResult(
            accepted=True,
            forwarded=False,
            reason="customer_forward_failed",
            customer_status_code=status_code,
        )

    logger.info("Lead accepted and forwarded email=%s zipcode=%s", lead.email, lead.zipcode)
    return IngestResult(accepted=True, forwarded=True, customer_status_code=status_code)
