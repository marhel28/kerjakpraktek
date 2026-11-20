---
name: security
description: Threat modeling, vulnerability scanning, secret detection, and OWASP Top 10 compliance audits.
---

# Operational Skill: Security

## Core Vulnerability Focus
1. **Injection Prevention**:
   - **SQL Injection**: Never use raw string formatting (`f"SELECT ... WHERE id = '{user_id}'"`). Always use parameterized ORM constructs (`select().where(col == val)`).
   - **Command Injection**: Avoid `shell=True` in subprocess calls. Pass arguments as arrays.
   - **XSS**: Sanitize user inputs rendered in HTML templates.
2. **Authentication & Authorization**:
   - Verify JWT structure, expiration (`exp`), and Redis revocation (`jti` blocklist).
   - Check role-based access control (RBAC): verify user owns the target resource or holds `ADMIN` role.
   - Guard WebSocket connections against unauthenticated handshake spoofing.
3. **Secret Hygiene**:
   - Never commit `.env` files, private keys, API tokens, or hardcoded passwords.
   - Never log authorization headers or plain password hashes.
   - Verify secrets are loaded exclusively via environment variables or runtime configurations.
4. **Data Exposure**:
   - Strip sensitive fields (`password_hash`, internal IDs) from public Pydantic/DTO response schemas.
