## API Usage

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
- FastAPI offers **built-in OpenAPI/Swagger** and **Pydantic-based validation** with minimal setup.
- Lower overhead and faster development for focused, single-purpose services.

`Django`is a strong framework, but for a dedicated microservice it would be excessive without adding real value.

---

### Quick run by docker
1. Run
```bash
docker compose up --build
```
2. Open 
http://127.0.0.1:8000/docs

**Note:All endpoints require `Bearer token` authentication.**

3. Click on Authorize
4. Use `Bearer Token`
```
FakeCustomerToken
```

---

## Smoke Test (cURL)

```bash
curl -X POST http://localhost:8000/api/v1/leads/ingest \
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

## Swagger UI

Swagger is available at:

```
http://localhost:8000/
```

Use the **Authorize** button and enter the token value:

```
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

## Contacts

Author: Maksym Petrykin  
Email: [m.petrykin@gmx.de](mailto:m.petrykin@gmx.de)  
Telegram: [@max_p95](https://t.me/max_p95)