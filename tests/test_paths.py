import pytest
from vk.errors import VaultInvalidPath
from vk.vault.paths import canonicalize_path


def test_canonicalize_path_with_mount():
    mount, path = canonicalize_path("kv/api-keys/stripe/prod")
    assert mount == "kv"
    assert path == "api-keys/stripe/prod"


def test_canonicalize_path_strips_leading_slash():
    mount, path = canonicalize_path("/api-keys/stripe/prod")
    assert path == "api-keys/stripe/prod"
    assert not path.startswith("/")


def test_canonicalize_path_strips_trailing_slash():
    mount, path = canonicalize_path("api-keys/stripe/prod/")
    assert not path.endswith("/")


def test_canonicalize_path_no_mount_uses_default():
    mount, path = canonicalize_path("api-keys/stripe/prod")
    assert mount == "kv"


def test_canonicalize_path_bare_mount_raises():
    """TD-4: bare mount name alone must raise VaultInvalidPath, not return ('kv', 'kv')."""
    with pytest.raises(VaultInvalidPath):
        canonicalize_path("kv")


def test_canonicalize_path_empty_raises():
    """Empty path must raise VaultInvalidPath."""
    with pytest.raises(VaultInvalidPath):
        canonicalize_path("")


def test_canonicalize_path_secret_mount():
    mount, path = canonicalize_path("secret/my-key/prod")
    assert mount == "secret"
    assert path == "my-key/prod"


def test_canonicalize_path_bare_secret_mount_raises():
    with pytest.raises(VaultInvalidPath):
        canonicalize_path("secret")
