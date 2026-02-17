# Complete Generator List

This document lists all 16 available generators in the TUI application, organized by category.

## Authentication & Access (6 generators)

### 1. Password Generator

**ID:** `password`
**Description:** Generate cryptographically secure passwords

**Options:**

- Length: 4-128 characters (default: 16)
- Count: 1-25 passwords (default: 1)
- Include uppercase letters (A-Z)
- Include lowercase letters (a-z)
- Include numbers (0-9)
- Include symbols (!@#$%^&*)
- Exclude similar characters (i, l, 1, L, o, 0, O)
- Exclude specific characters (custom input)

**Example Output:** `X7mK#9pLqR2vN4tY`

---

### 2. API Key Generator

**ID:** `apikey`
**Description:** Generate secure API keys with multiple formats

**Options:**

- Format: alphanumeric, hex, base64, base64url, uuid, numeric
- Length: 16-128 characters (default: 32)
- Prefix: Optional (e.g., `sk_`, `pk_`, `api_`)
- Uppercase: For hex format

**Example Output:** `sk_3fB9xK7mP2qL8vN5yT4rW1zC6hD0jG`

---

### 3. API Token Generator

**ID:** `apitoken`
**Description:** Generate API tokens with base64url encoding

**Options:**

- Length: 16-128 bytes (default: 32)
- Prefix: Optional (e.g., `token_`, `api_`)

**Example Output:** `token_MjY4NzQzOTEwMjU2NDg3MzIxOTQ1`

---

### 4. Bearer Token Generator

**ID:** `bearertoken`
**Description:** Generate bearer tokens for OAuth/API authentication

**Options:**

- Length: 32-128 bytes (default: 64)
- Uppercase: Use uppercase hex characters

**Example Output:** `f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6a5f4b3c2d1e0`

---

### 5. JWT Token Generator

**ID:** `jwttoken`
**Description:** Generate JSON Web Token (JWT) structure

**Options:**

- Payload Length: 32-256 bytes (default: 64)

**Example Output:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

---

### 6. OAuth Token Generator

**ID:** `oauthtoken`
**Description:** Generate OAuth access tokens with timestamp

**Options:**

- Length: 32-128 bytes (default: 64)
- Prefix: Optional (e.g., `oauth_`, `access_`)

**Example Output:** `oauth_1738713024_MjY4NzQzOTEwMjU2NDg3MzIxOTQ1`

---

## Cryptography & Security (7 generators)

### 7. Encryption Key Generator

**ID:** `encryptionkey`
**Description:** Generate symmetric or asymmetric encryption keys

**Options:**

- Type: symmetric (AES) or asymmetric (RSA)
- Key Size:
  - Symmetric: 16, 24, or 32 bytes
  - Asymmetric: 2048 or 4096 bits
- Format: hex, base64, or PEM

**Example Output (Symmetric, 32 bytes, hex):**

```
f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5
```

**Example Output (Asymmetric, 2048 bits, PEM):**

```
PRIVATE KEY:
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----

PUBLIC KEY:
-----BEGIN RSA PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END RSA PUBLIC KEY-----
```

---

### 8. SSH Key Generator

**ID:** `sshkey`
**Description:** Generate SSH RSA key pairs

**Options:**

- Key Size: 2048 or 4096 bits

**Example Output:**

```
PRIVATE KEY:
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----

PUBLIC KEY:
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...
```

---

### 9. Laravel Key Generator

**ID:** `laravelkey`
**Description:** Generate Laravel application encryption key

**Options:** None (generates standard Laravel key format)

**Example Output:** `base64:f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3`

---

### 10. Webhook Secret Generator

**ID:** `webhooksecret`
**Description:** Generate secure webhook signing secrets

**Options:**

- Length: 32-128 bytes (default: 64)
- Prefix: Optional (e.g., `whsec_`, `webhook_`)

**Example Output:** `whsec_f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5`

---

### 11. Salt Generator

**ID:** `salt`
**Description:** Generate cryptographic salts for password hashing

**Options:**

- Length: 16-64 bytes (default: 32)

**Example Output:** `f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9`

---

### 12. Hash Generator

**ID:** `hash`
**Description:** Generate cryptographic hashes of random data

**Options:**

- Algorithm: sha256, sha512, sha1, md5
- Input Length: 16-128 bytes (default: 32)

**Example Output:** `f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9`

---

### 13. Bcrypt Hash Generator

**ID:** `bcrypthash`
**Description:** Generate bcrypt hashes for password storage

**Options:**

- Password: Text to hash
- Cost Factor: 4-15 (default: 10, higher = more secure but slower)

**Example Output:** `$2a$10$N9qo8uLOickgx2ZMRZoMye7FRNpJnJZp8T/dU/Lw1VX9EUOgZ.vFu`

---

## Identifiers & Encoding (3 generators)

### 14. UUID Generator

**ID:** `uuid`
**Description:** Generate Universally Unique Identifiers

**Options:**

- Version: 1 (time-based), 3 (name MD5), 4 (random), 5 (name SHA1), 7 (time-ordered)
- Include Hyphens: Yes/No
- Uppercase: Yes/No
- Namespace: For v3/v5 (UUID or DNS/URL/OID/X500)
- Name: For v3/v5 (string to hash)

**Example Output (v4, hyphens):** `f47ac10b-58cc-4372-a567-0e02b2c3d479`

**Example Output (v4, no hyphens, uppercase):** `F47AC10B58CC4372A5670E02B2C3D479`

---

### 15. Base64 Encoder

**ID:** `base64`
**Description:** Encode random data or text to Base64

**Options:**

- Input Type: random or text
- Text Input: Custom text (if input type is text)
- Random Length: 16-128 bytes (default: 32, if input type is random)
- Encoding: standard, url (URL-safe), raw (no padding), rawurl (URL-safe, no padding)

**Example Output (random, standard):** `f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5==`

**Example Output (text "Hello World", standard):** `SGVsbG8gV29ybGQ=`

---

### 16. Base64 String Generator

**ID:** `base64string`
**Description:** Generate random Base64 strings

**Options:**

- Length: 16-128 bytes (default: 32)
- URL-Safe: Yes/No (removes padding and uses URL-safe characters)

**Example Output (standard):** `f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5==`

**Example Output (URL-safe):** `f3b9c8d7e6a5f4b3c2d1e0f9a8b7c6d5`

---

## Category Summary

| Category | Generators | Focus |
|----------|-----------|-------|
| Authentication & Access | 6 | Passwords, Keys, Tokens for API/OAuth |
| Cryptography & Security | 7 | Encryption, SSH, Hashing, Salts |
| Identifiers & Encoding | 3 | UUIDs, Base64 encoding |

**Total: 16 Generators**

---

## Security Notes

All generators use cryptographically secure random number generation (`crypto/rand`) to ensure:

- Unpredictability
- High entropy
- Suitable for security-sensitive applications

**Use Cases:**

- API authentication
- Password generation
- Encryption key creation
- Secure token generation
- Database salt creation
- Webhook signature verification
