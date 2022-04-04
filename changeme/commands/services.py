import multiprocessing as mp
import os
import shutil
import sys
from pathlib import Path

import click
from changeme.utils import execute_cmd, mkdir_p
from rich.console import Console
from rich.prompt import Confirm
import subprocess

console = Console()


def run_sanic(app, **kwargs):
    app.run(**kwargs)


def run_vite():
    subprocess.run(["yarn", "dev"], check=True)


@click.command(name="web")
@click.option("--host", "-H", default="0.0.0.0", help="Listening Host")
@click.option("--port", "-p", default="8000", help="Listening Port")
@click.option("--workers", "-w", default=1, help="How many workers start?")
@click.option(
    "--services",
    "-s",
    default="example",
    help="List of services to enable",
)
@click.option(
    "--pages",
    "-p",
    default="example",
    help="List of pages to enable",
)
@click.option(
    "--vite-server",
    "-V",
    is_flag=True,
    default=False,
    help="Run vite server with Sanic",
)
@click.option(
    "--auto-reload", "-A", default=False, is_flag=True, help="Enable Auto reload"
)
@click.option(
    "--access-log", "-L", default=False, is_flag=True, help="Enable access_log"
)
@click.option("--debug", "-D", default=False, is_flag=True, help="Enable Auto reload")
def webcli(host, port, workers, services, pages, auto_reload, access_log, debug, vite_server):
    """Run Web Server"""
    # pylint: disable=import-outside-toplevel
    from changeme.server import app_init
    from changeme.types.config import Settings

    pwd = os.getcwd()
    console.print(f"PWD: {pwd}")
    settings = Settings(BASE_PATH=pwd)
    settings.TEMPLATES_DIR = f"{pwd}/templates"
    services_bp = None
    if services:
        services_bp = services.split(",")

    pages_bp = None
    if pages:
        pages_bp = pages.split(",")

    app = app_init(settings, services_bp=services_bp, pages_bp=pages_bp)
    w = int(workers)
    console.print(f"Debug mode: {debug}")
    if not vite_server:
        app.run(
            host=host,
            port=int(port),
            workers=w,
            auto_reload=auto_reload,
            debug=debug,
            access_log=access_log,
        )
    else:
        keywords = dict(
            host=host,
            port=int(port),
            workers=w,
            auto_reload=auto_reload,
            debug=debug,
            access_log=access_log,
        )
        vite = mp.Process(target=run_vite)
        sanic = mp.Process(target=run_sanic, args=(app,), kwargs=keywords)
        vite.start()
        sanic.start()
        vite.join()
        sanic.join()


@click.option(
    "--vite-build", "-v", default=True, is_flag=True, help="Also do a yarn build"
)
@click.command(name="collectstatic")
@click.argument("outputdir")
def collectcli(outputdir, vite_build):
    """ Collects statics file into one folder """
    from changeme.types.config import Settings
    root = Path.cwd()
    settings = Settings(BASE_PATH=str(root))

    output = root / outputdir
    if output.exists():
        # console.print(f"[bold red]{output} dir will be deleted[/]")
        should_del = Confirm.ask(
            f"{output} dir will be deleted, continue?", default=True)
        if should_del:
            shutil.rmtree(output)
        else:
            console.print(f"[bold red]Anything collected[/]")
            sys.exit()

    for k, v in settings.STATICFILES_DIRS.items():
        dst = Path(f"{output}/{k}")
        console.print(f"Copying from {v} to {dst}")
        shutil.copytree(v, str(dst))
        # for file_or_dir in Path(v).glob("**/*"):
        #    print(file_or_dir)

    if vite_build:
        res = execute_cmd("yarn build")
        console.print(res)

    dst = Path(f"{output}/{settings.VITE_BASE}")

    console.print(f"Copying from {settings.VITE_OUTPUT_DIR} to {dst}")
    shutil.copytree(settings.VITE_OUTPUT_DIR, str(dst))
