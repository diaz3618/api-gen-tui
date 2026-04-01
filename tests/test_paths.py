import pytest
from vk.vault.paths import PathBuilder, canonicalize_path


def test_path_builder_default_prefix():
    pb = PathBuilder()
    assert pb.build("stripe", "prod") == "api-keys/stripe/prod"


def test_path_builder_custom_prefix():
    pb = PathBuilder(prefix="secrets")
    assert pb.build("stripe", "prod") == "secrets/stripe/prod"


def test_path_builder_empty_prefix():
    pb = PathBuilder()
    assert pb.build("stripe", "prod", prefix="") == "stripe/prod"


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
