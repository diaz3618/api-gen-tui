# Vault server configuration for vk local development
# Storage: file backend — data persists across container restarts
# ⚠️  This is a LOCAL ONLY configuration — not suitable for production

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = "true"
}

# Disable mlock — required in Docker containers without privileged mode
disable_mlock = true

# API address as seen from inside the container
api_addr = "http://0.0.0.0:8200"

# UI is disabled — vk is a CLI tool
ui = false
