from app.customer_mapping import map_to_customer_payload
from app.schemas import NormalizedLead


def test_customer_payload_shape():
    lead = NormalizedLead(
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        phone="+491234",
        zipcode="66123",
        house_owner=True,
        street="Weststr.",
        housenumber="1",
        city="Chemnitz",
        country="de",
        product_name="solar",
        lead_attributes={"solar_owner": "Ja"},
        meta_attributes={"unique_id": "123"},
    )

    payload = map_to_customer_payload(lead)

    assert "lead" in payload
    assert "product" in payload
    assert payload["lead"]["phone"] == "+491234"
    assert payload["lead"]["postcode"] == "66123"
    assert payload["product"]["name"] == "solar"
    assert payload["lead_attributes"]["solar_owner"] == "Ja"
    assert payload["meta_attributes"]["unique_id"] == "123"
