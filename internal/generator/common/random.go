package common

import (
	"crypto/rand"
	"math/big"
)

const (
	AlphaNumeric = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	Hex          = "0123456789abcdef"
	Numeric      = "0123456789"
	LowerAlpha   = "abcdefghijklmnopqrstuvwxyz"
	UpperAlpha   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	Symbols      = "!@#$%^&*()-_=+[]{}|;:,.<>?"
)

// RandomInt generates a secure random integer in [0, max).
func RandomInt(max int64) (int64, error) {
	n, err := rand.Int(rand.Reader, big.NewInt(max))
	if err != nil {
		return 0, err
	}
	return n.Int64(), nil
}

// RandomString generates a random string of given length using the provided charset.
func RandomString(length int, charset string) (string, error) {
	if length <= 0 {
		return "", nil
	}
	b := make([]byte, length)
	max := big.NewInt(int64(len(charset)))
	for i := range b {
		n, err := rand.Int(rand.Reader, max)
		if err != nil {
			return "", err
		}
		b[i] = charset[n.Int64()]
	}
	return string(b), nil
}

// RandomBytes generates n secure random bytes.
func RandomBytes(n int) ([]byte, error) {
	b := make([]byte, n)
	_, err := rand.Read(b)
	if err != nil {
		return nil, err
	}
	return b, nil
}
