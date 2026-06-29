# MAVVE API Reference

## Base URL
Local Development: `http://localhost:8000/api`

---

## 1. Orders API

### `POST /orders/intercept`
Evaluates an order's RTO risk and initiates a MAVVE session if the risk exceeds the threshold.

**Request Schema:**
```json
{
  "order_id": "ORD-1029",
  "force": false
}
```
*`force` (boolean, optional): If true, bypasses the RTO score threshold and forces a MAVVE session.*

**Response (High Risk):**
```json
{
  "status": "intercepted",
  "score": 0.82,
  "message": "High RTO risk detected. MAVVE session initialized."
}
```

**Response (Low Risk):**
```json
{
  "status": "ignored",
  "score": 0.15,
  "message": "Risk below threshold. Proceed to dispatch."
}
```

---

## 2. Webhooks API

### `GET /webhooks/whatsapp`
Used by Meta to verify the webhook endpoint.

**Query Parameters:**
- `hub.mode`: subscribe
- `hub.challenge`: integer
- `hub.verify_token`: string

### `POST /webhooks/whatsapp`
Receives incoming messages and status updates from WhatsApp users.

---

## 3. Simulator API

### `POST /demo/simulate`
Generates a mock order and triggers an end-to-end MAVVE simulation.

**Request Schema:**
```json
{
  "scenario": "bad_address",
  "language": "hi"
}
```

---

## Error Handling

MAVVE uses standard HTTP status codes:
- `400 Bad Request`: Invalid payload or missing fields.
- `403 Forbidden`: Failed webhook verification (invalid token).
- `404 Not Found`: Order ID or Session not found.
- `500 Internal Server Error`: LLM or external API failure.
