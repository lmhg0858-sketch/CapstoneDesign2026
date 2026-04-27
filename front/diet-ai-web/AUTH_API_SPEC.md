# Auth API Payload Spec

## Base URL
- `VITE_API_BASE_URL` (example: `http://localhost:8080`)

## 1) Login
- Method: `POST`
- Path: `/auth/login`
- Headers:
  - `Content-Type: application/json`
- Request body:
```json
{
  "id": "string",
  "password": "string"
}
```

## 2) Signup
- Method: `POST`
- Path: `/auth/signup`
- Headers:
  - `Content-Type: application/json`
- Request body:
```json
{
  "name": "string",
  "nickname": "string",
  "email": "string",
  "gender": "MALE",
  "age": 25,
  "height": 170,
  "weight": 65,
  "desease": ["HYPERTENSION", "DIABETES"],
  "id": "string",
  "password": "string"
}
```

## Chronic disease enum values
- `HYPERTENSION` (고혈압)
- `HYPERLIPIDEMIA` (고지혈증)
- `DIABETES` (당뇨)
- `KIDNEY_DISEASE` (신장질환)

## Response expectation (front)
- Success: `2xx` with JSON body (shape free)
- Error: non-`2xx` with optional JSON `{ "message": "..." }`
