class VkError(Exception):
    """Base exception for all vk errors."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:
        if self.hint:
            return f"{self.message}\nHint: {self.hint}"
        return self.message


class VaultNotRunning(VkError):
    def __init__(
        self, message: str = "Vault container is not running.", hint: str = "run `vk up`"
    ) -> None:
        super().__init__(message, hint=hint)


class VaultSealed(VkError):
    def __init__(self, message: str = "Vault is sealed.", hint: str = "run `vk status`") -> None:
        super().__init__(message, hint=hint)


class VaultForbidden(VkError):
    def __init__(
        self,
        message: str = "Vault authentication failed or token expired.",
        hint: str = "run `vk login`",
    ) -> None:
        super().__init__(message, hint=hint)


class VaultInvalidPath(VkError):
    def __init__(self, path: str = "", hint: str = "Check `vk list` for available paths.") -> None:
        message = f"Path does not exist in Vault: {path}" if path else "Invalid Vault path."
        super().__init__(message, hint=hint)


class VaultAlreadyInitialized(VkError):
    def __init__(
        self,
        message: str = "Vault is already initialized.",
        hint: str = "`vk vault-init` is idempotent — skipping re-initialization.",
    ) -> None:
        super().__init__(message, hint=hint)


class GeneratorError(VkError):
    pass
