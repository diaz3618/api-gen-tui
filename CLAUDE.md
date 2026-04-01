<!-- GSD:project-start source:PROJECT.md -->
## Project

**vk — Local Vault API Key Manager**

`vk` is a local operator CLI tool (Python 3.12) that runs HashiCorp Vault in Docker, manages
persistent secret storage via KV v2, and provides a rich API key/token generator with flexible
encoding, prefix, length, and character-class options. It lives in the same repo as `api-gen-tui`
(Go TUI), which will eventually integrate with Vault as a frontend.

**Core Value:** A developer can generate a properly-formatted API key and store it in a locally-running Vault
instance with a single command — no manual curl, no raw token juggling, no leaving keys in
shell history.

### Constraints

- **Runtime**: Docker + Docker Compose required on developer machine
- **Language**: Python 3.12 — typer (CLI), rich (output), hvac (Vault), python-dotenv (.env), pyperclip (clipboard)
- **Vault image**: Official HashiCorp `hashicorp/vault` image, KV v2 enabled
- **Scope**: Local operator tool — small, maintainable, no enterprise patterns
- **No hardcoded secrets**: All credentials via `.env`; `.env` gitignored; `.env.example` committed
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Go 1.25.5 — entire codebase; declared in `go.mod` line 3
- None
## Runtime
- Go runtime (no external runtime dependency; compiles to a static native binary)
- Binary name: `api-gen-tui`
- Supports cross-compilation for: linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64
- Go Modules (`go mod`)
- Lockfile: `go.sum` present (66 lines)
## Frameworks
- `github.com/charmbracelet/bubbletea` v1.3.10 — Elm-architecture TUI framework; all application state and event loop lives here
- `github.com/charmbracelet/bubbles` v0.21.1 — Pre-built Bubble Tea components (`list`, `viewport`, `textinput`)
- `github.com/charmbracelet/lipgloss` v1.1.0 — Terminal styling and layout (colours, borders, alignment)
- None declared in `go.mod`; no test files detected in the repository
- Standard `go build` toolchain
- `golangci-lint` (via GitHub Actions, not a `go.mod` dependency) — linting
- `gofmt` — formatting enforced in CI
## Key Dependencies
- `github.com/charmbracelet/bubbletea` v1.3.10 — application framework; removing it would require a full rewrite
- `github.com/charmbracelet/bubbles` v0.21.1 — `list.Model` and `viewport.Model` used throughout `internal/ui/`
- `github.com/charmbracelet/lipgloss` v1.1.0 — used in every UI file and in `internal/generator/security/encryption.go` for side-by-side key layout
- `github.com/google/uuid` v1.6.0 — UUID generation (v1, v3, v4, v5, v7) in `internal/generator/network/uuid.go`
- `golang.org/x/crypto` v0.47.0 — `bcrypt` (password hashing) and `ssh` (SSH key generation) in `internal/generator/security/crypto.go`
- `github.com/atotto/clipboard` v0.1.4 — clipboard support pulled in by `bubbles`
- `github.com/charmbracelet/colorprofile` v0.4.1 — terminal colour profile detection
- `github.com/charmbracelet/x/ansi`, `cellbuf`, `term` — low-level terminal helpers for bubbletea
- `github.com/muesli/termenv` v0.16.0 — terminal environment detection
- `github.com/sahilm/fuzzy` v0.1.1 — fuzzy filtering inside `bubbles/list`
- `golang.org/x/sys` v0.40.0 — OS-level terminal calls
- `golang.org/x/text` v0.33.0 — Unicode/text utilities
## Configuration
- No environment variables required; the binary is fully self-contained
- No `.env` files present or referenced
- `go.mod` / `go.sum` — dependency pinning
- CI build flags: `-ldflags="-s -w"` (strip debug symbols) used in release workflow (`release.yml`)
- No `Makefile`, `Dockerfile`, or other build wrappers
## Platform Requirements
- Go ≥ 1.23 (CI matrix: 1.23, 1.24, 1.25)
- A POSIX-compatible terminal that supports ANSI escape codes and alt-screen mode
- Distributed as a pre-compiled binary; no Go installation needed at runtime
- Targets: Linux (amd64/arm64), macOS (amd64/arm64), Windows (amd64)
- Release pipeline: GitHub Actions → `softprops/action-gh-release@v1` triggered by `v*.*.*` tags
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Snake_case is not used; files are named in flat lowercase: `password.go`, `apikey.go`, `tokens.go`, `crypto.go`
- UI component files match their exported type: `header.go` → `Header`, `breadcrumb.go` → `Breadcrumb`, `form.go` → `FormModel`
- No `_test.go` files exist anywhere in the project (see Testing doc)
- Exported functions use PascalCase: `GeneratePassword`, `GenerateAPIKey`, `GenerateToken`, `GenerateUUID`
- Unexported helpers use camelCase and often a `generate` prefix: `generateSinglePassword`, `generateBearerToken`, `generateSymmetricKey`
- Constructor functions follow the `New*` convention: `NewModel()`, `NewHeader()`, `NewBreadcrumb()`, `NewForm()`, `NewTextField()`, `NewToggleField()`
- Render methods follow the `.Render()` pattern on UI components
- camelCase throughout: `charSet`, `keyBytes`, `privateKeyPEM`, `pageVp`
- Short loop variables are single-letter: `i`, `b`, `v`, `f`
- Boolean flags use `Include*` prefix in option structs: `IncludeUppercase`, `IncludeLowercase`
- Structs for options use `*Options` suffix: `PasswordOptions`, `APIKeyOptions`, `TokenOptions`, `UUIDOptions`, `Base64Options`
- Enum-like string types are declared as `type Foo string`: `TokenType`, `APIKeyFormat`, `EncryptionType`, `KeyFormat`, `NumberType`, `FieldType`
- Constants for enum values use `PascalCase` (not `SCREAMING_SNAKE_CASE`): `TokenTypeAPIToken`, `FormatAlphaNumeric`, `EncryptionSymmetric`
- UI state uses `type State int` with iota: `StateCategoryList`, `StateGeneratorList`, `StateForm`
- BubbleTea message types use `Msg` suffix: `FormSubmittedMsg`
- BubbleTea model fields follow the framework convention: `Init()`, `Update()`, `View()`
- One-word, lowercase package names: `security`, `network`, `encoding`, `common`, `components`, `ui`, `math`
- No underscores or mixed case in package names
## Code Style
- `gofmt -s` is enforced in CI via `.github/workflows/ci.yml` — the build fails if any file is not formatted
- Standard Go formatting applies: tabs for indentation, no trailing spaces
- `hash.go` has non-standard indentation (missing leading tabs) — this appears to be a pre-existing formatting issue
- `golangci-lint` runs in CI via `.github/workflows/lint.yml` with `--timeout=5m`
- No local `.golangci.yml` config file exists — uses golangci-lint defaults
- `go vet ./...` runs as part of CI test job
- Security scanning: `govulncheck`, `gosec` (SARIF output), and `nancy` (dependency check) all run in CI
- CodeQL analysis runs on push/PR and weekly schedule
## Import Organization
- `tea "github.com/charmbracelet/bubbletea"` — alias used consistently everywhere BubbleTea is imported
## Error Handling
- Simple messages use `errors.New("...")` (in `password.go`)
- Formatted messages use `fmt.Errorf("...")` (everywhere else)
- Wrapped errors use `fmt.Errorf("...: %w", err)` — example from `crypto.go`:
- Sentinel error strings are lowercase without periods (Go convention): `"length must be positive"`, `"API key length must not exceed 512 characters"`
## Logging
## Comments
- Inline comments explain non-obvious logic: `// Base64 is 4 chars for every 3 bytes.`, `// Similar characters that look similar`
- Section comments in large files group related code: `// Authentication`, `// Encryption`, `// SSH & Keys`
- Function-level doc comments appear only on exported functions in `common/random.go` and `encoding/base64.go`:
- Most exported functions in `security/` and other packages lack doc comments — this is inconsistent
## Function Design
## Module Design
- `security/password.go` — password generation only
- `security/apikey.go` — API key generation only
- `security/tokens.go` — token generation only
- `common/random.go` — shared random primitives
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Pure TUI — no HTTP server, no network interface, no daemon. Runs entirely in the terminal.
- Strictly unidirectional data flow: keyboard input → `Update()` → state mutation → `View()` → rendered string.
- Two distinct internal layers: a UI layer (`internal/ui`) and a generator layer (`internal/generator`). The UI layer calls into the generator layer; the generator layer has no knowledge of the UI.
- All randomness is cryptographically secure via `crypto/rand`. The `math/number.go` package uses `math/rand` for floating-point decimals only; everything else uses `crypto/rand`.
## Layers
### 1. Entry Point (`main.go`)
- **Purpose:** Bootstraps the Bubble Tea program.
- **Location:** `main.go`
- **Responsibilities:**
- **Depends on:** `internal/ui`, `github.com/charmbracelet/bubbletea`
### 2. UI Layer (`internal/ui`)
- **Purpose:** Manages all application state and the entire TUI rendering pipeline.
- **Location:** `internal/ui/`
- **Contains:**
- **Depends on:** `internal/ui/components`, `internal/generator/*`
- **Used by:** `main.go`
### 3. UI Components (`internal/ui/components`)
- **Purpose:** Reusable, stateful sub-models and shared styling constants.
- **Location:** `internal/ui/components/`
- **Contains:**
- **Depends on:** `github.com/charmbracelet/bubbles/textinput`, `github.com/charmbracelet/lipgloss`
- **Used by:** `internal/ui`
### 4. Generator Layer (`internal/generator`)
- **Purpose:** Pure business logic — generates cryptographic artifacts. Zero UI dependencies (exception: `encryption.go` imports `lipgloss` solely for horizontal key layout formatting).
- **Location:** `internal/generator/`
- **Sub-packages:**
- **Depends on:** `crypto/rand`, `golang.org/x/crypto`, `github.com/google/uuid`, `internal/generator/common`
- **Used by:** `internal/ui` (via `generators.go` closures in `GeneratorRegistry`)
## Navigation State Machine
```
```
- **`esc`** from any state decrements `state` by 1 (back navigation); `esc` at `StateCategoryList` quits.
- **`q` / `ctrl+c`** quits from any state.
- Breadcrumb is pushed on forward navigation and popped on `esc`.
## Data Flow
### User Input → Generated Output
### View Rendering Stack
```
```
## Key Abstractions
### `GeneratorConfig` (`internal/ui/generators.go`)
```go
```
- All generators are registered at package init time in `GeneratorRegistry map[string]GeneratorConfig`.
- The `Generate` function receives a weakly typed `map[string]any`; callers type-assert values (e.g., `v["length"].(int)`).
- Adding a new generator requires only appending to `GeneratorRegistry` in `generators.go`.
### `FormModel` (`internal/ui/components/form.go`)
- Implements `tea.Model` interface (partially — no `Init()` return Cmd).
- Maintains `[]Field` + `Focus int` cursor.
- Field types: `TypeTextInput`, `TypeIntInput`, `TypeSelect`, `TypeToggle`, `TypeTextArea`, `TypeRange`.
- On Submit button `enter`: emits `FormSubmittedMsg` via a `tea.Cmd` closure.
### `Field` (`internal/ui/components/form.go`)
- Tagged union via `FieldType` enum.
- Text-backed fields embed a `textinput.Model`; toggle/select fields store their state directly in `Value any`.
## Entry Points and Lifecycle
## Error Handling
- Generator functions return `(string, error)`. On error, `MainModel` stores `err` and `View()` renders it with `ErrorStyle`.
- `main.go` is the only place calling `os.Exit(1)` — only if `tea.Program.Run()` itself fails (catastrophic startup failure).
- Generator layer validates all inputs (ranges, required fields) and returns descriptive `fmt.Errorf` errors.
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
