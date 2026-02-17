package security

import (
	"crypto/rand"
	"errors"
	"math/big"
	"strings"
)

type PasswordOptions struct {
	Length           int
	Count            int
	IncludeUppercase bool
	IncludeLowercase bool
	IncludeNumbers   bool
	IncludeSymbols   bool
	ExcludeSimilar   bool
	ExcludeChars     string
}

const (
	lowerChars   = "abcdefghijklmnopqrstuvwxyz"
	upperChars   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	numberChars  = "0123456789"
	symbolChars  = "!@#$%^&*()-_=+[]{}|;:,.<>?"
	similarChars = "il1Lo0O" // Characters that look similar
)

func GeneratePassword(opts PasswordOptions) (string, error) {
	if opts.Length <= 0 {
		return "", errors.New("length must be greater than 0")
	}

	if opts.Length < 4 || opts.Length > 128 {
		return "", errors.New("length must be between 4 and 128")
	}

	if opts.Count <= 0 {
		opts.Count = 1
	}

	if opts.Count > 25 {
		return "", errors.New("count must be between 1 and 25")
	}

	var charSet strings.Builder
	if opts.IncludeLowercase {
		charSet.WriteString(lowerChars)
	}
	if opts.IncludeUppercase {
		charSet.WriteString(upperChars)
	}
	if opts.IncludeNumbers {
		charSet.WriteString(numberChars)
	}
	if opts.IncludeSymbols {
		charSet.WriteString(symbolChars)
	}

	pool := charSet.String()
	if pool == "" {
		return "", errors.New("at least one character set must be selected")
	}

	// Remove similar characters if requested
	if opts.ExcludeSimilar {
		pool = removeSimilarChars(pool)
	}

	// Remove specific excluded characters
	if opts.ExcludeChars != "" {
		pool = removeChars(pool, opts.ExcludeChars)
	}

	if len(pool) == 0 {
		return "", errors.New("no characters available after exclusions")
	}

	// Generate multiple passwords if count > 1
	var results []string
	for i := 0; i < opts.Count; i++ {
		password, err := generateSinglePassword(opts.Length, pool)
		if err != nil {
			return "", err
		}
		results = append(results, password)
	}

	return strings.Join(results, "\n"), nil
}

func generateSinglePassword(length int, pool string) (string, error) {
	var password strings.Builder
	poolLen := big.NewInt(int64(len(pool)))

	for i := 0; i < length; i++ {
		idx, err := rand.Int(rand.Reader, poolLen)
		if err != nil {
			return "", err
		}
		password.WriteByte(pool[idx.Int64()])
	}

	return password.String(), nil
}

func removeSimilarChars(s string) string {
	var result strings.Builder
	for _, c := range s {
		if !strings.ContainsRune(similarChars, c) {
			result.WriteRune(c)
		}
	}
	return result.String()
}

func removeChars(s, exclude string) string {
	var result strings.Builder
	for _, c := range s {
		if !strings.ContainsRune(exclude, c) {
			result.WriteRune(c)
		}
	}
	return result.String()
}
