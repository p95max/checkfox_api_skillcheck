## API Usage

### Service Functionality

The service acts as a webhook-based lead processor:

- Receives incoming lead data via a single API endpoint
- Normalizes and validates incoming payloads
- Applies customer-specific business rules
- Transforms accepted leads into the customer-required schema
- Forwards valid leads to the fake customer API
- Rejects invalid leads without forwarding

The service is designed as a stateless, API-only microservice.

## Business Rules Summary

* Only leads with zipcode starting with `66` are accepted
* Only house owners are accepted
* Invalid leads return HTTP 200 with `accepted = false`
* Unauthorized requests return HTTP 401

## Technology Choice  
### Why FastAPI instead of Django

FastAPI was chosen because this project is a **small, isolated microservice**:

- The service is **API-only** and does not require templates, admin panel, or a full ORM.
- `Django` brings **significant built-in complexity** (apps, settings, middleware, admin) that is unnecessary for a standalone microservice.
- FastAPI offers **built-in OpenAPI / Swagger** and **Pydantic-based validation** with minimal setup.
- Lower overhead and faster development for focused, single-purpose services.

`Django` is a strong framework, but for a dedicated microservice it would be excessive without adding real value.

---

# Live Service

A production-ready instance is deployed and publicly available:

https://checkfox-api-skillcheck.onrender.com

The service is fully functional and connected to the fake customer API provided in the task.

**The service is deployed on a free-tier hosting plan.  
Cold starts and short response delays may occur during periods of inactivity.**

---

## Quick run by Docker

1. Run:
```bash
docker compose up --build
```

2. Open:
```text
http://127.0.0.1:8000/
```
(this redirects automatically to `/docs`)

**Note: All endpoints require `Bearer token` authentication.**

3. Click **Authorize**
4. Enter token value:
```text
FakeCustomerToken
```

---

## Webhook / Trigger Test (Endpoint #1)

The external trigger endpoint provided in the task can be used to send
an arbitrary lead to this service as a webhook.

This demonstrates the full end-to-end flow:
trigger → webhook → validation → transformation → customer API.

```bash
curl -i -X POST https://contactapi.static.fyi/lead/trigger/fake/petrykin/ \
  -H "Authorization: Bearer FakeCustomerToken" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://checkfox-api-skillcheck.onrender.com/api/v1/leads/ingest",
    "headers": {
      "Authorization": "Bearer FakeCustomerToken"
    }
  }'
```

## Smoke Test (cURL)

### Local (Docker)

```bash
curl -X POST http://localhost:8000/api/v1/leads/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FakeCustomerToken" \
  -d '{"payload":{"first_name":"John","last_name":"Doe","email":"johndoe123@example.com","phone":"+491234","zipcode":"66123","house_owner":true,"address_line1":"Weststr. 1","city":"Chemnitz"}}'
```

---

### Production (accepted: zipcode `66***` + `house_owner=true`)

```bash
curl -i -X POST https://checkfox-api-skillcheck.onrender.com/api/v1/leads/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FakeCustomerToken" \
  -d '{"payload":{"first_name":"John","last_name":"Doe","email":"johndoe123@example.com","phone":"+491234","zipcode":"66123","house_owner":true,"address_line1":"Weststr. 1","city":"Chemnitz"}}'
```

Expected response:

```json
{
  "accepted": true,
  "forwarded": true,
  "reason": null,
  "customer_status_code": 200
}
```

---

### Negative test (rejected: zipcode not allowed)

```bash
curl -i -X POST https://checkfox-api-skillcheck.onrender.com/api/v1/leads/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FakeCustomerToken" \
  -d '{"payload":{"first_name":"John","last_name":"Doe","email":"johndoe123@example.com","phone":"+491234","zipcode":"88123","house_owner":true,"address_line1":"Weststr. 1","city":"Chemnitz"}}'
```

Expected response:

```json
{
  "accepted": false,
  "forwarded": false,
  "reason": "zipcode_not_allowed",
  "customer_status_code": null
}
```

---

### Unauthorized test (missing Bearer token → HTTP 401)

```bash
curl -i -X POST https://checkfox-api-skillcheck.onrender.com/api/v1/leads/ingest \
  -H "Content-Type: application/json" \
  -d '{"payload":{"first_name":"John","last_name":"Doe","email":"johndoe123@example.com","phone":"+491234","zipcode":"66123","house_owner":true,"address_line1":"Weststr. 1","city":"Chemnitz"}}'
```

---

## Swagger UI

Swagger is available at:

Local:
```text
http://localhost:8000/
```

Production:
```text
https://checkfox-api-skillcheck.onrender.com
```

Use the **Authorize** button and enter the token value:

```text
FakeCustomerToken
```

Swagger automatically attaches the `Authorization: Bearer` header to all requests.

---

## Test Payload Examples

### Positive Test Data

Accepted lead (zipcode starts with `66`)

```json
{
  "payload": {
    "address_line1": "Weststr. 1",
    "city": "Chemnitz",
    "email": "johndoe123@example.com",
    "first_name": "John",
    "house_owner": true,
    "last_name": "Doe",
    "phone": "+491234",
    "zipcode": "86123"
  }
}
```

Expected behavior:

* `accepted = true`
* Lead is forwarded to customer API

---

### Negative Test Data

Rejected lead (zipcode does NOT start with `66`)

```json
{
  "payload": {
    "address_line1": "Weststr. 1",
    "city": "Chemnitz",
    "email": "johndoe123@example.com",
    "first_name": "John",
    "house_owner": true,
    "last_name": "Doe",
    "phone": "+491234",
    "zipcode": "86123"
  }
}
```

Expected behavior:

* `accepted = false`
* `reason = "zipcode_not_allowed"`
* Lead is not forwarded

---

## Pytest

```bash
poetry run pytest
```

---

## AI Usage Disclosure

AI assistance was used during the development of this project in a limited and transparent way.

### AI-assisted parts

The following areas were created or refined with the help of AI tools:

- Initial project scaffolding (FastAPI application structure, Docker setup)
- API schemas and data normalization logic, due to the absence of full customer documentation (customer_doc.pdf
customer_attribute_mapping.json)
- Customer payload transformation based on empirical validation against the fake customer API
- Test structure and basic test cases
- Documentation drafts (README and API usage examples)

All AI-generated content was reviewed, adjusted, and validated manually.

---

## Contacts

Author: Maksym Petrykin  
Email: m.petrykin@gmx.de  
Telegram: @max_p95