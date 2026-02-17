package math

import (
	"fmt"
	"math/big"
	"math/rand"
	"sort"

	"github.com/diaz3618/api-gen-tui/internal/generator/common"
)

type NumberType string

const (
	Integer    NumberType = "integer"
	Decimal    NumberType = "decimal"
	Prime      NumberType = "prime"
	Percentage NumberType = "percentage"
	Binary     NumberType = "binary"
	Even       NumberType = "even"
	Odd        NumberType = "odd"
	Negative   NumberType = "negative"
	Hex        NumberType = "hex"
	Octal      NumberType = "octal"
)

type NumberOptions struct {
	Type      NumberType
	Min       int64
	Max       int64
	Count     int
	Unique    bool
	Sort      string // "asc", "desc", "none"
	Precision int    // for decimals
}

func GenerateNumbers(opts NumberOptions) ([]string, error) {
	if opts.Count <= 0 {
		opts.Count = 1
	}
	if opts.Min > opts.Max {
		opts.Min, opts.Max = opts.Max, opts.Min
	}

	results := make([]string, 0, opts.Count)
	seen := make(map[string]bool)

	for len(results) < opts.Count {
		var val string

		switch opts.Type {
		case Integer:
			v, err := common.RandomInt(opts.Max - opts.Min + 1)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("%d", v+opts.Min)

		case Even:
			v, err := generateEvenNumber(opts.Min, opts.Max)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("%d", v)

		case Odd:
			v, err := generateOddNumber(opts.Min, opts.Max)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("%d", v)

		case Negative:
			v, err := common.RandomInt(opts.Max - opts.Min + 1)
			if err != nil {
				return nil, err
			}
			num := v + opts.Min
			if num > 0 {
				num = -num
			}
			val = fmt.Sprintf("%d", num)

		case Hex:
			v, err := common.RandomInt(opts.Max - opts.Min + 1)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("0x%X", v+opts.Min)

		case Octal:
			v, err := common.RandomInt(opts.Max - opts.Min + 1)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("0o%o", v+opts.Min)

		case Binary:
			v, err := common.RandomInt(2)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("%d", v)

		case Percentage:
			v, err := common.RandomInt(101)
			if err != nil {
				return nil, err
			}
			val = fmt.Sprintf("%d%%", v)

		case Decimal:
			intPart, _ := common.RandomInt(opts.Max - opts.Min)
			floatPart := rand.Float64()
			finalVal := float64(intPart+opts.Min) + floatPart
			format := fmt.Sprintf("%%.%df", opts.Precision)
			val = fmt.Sprintf(format, finalVal)

		case Prime:
			// Simple rejection sampling for primes
			attempts := 0
			maxAttempts := 10000
			for attempts < maxAttempts {
				n, err := common.RandomInt(opts.Max - opts.Min + 1)
				if err != nil {
					return nil, err
				}
				num := big.NewInt(n + opts.Min)
				if num.ProbablyPrime(20) {
					val = num.String()
					break
				}
				attempts++
			}
			if attempts >= maxAttempts {
				return nil, fmt.Errorf("could not find prime in range after %d attempts", maxAttempts)
			}
		}

		if opts.Unique {
			if !seen[val] {
				seen[val] = true
				results = append(results, val)
			} else {
				rangeSize := opts.Max - opts.Min + 1
				if int64(len(seen)) >= rangeSize {
					break
				}
			}
		} else {
			results = append(results, val)
		}
	}

	// Sorting
	if opts.Sort == "asc" {
		sort.Strings(results)
	} else if opts.Sort == "desc" {
		sort.Sort(sort.Reverse(sort.StringSlice(results)))
	}

	return results, nil
}

func generateEvenNumber(min, max int64) (int64, error) {
	if min%2 != 0 {
		min++
	}
	if max%2 != 0 {
		max--
	}

	if min > max {
		return 0, fmt.Errorf("no even numbers in range")
	}

	count := (max-min)/2 + 1
	idx, err := common.RandomInt(count)
	if err != nil {
		return 0, err
	}

	return min + (idx * 2), nil
}

func generateOddNumber(min, max int64) (int64, error) {
	if min%2 == 0 {
		min++
	}
	if max%2 == 0 {
		max--
	}

	if min > max {
		return 0, fmt.Errorf("no odd numbers in range")
	}

	count := (max-min)/2 + 1
	idx, err := common.RandomInt(count)
	if err != nil {
		return 0, err
	}

	return min + (idx * 2), nil
}
