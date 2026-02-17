# Quick Reference Card

## Build & Run

```bash
# Build the application
go build -o api-gen-tui .

# Run it
./api-gen-tui

# Or run directly without building
go run .
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate up/down |
| `Tab` | Next form field |
| `Enter` | Select / Generate |
| `Space` | Toggle on/off |
| `Esc` | Go back |
| `q` | Quit |
| `Ctrl+C` | Force quit |

## Important Files

- `README.md` - Full documentation for beginners
- `GENERATORS.md` - Available generator types
- `main.go` - Application entry point
- `go.mod` - Dependencies

## Available Generators

### Authentication & Access

1. **Password Generator**
   - Length: 4-128 chars
   - Count: 1-25
   - Options: uppercase, lowercase, numbers, symbols
   - Exclude similar/specific chars

2. **API Key Generator**
   - Formats: alphanumeric, hex, base64, base64url, uuid, numeric
   - Length: 16-128
   - Custom prefix support

3. **API Token Generator**
   - Base64url encoded tokens
   - Custom prefix support

4. **Bearer Token Generator**
   - Hex-encoded bearer tokens
   - OAuth/API authentication

5. **JWT Token Generator**
   - Simulated JWT structure (header.payload.signature)
   - Configurable payload length

6. **OAuth Token Generator**
   - Tokens with timestamp
   - Custom prefix support

### Cryptography & Security

7. **Encryption Key Generator**
   - Symmetric: AES keys (16/24/32 bytes)
   - Asymmetric: RSA keys (2048/4096 bits)
   - Formats: hex, base64, PEM

2. **SSH Key Generator**
   - RSA key pairs
   - 2048 or 4096 bit keys

3. **Laravel Key Generator**
   - Base64-encoded 32-byte keys
   - Laravel APP_KEY format

4. **Webhook Secret Generator**
    - Secure webhook signing secrets
    - Custom prefix support

5. **Salt Generator**
    - Cryptographic salts
    - 16-64 bytes

6. **Hash Generator**
    - Random data hashes
    - Multiple algorithms

7. **Bcrypt Hash Generator**
    - Password hashing with bcrypt
    - Configurable cost factor (4-15)

### Identifiers & Encoding

14. **UUID Generator**
    - Versions: v1, v3, v4, v5, v7
    - Hyphenated format option
    - Uppercase option
    - Namespace+name for v3/v5

2. **Base64 Encoder**
    - Encode random data or text
    - Multiple encodings: standard, URL-safe, raw

3. **Base64 String Generator**
    - Random base64 strings
    - URL-safe option

## Troubleshooting

```bash
# "go: command not found"
sudo dnf install golang  # Fedora/RHEL
sudo apt install golang-go  # Ubuntu/Debian
brew install go  # macOS

# Download dependencies
go mod download

# Clean build
go clean -modcache
go mod download
go build -o api-gen-tui .

# Make executable
chmod +x api-gen-tui
```

## Project Structure

```
api-gen-tui/
├── main.go              - Entry point
├── internal/
│   ├── generator/       - Generation logic
│   │   ├── security/    - Password, API keys
│   │   ├── network/     - UUIDs
│   │   └── math/        - Numbers
│   └── ui/              - User interface
│       ├── model.go     - Main TUI model
│       └── components/  - UI components
```

## Tips

1. **Generate Multiple**: Use the count field to generate many items at once
2. **Copy Results**: Use your terminal's copy function (usually mouse select or Ctrl+Shift+C)
3. **Quick Testing**: Use `go run .` during development to skip building
4. **Terminal Size**: Resize terminal if UI looks cramped (minimum 80x24)

## Learn More

- Full guide: [README.md](README.md)
- Generators list: [GENERATORS_LIST.md](GENERATORS_LIST.md)
