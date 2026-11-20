---
name: api-design
description: RESTful API standards, WebSocket contracts, OpenAPI documentation, schema validation, and backwards compatibility.
---

# Operational Skill: API Design

## Design Guidelines
1. **REST Resource Naming**:
   - Use plural nouns: `/api/products`, `/api/orders`, `/messages`.
   - Use standard HTTP methods:
     - `GET`: Safe, idempotent read.
     - `POST`: Create resource or execute non-idempotent action.
     - `PUT`: Complete resource replacement.
     - `PATCH`: Partial update.
     - `DELETE`: Remove resource.
2. **Schema Contracts**:
   - Enforce strict Pydantic v2 validation on all request bodies.
   - Separate Create/Update input schemas from Out/Response schemas.
   - Never leak internal primary keys or sensitive metadata unless intended.
3. **Status Codes & Responses**:
   - `200 OK`: Successful read or update.
   - `201 Created`: Successful creation with returned entity.
   - `400 Bad Request`: Malformed syntax or invalid business validation.
   - `401 Unauthorized`: Missing or invalid authentication token.
   - `403 Forbidden`: Authenticated user lacks permission.
   - `404 Not Found`: Resource does not exist.
   - `422 Unprocessable Entity`: Schema validation failure.
4. **WebSocket Contracts**:
   - Standard envelope format: `{"type": "<event_name>", "data": {...}}`.
   - Handshake authentication via query parameter token with immediate closure (`1008`) upon invalid credential.
