import typer
from vk.cli import infra, keys

app = typer.Typer(
    name="vk",
    help="Local Vault API key manager.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Infrastructure commands — explicit names prevent auto-conversion surprises
app.command()(infra.up)
app.command()(infra.down)
app.command()(infra.status)
app.command(name="vault-init")(infra.vault_init)  # explicit: underscore→hyphen made safe
app.command()(infra.login)

# Key management commands
app.command()(keys.generate)
app.command()(keys.store)
app.command()(keys.get)
app.command(name="list")(keys.list_keys)  # FIX: was 'list-keys', D-03 requires 'list'
app.command()(keys.delete)
app.command()(keys.export)

# UX commands (Phase 5) — imported after app definition to avoid circular imports
from vk.cli.repl import repl  # noqa: E402
from vk.cli.policy import policy  # noqa: E402

app.command()(repl)
app.command()(policy)
