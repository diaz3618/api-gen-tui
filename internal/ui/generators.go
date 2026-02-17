package ui

import (
	"strconv"

	"github.com/diaz3618/api-gen-tui/internal/generator/encoding"
	"github.com/diaz3618/api-gen-tui/internal/generator/network"
	"github.com/diaz3618/api-gen-tui/internal/generator/security"
	"github.com/diaz3618/api-gen-tui/internal/ui/components"
)

type GeneratorConfig struct {
	Title       string
	Description string
	Category    string
	BuildForm   func() components.FormModel
	Generate    func(values map[string]any) (string, error)
}

var GeneratorRegistry = map[string]GeneratorConfig{
	// Authentication
	"password": {
		Title:       "Password Generator",
		Description: "Generate cryptographically secure passwords (4-128 characters, up to 25 at once)",
		Category:    "authentication",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length", 4, 128, 16),
				components.NewRangeField("count", "Count", 1, 25, 1),
				components.NewToggleFieldWithHelp("upper", "Uppercase (A-Z)", true, "Include uppercase letters"),
				components.NewToggleFieldWithHelp("lower", "Lowercase (a-z)", true, "Include lowercase letters"),
				components.NewToggleFieldWithHelp("number", "Numbers (0-9)", true, "Include numeric digits"),
				components.NewToggleFieldWithHelp("symbol", "Symbols (!@#$...)", true, "Include special symbols"),
				components.NewToggleFieldWithHelp("excludeSimilar", "Exclude Similar Characters", false, "Remove i,l,1,L,o,0,O"),
				components.NewTextFieldWithHelp("excludeChars", "Exclude Specific Chars", "", "", "Characters to exclude (e.g., @#$)"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			c := v["count"].(int)
			excludeChars := v["excludeChars"].(string)

			return security.GeneratePassword(security.PasswordOptions{
				Length:           l,
				Count:            c,
				IncludeUppercase: v["upper"].(bool),
				IncludeLowercase: v["lower"].(bool),
				IncludeNumbers:   v["number"].(bool),
				IncludeSymbols:   v["symbol"].(bool),
				ExcludeSimilar:   v["excludeSimilar"].(bool),
				ExcludeChars:     excludeChars,
			})
		},
	},
	"apikey": {
		Title:       "API Key Generator",
		Description: "Generate secure API keys with custom formats and prefixes",
		Category:    "authentication",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewSelectFieldWithHelp("format", "Format",
					[]string{"alphanumeric", "hex", "base64", "base64url", "uuid", "numeric"},
					0, "Choose the encoding format"),
				components.NewRangeField("length", "Length", 16, 128, 32),
				components.NewTextFieldWithHelp("prefix", "Prefix (optional)", "", "sk_", "e.g., sk_, pk_, api_"),
				components.NewToggleFieldWithHelp("upper", "Uppercase", false, "For hex format only"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return security.GenerateAPIKey(security.APIKeyOptions{
				Format:    security.APIKeyFormat(v["format"].(string)),
				Length:    l,
				Prefix:    v["prefix"].(string),
				Uppercase: v["upper"].(bool),
			})
		},
	},
	"apitoken": {
		Title:       "API Token Generator",
		Description: "Generate API tokens with base64url encoding",
		Category:    "tokens",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length", 16, 128, 32),
				components.NewTextFieldWithHelp("prefix", "Prefix (optional)", "", "token_", "e.g., token_, api_"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return security.GenerateToken(security.TokenOptions{
				Type:   security.TokenTypeAPIToken,
				Length: l,
				Prefix: v["prefix"].(string),
			})
		},
	},
	"bearertoken": {
		Title:       "Bearer Token Generator",
		Description: "Generate bearer tokens for OAuth/API authentication",
		Category:    "tokens",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length", 32, 128, 64),
				components.NewToggleFieldWithHelp("upper", "Uppercase", false, "Use uppercase hex characters"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return security.GenerateToken(security.TokenOptions{
				Type:      security.TokenTypeBearer,
				Length:    l,
				Uppercase: v["upper"].(bool),
			})
		},
	},
	"jwttoken": {
		Title:       "JWT Token Generator",
		Description: "Generate JSON Web Token (JWT) structure",
		Category:    "tokens",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("payloadLength", "Payload Length", 32, 256, 64),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["payloadLength"].(int)
			return security.GenerateToken(security.TokenOptions{
				Type:   security.TokenTypeJWT,
				Length: l,
			})
		},
	},
	"oauthtoken": {
		Title:       "OAuth Token Generator",
		Description: "Generate OAuth access tokens with timestamp",
		Category:    "tokens",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length", 32, 128, 64),
				components.NewTextFieldWithHelp("prefix", "Prefix (optional)", "", "oauth_", "e.g., oauth_, access_"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return security.GenerateToken(security.TokenOptions{
				Type:   security.TokenTypeOAuth,
				Length: l,
				Prefix: v["prefix"].(string),
			})
		},
	},

	// Encryption
	"encryptionkey": {
		Title:       "Encryption Key Generator",
		Description: "Generate symmetric or asymmetric encryption keys",
		Category:    "encryption",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewSelectFieldWithHelp("type", "Key Type",
					[]string{"symmetric", "asymmetric"},
					0, "Symmetric (AES) or Asymmetric (RSA)"),
				components.NewSelectFieldWithHelp("size", "Key Size",
					[]string{"16", "24", "32", "2048", "4096"},
					2, "Bytes for symmetric (16/24/32), bits for asymmetric (2048/4096)"),
				components.NewSelectFieldWithHelp("format", "Format",
					[]string{"hex", "base64", "pem"},
					0, "Output format"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			size, _ := strconv.Atoi(v["size"].(string))
			return security.GenerateEncryptionKey(security.EncryptionKeyOptions{
				Type:    security.EncryptionType(v["type"].(string)),
				KeySize: size,
				Format:  security.KeyFormat(v["format"].(string)),
			})
		},
	},
	// SSH & Keys
	"sshkey": {
		Title:       "SSH Key Generator",
		Description: "Generate SSH RSA key pairs",
		Category:    "keys",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewSelectFieldWithHelp("keySize", "Key Size",
					[]string{"2048", "4096"},
					0, "RSA key size in bits"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			size, _ := strconv.Atoi(v["keySize"].(string))
			return security.GenerateSSHKey(size)
		},
	},
	"laravelkey": {
		Title:       "Laravel Key Generator",
		Description: "Generate Laravel application encryption key",
		Category:    "keys",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewTextFieldWithHelp("info", "Info", "", "Generates base64:xxxxx format", "32-byte key automatically generated"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			return security.GenerateLaravelKey()
		},
	},
	"webhooksecret": {
		Title:       "Webhook Secret Generator",
		Description: "Generate secure webhook signing secrets",
		Category:    "encryption",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length", 32, 128, 64),
				components.NewTextFieldWithHelp("prefix", "Prefix (optional)", "", "whsec_", "e.g., whsec_, webhook_"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return security.GenerateToken(security.TokenOptions{
				Type:   security.TokenTypeWebhook,
				Length: l,
				Prefix: v["prefix"].(string),
			})
		},
	},
	// Hashing & Security
	"salt": {
		Title:       "Cryptographic Salt Generator",
		Description: "Generate random salts for password hashing",
		Category:    "hashing",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length (bytes)", 16, 64, 32),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return security.GenerateSalt(l)
		},
	},
	"hash": {
		Title:       "Hash Generator",
		Description: "Generate cryptographic hashes of random data",
		Category:    "hashing",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewSelectFieldWithHelp("algorithm", "Algorithm",
					[]string{"sha256", "sha512", "sha1", "md5"},
					0, "Hash algorithm"),
				components.NewRangeField("inputLength", "Input Length", 16, 128, 32),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["inputLength"].(int)
			return security.GenerateHash(v["algorithm"].(string), l)
		},
	},
	"bcrypthash": {
		Title:       "Bcrypt Hash Generator",
		Description: "Generate bcrypt hashes for password storage",
		Category:    "hashing",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewTextFieldWithHelp("password", "Password", "", "mypassword", "Password to hash"),
				components.NewRangeField("cost", "Cost Factor", 4, 15, 10),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			password := v["password"].(string)
			if password == "" {
				password = "defaultpassword"
			}
			cost := v["cost"].(int)
			return security.GenerateBcryptHash(password, cost)
		},
	},

	// Identifiers
	"uuid": {
		Title:       "UUID Generator",
		Description: "Generate Universally Unique Identifiers (v1, v3, v4, v5, v7)",
		Category:    "identifiers",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewSelectFieldWithHelp("version", "Version",
					[]string{"1", "3", "4", "5", "7"},
					2, "v4: Random, v7: Time-ordered, v1: Time-based, v3/v5: Name-based"),
				components.NewToggleField("hyphens", "Include Hyphens", true),
				components.NewToggleField("upper", "Uppercase", false),
				components.NewTextFieldWithHelp("ns", "Namespace (v3/v5)", "", "DNS", "For v3/v5: UUID or DNS/URL/OID/X500"),
				components.NewTextFieldWithHelp("name", "Name (v3/v5)", "", "example.com", "For v3/v5: Name string"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			ver, _ := strconv.Atoi(v["version"].(string))
			return network.GenerateUUID(network.UUIDOptions{
				Version:   ver,
				Hyphens:   v["hyphens"].(bool),
				Uppercase: v["upper"].(bool),
				Namespace: v["ns"].(string),
				Name:      v["name"].(string),
			})
		},
	},
	// Encoding
	"base64": {
		Title:       "Base64 Encoder",
		Description: "Encode random data or text to Base64",
		Category:    "encoding",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewSelectFieldWithHelp("inputType", "Input Type",
					[]string{"random", "text"},
					0, "Random bytes or custom text"),
				components.NewTextFieldWithHelp("text", "Text Input", "", "Hello World", "Text to encode (if input type is text)"),
				components.NewRangeField("length", "Random Length", 16, 128, 32),
				components.NewSelectFieldWithHelp("encoding", "Encoding",
					[]string{"standard", "url", "raw", "rawurl"},
					0, "Standard, URL-safe, or raw (no padding)"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			text := v["text"].(string)
			return encoding.GenerateBase64(encoding.Base64Options{
				InputType: v["inputType"].(string),
				Input:     text,
				Length:    l,
				Encoding:  v["encoding"].(string),
				Padding:   true,
			})
		},
	},
	"base64string": {
		Title:       "Base64 String Generator",
		Description: "Generate random Base64 strings",
		Category:    "encoding",
		BuildForm: func() components.FormModel {
			return components.NewForm([]components.Field{
				components.NewRangeField("length", "Length (bytes)", 16, 128, 32),
				components.NewToggleFieldWithHelp("urlSafe", "URL-Safe", false, "Use URL-safe encoding (no padding)"),
			})
		},
		Generate: func(v map[string]any) (string, error) {
			l := v["length"].(int)
			return encoding.GenerateBase64String(l, v["urlSafe"].(bool))
		},
	},
}
