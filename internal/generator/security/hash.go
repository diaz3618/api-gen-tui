package security

import (
"crypto/md5"
"crypto/rand"
"crypto/sha1"
"crypto/sha256"
"crypto/sha512"
"encoding/hex"
"fmt"
)

func GenerateHash(algorithm string, inputLength int) (string, error) {
// Validate input length
if inputLength <= 0 {
return "", fmt.Errorf("input length must be positive")
}
if inputLength > 1024 {
return "", fmt.Errorf("input length must not exceed 1024 bytes")
}

// Generate random data to hash
data := make([]byte, inputLength)
if _, err := rand.Read(data); err != nil {
return "", fmt.Errorf("failed to generate random data: %w", err)
}

// Hash the data based on the algorithm
var hash []byte
switch algorithm {
case "sha256":
h := sha256.Sum256(data)
hash = h[:]
case "sha512":
h := sha512.Sum512(data)
hash = h[:]
case "sha1":
h := sha1.Sum(data)
hash = h[:]
case "md5":
h := md5.Sum(data)
hash = h[:]
default:
return "", fmt.Errorf("unsupported hash algorithm: %s", algorithm)
}

return hex.EncodeToString(hash), nil
}
