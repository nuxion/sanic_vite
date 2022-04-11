from pathlib import Path

import click
from changeme.init_script import init
from rich.console import Console
from rich.panel import Panel


@click.command()
@click.option(
    "--with-vite",
    "-V",
    is_flag=True,
    default=True,
    help="Create configuration for vite",
)
@click.argument("base_path")
def startproject(base_path, with_vite):

    root = Path(base_path)
    console = Console()
    p = Panel.fit(
        "[bold magenta]:smile_cat: Hello and welcome to "
        " Sanic Builder [/bold magenta]",
        border_style="red",
    )
    console.print(p)
    console.print(
        f"\n Starting project at [bold blue underline]{root.resolve()}[/bold blue underline]\n"
    )

    init(base_path, with_vite)
