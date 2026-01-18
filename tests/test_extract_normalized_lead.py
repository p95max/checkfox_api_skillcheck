from app.services import extract_normalized_lead


def test_extracts_nested_payload_ok():
    payload = {
        "lead": {
            "city": "Chemnitz",
            "country": "de",
            "email": "johndoe123@example.com",
            "first_name": "John",
            "housenumber": "1",
            "last_name": "Doe",
            "phone": "+491234",
            "postcode": "66123",
            "street": "Weststr.",
        },
        "lead_attributes": {
            "house_owner": True,
            "property_type": "single_family_house",
        },
        "meta_attributes": {
            "unique_id": "abc-123",
            "utm_source": "google",
        },
        "product": {"name": "solar"},
    }

    lead = extract_normalized_lead(payload)

    assert lead.first_name == "John"
    assert lead.last_name == "Doe"
    assert lead.email == "johndoe123@example.com"
    assert lead.phone == "+491234"
    assert lead.zipcode == "66123"
    assert lead.house_owner is True
    assert lead.street == "Weststr."
    assert lead.housenumber == "1"
    assert lead.city == "Chemnitz"
    assert lead.country == "de"
    assert lead.product_name == "solar"
    assert lead.meta_attributes["unique_id"] == "abc-123"


def test_extracts_nested_payload_defaults_owner_false_when_missing():
    payload = {
        "lead": {
            "email": "johndoe123@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+491234",
            "postcode": "66123",
            "street": "Weststr.",
        },
        "lead_attributes": {
            "property_type": "single_family_house",
        },
        "meta_attributes": {},
        "product": {"name": "solar"},
    }

    lead = extract_normalized_lead(payload)

    assert lead.house_owner is False
