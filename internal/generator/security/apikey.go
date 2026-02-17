package security

import (
	"encoding/base64"
	"fmt"
	"strings"

	"github.com/diaz3618/api-gen-tui/internal/generator/common"
	"github.com/diaz3618/api-gen-tui/internal/generator/network"
)

type APIKeyFormat string

const (
	FormatAlphaNumeric APIKeyFormat = "alphanumeric"
	FormatHex          APIKeyFormat = "hex"
	FormatBase64       APIKeyFormat = "base64"
	FormatBase64URL    APIKeyFormat = "base64url"
	FormatUUID         APIKeyFormat = "uuid"
	FormatNumeric      APIKeyFormat = "numeric"
)

type APIKeyOptions struct {
	Format    APIKeyFormat
	Length    int
	Prefix    string
	Uppercase bool // For Hex
}

func GenerateAPIKey(opts APIKeyOptions) (string, error) {
	// Validate length
	if opts.Length <= 0 {
		return "", fmt.Errorf("API key length must be positive")
	}
	if opts.Length > 512 {
		return "", fmt.Errorf("API key length must not exceed 512 characters")
	}

	var key string
	var err error

	switch opts.Format {
	case FormatAlphaNumeric:
		key, err = common.RandomString(opts.Length, common.AlphaNumeric)
	case FormatHex:
		key, err = common.RandomString(opts.Length, common.Hex)
		if opts.Uppercase {
			key = strings.ToUpper(key)
		}
	case FormatNumeric:
		key, err = common.RandomString(opts.Length, common.Numeric)
	case FormatBase64, FormatBase64URL:
		// Calculate necessary bytes to get approximately length chars
		// Base64 is 4 chars for every 3 bytes.
		// n_bytes = (length * 3) / 4
		nBytes := (opts.Length * 3) / 4
		if nBytes == 0 {
			nBytes = 1
		}
		b, rErr := common.RandomBytes(nBytes)
		if rErr != nil {
			return "", rErr
		}
		if opts.Format == FormatBase64URL {
			key = base64.RawURLEncoding.EncodeToString(b)
		} else {
			key = base64.StdEncoding.EncodeToString(b)
		}
		// Trim or pad if strictly required, but base64 usually fixed by byte count.
		// Let's truncate if longer to match exact length requested if possible,
		// though base64 logic aligns to blocks.
		if len(key) > opts.Length {
			key = key[:opts.Length]
		}
	case FormatUUID:
		key, err = network.GenerateUUID(network.UUIDOptions{Version: 4, Hyphens: true}) // Reuse UUID logic
	default:
		key, err = common.RandomString(opts.Length, common.AlphaNumeric)
	}

	if err != nil {
		return "", err
	}

	if opts.Prefix != "" {
		key = opts.Prefix + key
	}

	return key, nil
}
