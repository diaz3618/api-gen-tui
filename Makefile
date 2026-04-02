# vk — Local Vault API Key Manager
# Requires: Docker, Docker Compose v2, uv

.PHONY: up down init status test install clean help

# Default: show help
.DEFAULT_GOAL := help

COMPOSE = docker compose -f docker/docker-compose.yml
VAULT_ADDR ?= http://127.0.0.1:8200

## Start Vault container (auto-unseals if .env has VAULT_UNSEAL_KEY)
up:
	uv run vk up

## Stop Vault container
down:
	uv run vk down

## Initialize Vault on first run (writes unseal key + root token to .env)
init:
	uv run vk vault-init

## Show Vault status panel
status:
	uv run vk status

## Run unit tests
test:
	uv run pytest tests/ -v
	# NOTE: do NOT run `python -m pytest` directly — system Python may lack vk deps.
	# Use `uv run pytest` (this target) or `.venv/bin/python -m pytest` explicitly.

## Install vk in development mode (creates .venv, installs deps)
install:
	uv sync && uv pip install -e .

## Remove build artifacts and .venv
clean:
	rm -rf .venv dist *.egg-info __pycache__ .pytest_cache .ruff_cache

## Show this help message
help:
	@grep -E '^##' Makefile | sed 's/## //'
