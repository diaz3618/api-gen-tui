import typer
from vk.cli import infra, keys

app = typer.Typer(
    name="vk",
    help="Local Vault API key manager.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
)

# Register infrastructure commands
for cmd in [infra.up, infra.down, infra.status, infra.vault_init, infra.login]:
    app.command()(cmd)

# Register key management commands
for cmd in [keys.generate, keys.store, keys.get, keys.list_keys, keys.delete, keys.export]:
    app.command()(cmd)
