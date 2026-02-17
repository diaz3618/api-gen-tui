package network

import (
	"strings"

	"github.com/google/uuid"
)

type UUIDOptions struct {
	Version   int
	Hyphens   bool
	Uppercase bool
	Namespace string // For V3, V5
	Name      string // For V3, V5
}

func GenerateUUID(opts UUIDOptions) (string, error) {
	var id uuid.UUID
	var err error

	switch opts.Version {
	case 1:
		id, err = uuid.NewUUID()
	case 3:
		ns := uuid.NameSpaceDNS // Default
		if opts.Namespace != "" {
			parsed, pErr := uuid.Parse(opts.Namespace)
			if pErr == nil {
				ns = parsed
			}
		}
		id = uuid.NewMD5(ns, []byte(opts.Name))
	case 4:
		id, err = uuid.NewRandom()
	case 5:
		ns := uuid.NameSpaceDNS // Default
		if opts.Namespace != "" {
			parsed, pErr := uuid.Parse(opts.Namespace)
			if pErr == nil {
				ns = parsed
			}
		}
		id = uuid.NewSHA1(ns, []byte(opts.Name))
	case 7:
		id, err = uuid.NewV7()
	default:
		id, err = uuid.NewRandom() // Default to v4
	}

	if err != nil {
		return "", err
	}

	s := id.String()
	if !opts.Hyphens {
		s = strings.ReplaceAll(s, "-", "")
	}
	if opts.Uppercase {
		s = strings.ToUpper(s)
	}

	return s, nil
}
