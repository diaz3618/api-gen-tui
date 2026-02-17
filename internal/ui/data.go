package ui

import "github.com/charmbracelet/bubbles/list"

// CategoryItem implements list.Item
type CategoryItem struct {
	TitleStr, DescStr string
	ID                string
}

func (i CategoryItem) Title() string       { return i.TitleStr }
func (i CategoryItem) Description() string { return i.DescStr }
func (i CategoryItem) FilterValue() string { return i.TitleStr }

// GeneratorDefinition implements list.Item
type GeneratorDefinition struct {
	TitleStr, DescStr string
	ID                string // Must match key in GeneratorRegistry
}

func (i GeneratorDefinition) Title() string       { return i.TitleStr }
func (i GeneratorDefinition) Description() string { return i.DescStr }
func (i GeneratorDefinition) FilterValue() string { return i.TitleStr }

var Categories = []list.Item{
	CategoryItem{TitleStr: "Authentication", DescStr: "passwords, api keys, tokens", ID: "authentication"},
	CategoryItem{TitleStr: "Tokens & Access", DescStr: "bearer, jwt, oauth tokens", ID: "tokens"},
	CategoryItem{TitleStr: "Encryption", DescStr: "symmetric, asymmetric keys", ID: "encryption"},
	CategoryItem{TitleStr: "Hashing & Security", DescStr: "bcrypt, salts, hashes", ID: "hashing"},
	CategoryItem{TitleStr: "SSH & Keys", DescStr: "ssh keys, framework keys", ID: "keys"},
	CategoryItem{TitleStr: "Identifiers", DescStr: "uuids, unique ids", ID: "identifiers"},
	CategoryItem{TitleStr: "Encoding", DescStr: "base64, encoding utilities", ID: "encoding"},
}
