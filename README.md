## API Usage

### Live Service

A production-ready instance is deployed and publicly available:

https://checkfox-api-skillcheck.onrender.com

The service is fully functional and connected to the fake customer API provided in the task.

---

## Business Rules Summary

* Only leads with zipcode starting with `66` are accepted
* Only house owners are accepted
* Invalid leads return HTTP 200 with `accepted = false`
* Unauthorized requests return HTTP 401

---

## Technology Choice  
### Why FastAPI instead of Django

FastAPI was chosen because this project is a **small, isolated microservice**:

- The service is **API-only** and does not require templates, admin panel, or a full ORM.
- `Django` brings **significant built-in complexity** (apps, settings, middleware, admin) that is unnecessary for a standalone microservice.
- FastAPI offers **built-in OpenAPI / Swagger** and **Pydantic-based validation** with minimal setup.
- Lower overhead and faster development for focused, single-purpose services.

`Django` is a strong framework, but for a dedicated microservice it would be excessive without adding real value.

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
    "first_name": "Max",
    "last_name": "P",
    "email": "max@example.com",
    "phone": "+491234",
    "zipcode": "66123",
    "house_owner": true,
    "address_line1": "Street 1"
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
    "first_name": "Max",
    "last_name": "P",
    "email": "max@example.com",
    "phone": "+491234",
    "zipcode": "88123",
    "house_owner": true,
    "address_line1": "Street 1"
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

## Contacts

Author: Maksym Petrykin  
Email: m.petrykin@gmx.de  
Telegram: @max_p95