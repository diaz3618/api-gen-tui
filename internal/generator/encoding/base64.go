package encoding

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
)

type Base64Options struct {
	InputType string // "random", "text"
	Input     string // For text input
	Length    int    // For random input (bytes)
	Encoding  string // "standard", "url", "raw", "rawurl"
	Padding   bool
}

// GenerateBase64 generates base64 encoded data
func GenerateBase64(opts Base64Options) (string, error) {
	var data []byte
	var err error

	if opts.InputType == "text" && opts.Input != "" {
		data = []byte(opts.Input)
	} else {
		// Generate random bytes
		if opts.Length == 0 {
			opts.Length = 32
		}
		// Validate length
		if opts.Length <= 0 {
			return "", fmt.Errorf("length must be positive")
		}
		if opts.Length > 1024 {
			return "", fmt.Errorf("length must not exceed 1024 bytes")
		}
		data = make([]byte, opts.Length)
		if _, err = rand.Read(data); err != nil {
			return "", fmt.Errorf("failed to generate random data: %w", err)
		}
	}

	// Choose encoding
	var encoded string
	switch opts.Encoding {
	case "url":
		if opts.Padding {
			encoded = base64.URLEncoding.EncodeToString(data)
		} else {
			encoded = base64.RawURLEncoding.EncodeToString(data)
		}
	case "raw":
		encoded = base64.RawStdEncoding.EncodeToString(data)
	case "rawurl":
		encoded = base64.RawURLEncoding.EncodeToString(data)
	default: // "standard"
		encoded = base64.StdEncoding.EncodeToString(data)
	}

	return encoded, nil
}

// GenerateBase64String generates a random base64 string
func GenerateBase64String(length int, urlSafe bool) (string, error) {
	if length == 0 {
		length = 32
	}

	// Validate length
	if length <= 0 {
		return "", fmt.Errorf("length must be positive")
	}
	if length > 1024 {
		return "", fmt.Errorf("length must not exceed 1024 bytes")
	}

	data := make([]byte, length)
	if _, err := rand.Read(data); err != nil {
		return "", fmt.Errorf("failed to generate random data: %w", err)
	}

	if urlSafe {
		return base64.RawURLEncoding.EncodeToString(data), nil
	}
	return base64.StdEncoding.EncodeToString(data), nil
}
