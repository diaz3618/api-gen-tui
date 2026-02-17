package security

import (
	"crypto/rand"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"strings"
	"time"
)

type TokenType string

const (
	TokenTypeAPIToken TokenType = "api"
	TokenTypeBearer   TokenType = "bearer"
	TokenTypeJWT      TokenType = "jwt"
	TokenTypeOAuth    TokenType = "oauth"
	TokenTypeWebhook  TokenType = "webhook"
)

type TokenOptions struct {
	Type      TokenType
	Length    int
	Prefix    string
	Uppercase bool
}

// GenerateToken generates various types of secure tokens
func GenerateToken(opts TokenOptions) (string, error) {
	switch opts.Type {
	case TokenTypeAPIToken:
		return generateAPIToken(opts)
	case TokenTypeBearer:
		return generateBearerToken(opts)
	case TokenTypeJWT:
		return generateJWTToken(opts)
	case TokenTypeOAuth:
		return generateOAuthToken(opts)
	case TokenTypeWebhook:
		return generateWebhookSecret(opts)
	default:
		return "", fmt.Errorf("unknown token type: %s", opts.Type)
	}
}

func generateAPIToken(opts TokenOptions) (string, error) {
	// Validate token length
	if opts.Length <= 0 {
		return "", fmt.Errorf("token length must be positive")
	}
	if opts.Length > 512 {
		return "", fmt.Errorf("token length must not exceed 512 bytes")
	}

	// API tokens are typically base64url encoded
	bytes := make([]byte, opts.Length)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}

	token := base64.URLEncoding.EncodeToString(bytes)
	if opts.Length > 0 && len(token) > opts.Length {
		token = token[:opts.Length]
	}

	if opts.Prefix != "" {
		return opts.Prefix + token, nil
	}
	return token, nil
}

func generateBearerToken(opts TokenOptions) (string, error) {
	// Validate token length
	if opts.Length <= 0 {
		return "", fmt.Errorf("token length must be positive")
	}
	if opts.Length > 512 {
		return "", fmt.Errorf("token length must not exceed 512 bytes")
	}

	// Bearer tokens are typically hex or base64
	bytes := make([]byte, opts.Length)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}

	token := hex.EncodeToString(bytes)
	if opts.Uppercase {
		token = strings.ToUpper(token)
	}

	return token, nil
}

func generateJWTToken(opts TokenOptions) (string, error) {
	// Validate payload length
	if opts.Length <= 0 {
		return "", fmt.Errorf("payload length must be positive")
	}
	if opts.Length > 1024 {
		return "", fmt.Errorf("payload length must not exceed 1024 bytes")
	}

	// Simulated JWT structure: header.payload.signature
	// Each part is base64url encoded

	headerBytes := make([]byte, 16)
	payloadBytes := make([]byte, opts.Length)
	signatureBytes := make([]byte, 32)

	if _, err := rand.Read(headerBytes); err != nil {
		return "", err
	}
	if _, err := rand.Read(payloadBytes); err != nil {
		return "", err
	}
	if _, err := rand.Read(signatureBytes); err != nil {
		return "", err
	}

	header := base64.RawURLEncoding.EncodeToString(headerBytes)
	payload := base64.RawURLEncoding.EncodeToString(payloadBytes)
	signature := base64.RawURLEncoding.EncodeToString(signatureBytes)

	return fmt.Sprintf("%s.%s.%s", header, payload, signature), nil
}

func generateOAuthToken(opts TokenOptions) (string, error) {
	// Validate token length
	if opts.Length <= 0 {
		return "", fmt.Errorf("token length must be positive")
	}
	if opts.Length > 512 {
		return "", fmt.Errorf("token length must not exceed 512 bytes")
	}

	// OAuth tokens with timestamp and random component
	timestamp := time.Now().Unix()
	bytes := make([]byte, opts.Length)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}

	randomPart := base64.URLEncoding.EncodeToString(bytes)
	token := fmt.Sprintf("%d_%s", timestamp, randomPart)

	if opts.Prefix != "" {
		return opts.Prefix + token, nil
	}
	return token, nil
}

func generateWebhookSecret(opts TokenOptions) (string, error) {
	// Validate secret length
	if opts.Length < 32 {
		return "", fmt.Errorf("webhook secret must be at least 32 bytes for security")
	}
	if opts.Length > 512 {
		return "", fmt.Errorf("webhook secret must not exceed 512 bytes")
	}

	// Webhook secrets are typically long, secure random strings
	bytes := make([]byte, opts.Length)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}

	secret := hex.EncodeToString(bytes)
	if opts.Prefix != "" {
		return opts.Prefix + secret, nil
	}
	return secret, nil
}
