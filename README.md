# Smoke curl
```bash
curl -X POST http://localhost:8000/api/v1/leads/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer FakeCustomerToken" \
  -d '{"payload":{"first_name":"John","last_name":"Doe","email":"johndoe123@example.com","phone":"+491234","zipcode":"66123","house_owner":true,"address_line1":"Weststr. 1","city":"Chemnitz"}}'
```

# Swagger body
## Positive test data(zipcode starts by "66---")
```bash
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
## Negative test data(zipcode NOT starts by "66---")
```bash
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