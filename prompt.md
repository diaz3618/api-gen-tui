Build a small, provider-independent local project that deploys HashiCorp Vault in Docker with persistent storage and provides a simple CLI/REPL for generating and storing API keys/tokens.

Goals
- Run Vault locally in Docker Compose.
- Persist Vault data across restarts with Docker volumes.
- Use a `.env` file for local operator credentials and configuration for ease of use.
- Provide a lightweight CLI and optional REPL that can:
  - initialize/unseal Vault if needed
  - log in
  - create, read, list, update, and delete stored secrets
  - generate API keys/tokens locally or through Vault-backed randomness/policies
  - support prefixes and flexible output options
  - store generated values in Vault under user-chosen paths
- Keep the codebase small and maintainable. Favor a compact Python or Node.js implementation with minimal dependencies.
- Do not build a huge web app. This is a local operator tool.

Important constraints
- Use Docker Compose.
- Use persistent named volumes or bind mounts for Vault storage.
- Use a `.env` file for easy local configuration, but do not hardcode secrets in source.
- Include a `.env.example`.
- Include a `README.md` with setup and usage.
- Include a `Makefile` or simple task runner commands for common workflows.
- Prefer a smooth local developer experience.

Vault requirements
- Use the official HashiCorp Vault image.
- Configure Vault in dev-safe local mode suitable for a single-user local environment, but with persistent storage.
- If using file storage, ensure it persists.
- Expose Vault on a configurable port.
- Enable KV v2 for secret storage.
- Use AppRole or token auth for the management tool if that makes sense locally, but keep setup simple.
- The tool should be able to authenticate using credentials/config from `.env`.
- The project should clearly separate local convenience from production guidance. Add comments that this setup is for local/private use, not hardened production.

API key/token generator requirements
Implement a generator module with rich options. It should support:
- prefix, suffix
- total length and random-part length
- output encodings and formats where feasible:
  - hex
  - base64
  - base64url
  - base32
  - alphanumeric
  - custom alphabet
  - uuid / uuid4
  - ulid if easy to support
  - url-safe token
- optional separators and grouping, for example `sk_live_xxxx_yyyy`
- uppercase/lowercase toggles where relevant
- ambiguity filters, for example excluding `0/O` and `1/l/I`
- required character classes where relevant:
  - min uppercase
  - min lowercase
  - min digits
  - min symbols
- checksum support only if trivial; otherwise skip
- generate one or many keys in a batch
- preview entropy estimate if easy to provide
- validate requested options and fail clearly on impossible combinations

Storage behavior
- The tool should support:
  - generate only
  - generate and store in Vault
  - store an externally supplied token in Vault
  - retrieve secret by path/key
  - list secrets under a path
  - delete secret
- Store metadata with each generated key:
  - created_at
  - format/type
  - prefix
  - total_length
  - generator options used
  - optional notes/tags
- Support a simple secret path convention like:
  - `kv/api-keys/<service>/<name>`
- Make the path configurable.

CLI/REPL requirements
Create a CLI, and if easy, an interactive REPL shell.
Suggested commands:
- `init`
- `up`
- `down`
- `status`
- `vault-init`
- `login`
- `generate`
- `store`
- `get`
- `list`
- `delete`
- `export`
- `policy`
- `shell` or `repl`

Example desired UX
- `tool up`
- `tool vault-init`
- `tool login`
- `tool generate --type base64url --length 48 --prefix sk_live_ --store kv/api-keys/stripe/default`
- `tool generate --type uuid --prefix dev_`
- `tool get kv/api-keys/stripe/default`
- `tool list kv/api-keys/stripe`
- `tool repl`

Implementation preferences
- Prefer Python 3.12 with:
  - `typer` or `click` for CLI
  - `rich` for output
  - `python-dotenv` for `.env`
  - `hvac` for Vault
- Or Go since vault is written in Go and it performs better than Python.
- Keep the code organized but small.
- Add type hints where practical.
- Add clear error messages.

Project deliverables
Create all needed files, including:
- `docker-compose.yml`
- Vault config file if needed
- application source code
- `.env.example`
- `.gitignore`
- `README.md`
- `Makefile`
- minimal tests for the generator logic
- sample commands or bootstrap script

Security and usability notes
- Make `.env.example` safe and omit real secrets.
- Ensure `.env` is gitignored.
- Explain which values the user must fill in after first run, especially unseal key/root token if applicable.
- Prefer not to require manual raw curl commands unless necessary.
- Make startup idempotent where possible.
- If initialization/unsealing must happen once, script it carefully and document it.
- For local ease of use, it is acceptable to store non-production local operator credentials in `.env`, but call out the tradeoff.

Nice-to-have
- Ability to create Vault password policies from generator presets when useful.
- Export generated keys as JSON.
- Copy-to-clipboard helper if easy.
- Batch generation from a CSV or JSON file if easy, but only if it doesn’t bloat the project.

Output requirements
- First, briefly explain the architecture and design choices.
- Then create the full project files.
- Show the exact file tree.
- Include all source code, not placeholders.
- Include commands to run:
  - initial setup
  - starting Vault
  - initializing Vault
  - logging in
  - generating and storing a key
- Keep the solution compact and practical, not enterprise-heavy.
