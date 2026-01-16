from app.schemas import NormalizedLead
from app.services import evaluate_lead_rules


def test_accepts_zip_66_owner_true():
    lead = NormalizedLead(
        first_name="Max",
        last_name="P",
        email="max@example.com",
        phone="+491234",
        zipcode="66123",
        house_owner=True,
        address_line1="Street 1",
        city="X",
    )
    accepted, reason = evaluate_lead_rules(lead)
    assert accepted is True
    assert reason is None


def test_rejects_wrong_zip():
    lead = NormalizedLead(
        first_name="Max",
        last_name="P",
        email="max@example.com",
        phone="+491234",
        zipcode="70123",
        house_owner=True,
        address_line1="Street 1",
        city="X",
    )
    accepted, reason = evaluate_lead_rules(lead)
    assert accepted is False
    assert reason == "zipcode_not_allowed"
