package security

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"encoding/pem"
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"
)

type EncryptionType string

const (
	EncryptionSymmetric  EncryptionType = "symmetric"
	EncryptionAsymmetric EncryptionType = "asymmetric"
)

type KeyFormat string

const (
	KeyFormatHex    KeyFormat = "hex"
	KeyFormatBase64 KeyFormat = "base64"
	KeyFormatPEM    KeyFormat = "pem"
)

type EncryptionKeyOptions struct {
	Type      EncryptionType
	KeySize   int
	Format    KeyFormat
	Algorithm string
}

func GenerateEncryptionKey(opts EncryptionKeyOptions) (string, error) {
	switch opts.Type {
	case EncryptionSymmetric:
		return generateSymmetricKey(opts)
	case EncryptionAsymmetric:
		return generateAsymmetricKey(opts)
	default:
		return "", fmt.Errorf("unknown encryption type: %s", opts.Type)
	}
}

func generateSymmetricKey(opts EncryptionKeyOptions) (string, error) {
	// Validate key size for symmetric keys (AES)
	if opts.KeySize != 16 && opts.KeySize != 24 && opts.KeySize != 32 {
		return "", fmt.Errorf("symmetric key size must be 16, 24, or 32 bytes (AES-128, AES-192, or AES-256)")
	}

	keyBytes := make([]byte, opts.KeySize)
	if _, err := rand.Read(keyBytes); err != nil {
		return "", fmt.Errorf("failed to generate random key: %w", err)
	}

	switch opts.Format {
	case KeyFormatHex:
		return hex.EncodeToString(keyBytes), nil
	case KeyFormatBase64:
		return base64.StdEncoding.EncodeToString(keyBytes), nil
	default:
		return hex.EncodeToString(keyBytes), nil
	}
}

func generateAsymmetricKey(opts EncryptionKeyOptions) (string, error) {
	keySize := opts.KeySize
	if keySize == 0 {
		keySize = 2048
	}

	// Enforce minimum RSA key size for security
	if keySize < 2048 {
		return "", fmt.Errorf("RSA key size must be at least 2048 bits for security")
	}
	if keySize > 16384 {
		return "", fmt.Errorf("RSA key size must not exceed 16384 bits")
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

	publicKeyBytes, err := x509.MarshalPKIXPublicKey(&privateKey.PublicKey)
	if err != nil {
		return "", fmt.Errorf("failed to marshal public key: %w", err)
	}
	publicKeyPEM := pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PUBLIC KEY",
		Bytes: publicKeyBytes,
	})

	// Format keys side-by-side with headers
	publicKeyLines := strings.Split(strings.TrimSpace(string(publicKeyPEM)), "\n")
	privateKeyLines := strings.Split(strings.TrimSpace(string(privateKeyPEM)), "\n")

	// Build public key column with header
	publicCol := []string{"PUBLIC KEY:"}
	publicCol = append(publicCol, publicKeyLines...)

	// Build private key column with header
	privateCol := []string{"PRIVATE KEY:"}
	privateCol = append(privateCol, privateKeyLines...)

	// Pad the shorter column with empty lines to match the longer one
	maxLen := len(publicCol)
	if len(privateCol) > maxLen {
		maxLen = len(privateCol)
	}

	for len(publicCol) < maxLen {
		publicCol = append(publicCol, "")
	}
	for len(privateCol) < maxLen {
		privateCol = append(privateCol, "")
	}

	// Join side-by-side with spacing
	publicSide := strings.Join(publicCol, "\n")
	privateSide := strings.Join(privateCol, "\n")

	// Use lipgloss to join horizontally with proper spacing
	result := lipgloss.JoinHorizontal(
		lipgloss.Top,
		publicSide,
		strings.Repeat(" ", 8), // 8 spaces between columns
		privateSide,
	)

	return result, nil
}
