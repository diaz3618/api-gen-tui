# API Generator TUI

A Terminal User Interface (TUI) app for generating various types of random data. Built with Go and the Bubbletea framework.

## What is is?

A command-line application that  generates random data directly in your terminal. It provides an interactive, keyboard-driven interface with a modern TUI for generating:

- **Authentication & Access**: Passwords, API Keys, API Tokens, Bearer Tokens, JWT Tokens, OAuth Tokens
- **Cryptography & Security**: Encryption Keys (symmetric/asymmetric), SSH Keys, Laravel Keys, Webhook Secrets, Salts, Hashes, Bcrypt Hashes
- **Identifiers & Encoding**: UUIDs (v1, v3, v4, v5, v7), Base64 encoding

## Features

- **Cryptographically Secure** - Uses crypto/rand for all random generation
- **Fast & Lightweight** - Native Go binary with no runtime dependencies
- **Keyboard Navigation** - Keyboard-driven interface

## Prerequisites

Before you begin, make sure you have **Go** installed.

### Installing Go

#### On Linux (Fedora/RHEL)

```bash
sudo dnf install golang
```

#### On Linux (Ubuntu/Debian)

```bash
sudo apt install golang-go
```

#### On macOS

```bash
brew install go
```

#### On Windows

Download and install from [golang.org/dl](https://golang.org/dl/)

### Verify Installation

```bash
go version
```

You should see output like: `go version go1.25.5 linux/amd64`

## Installation

### 1. Clone or Download

If you have this project already, navigate to the project directory:

```bash
cd /path/to/api-gen-tui
```

If you need to clone it:

```bash
git clone https://github.com/diaz3618/api-gen-tui
cd api-gen-tui
```

### 2. Build the Application

```bash
go build -o api-gen-tui .
```

This command:

- `go build` - Compiles your Go code
- `-o api-gen-tui` - Names the output binary "api-gen-tui"
- `.` - Uses the current directory

After running this, you'll have an executable file called `api-gen-tui` in your current directory.

## Running the Application

### Option 1: Run the Binary (Recommended)

After building:

```bash
./api-gen-tui
```

### Option 2: Run Directly (Without Building)

You can also run without building first:

```bash
go run .
```

This is useful during development but slower than running the compiled binary.

## Building from Source

### Development Build

For quick testing during development:

```bash
go run .
```

### Production Build

For better performance:

```bash
go build -o api-gen-tui .
```

### Optimized Build (Smaller Binary)

```bash
go build -ldflags="-s -w" -o api-gen-tui .
```

This strips debug information, making the binary smaller.

### Cross-Platform Build

Build for different operating systems:

```bash
# For Windows
GOOS=windows GOARCH=amd64 go build -o api-gen-tui.exe .

# For macOS
GOOS=darwin GOARCH=amd64 go build -o api-gen-tui-mac .

# For Linux
GOOS=linux GOARCH=amd64 go build -o api-gen-tui-linux .
```

## Dependencies

This project uses the following Go libraries:

- **github.com/charmbracelet/bubbletea** (v1.3.10) - TUI framework
- **github.com/charmbracelet/bubbles** (v0.21.1) - UI components
- **github.com/charmbracelet/lipgloss** (v1.1.0) - Terminal styling
- **github.com/google/uuid** (v1.6.0) - UUID generation

## License

See: [LICENSE](LICENSE)
