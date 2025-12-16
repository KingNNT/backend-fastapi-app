"""CLI entry point for database operations."""

import typer

from app.infrastructure.cli.commands import seed

app = typer.Typer(
    name="cli",
    help="Database CLI for backend-fastapi-app",
    add_completion=False,
)

# Register command groups
app.add_typer(seed.app, name="db", help="Database seeding commands")


@app.callback()
def main() -> None:
    """Database CLI for backend-fastapi-app.

    Use 'db' subcommand for seeding operations.
    """
    pass


if __name__ == "__main__":
    app()
