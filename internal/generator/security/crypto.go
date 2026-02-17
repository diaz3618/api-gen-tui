package security

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/base64"
	"encoding/pem"
	"fmt"

	"golang.org/x/crypto/bcrypt"
	"golang.org/x/crypto/ssh"
)

func GenerateSSHKey(keySize int) (string, error) {
	if keySize == 0 {
		keySize = 2048
	}

	// Enforce minimum security standards
	if keySize < 2048 {
		return "", fmt.Errorf("SSH key size must be at least 2048 bits for security")
	}
	if keySize > 16384 {
		return "", fmt.Errorf("SSH key size must not exceed 16384 bits")
	}

	privateKey, err := rsa.GenerateKey(rand.Reader, keySize)
	if err != nil {
		return "", fmt.Errorf("failed to generate RSA key: %w", err)
	}

	privateKeyBytes := x509.MarshalPKCS1PrivateKey(privateKey)
	privateKeyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privateKeyBytes,
	})

	publicKey, err := ssh.NewPublicKey(&privateKey.PublicKey)
	if err != nil {
		return "", fmt.Errorf("failed to generate SSH public key: %w", err)
	}
	publicKeySSH := ssh.MarshalAuthorizedKey(publicKey)

	// Display keys stacked vertically for better readability
	return fmt.Sprintf("PRIVATE KEY:\n%s\nPUBLIC KEY:\n%s", string(privateKeyPEM), string(publicKeySSH)), nil
}

func GenerateLaravelKey() (string, error) {
	// Generate 32 random bytes (256 bits for AES-256)
	keyBytes := make([]byte, 32)
	if _, err := rand.Read(keyBytes); err != nil {
		return "", fmt.Errorf("failed to generate random key: %w", err)
	}

	// Base64 encode and add Laravel prefix
	encodedKey := base64.StdEncoding.EncodeToString(keyBytes)
	return fmt.Sprintf("base64:%s", encodedKey), nil
}

func GenerateBcryptHash(password string, cost int) (string, error) {
	if cost == 0 {
		cost = bcrypt.DefaultCost
	}
	if cost < bcrypt.MinCost || cost > bcrypt.MaxCost {
		return "", fmt.Errorf("cost must be between %d and %d", bcrypt.MinCost, bcrypt.MaxCost)
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(password), cost)
	if err != nil {
		return "", fmt.Errorf("failed to generate bcrypt hash: %w", err)
	}

	return string(hash), nil
}

func GenerateSalt(length int) (string, error) {
	if length == 0 {
		length = 32
	}

	// Validate salt length
	if length < 16 {
		return "", fmt.Errorf("salt length must be at least 16 bytes for security")
	}
	if length > 256 {
		return "", fmt.Errorf("salt length must not exceed 256 bytes")
	}

	salt := make([]byte, length)
	if _, err := rand.Read(salt); err != nil {
		return "", fmt.Errorf("failed to generate salt: %w", err)
	}

	return base64.StdEncoding.EncodeToString(salt), nil
}
