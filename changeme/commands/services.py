import multiprocessing as mp
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click
from changeme.utils import execute_cmd, mkdir_p
from rich.console import Console
from rich.prompt import Confirm

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
@click.option(
    "--with-auth-bp", "-E", default=True, is_flag=True, help="Enable authentication endpoints"
)
@click.option("--debug", "-D", default=False, is_flag=True, help="Enable Auto reload")
def webcli(host, port, workers, services, pages, auto_reload, access_log, debug,
           with_auth_bp,
           vite_server):
    """Run Web Server"""
    # pylint: disable=import-outside-toplevel
    from changeme.server import create_app
    from changeme.types import Settings

    pwd = os.getcwd()
    settings = Settings(BASE_PATH=pwd)
    console.print(f"BASE_PATH: {settings.BASE_PATH}")
    settings.TEMPLATES_DIR = f"{pwd}/templates"
    console.print(f"TEMPLATES_DIR: {settings.TEMPLATES_DIR}")
    console.print(f"Debug mode: {debug}")

    services_bp = None
    if services:
        services_bp = services.split(",")

    pages_bp = None
    if pages:
        pages_bp = pages.split(",")

    app = create_app(settings, services_bp=services_bp,
                     pages_bp=pages_bp, with_vite=True, with_auth_bp=with_auth_bp)
    w = int(workers)
    app.run(
        host=host,
        port=int(port),
        access_log=access_log,
        workers=w,
        debug=debug
    )
    # if not vite_server:
    #     app.run(
    #         host=host,
    #         port=int(port),
    #         workers=w,
    #         auto_reload=auto_reload,
    #         debug=debug,
    #         access_log=access_log,
    #     )
    # else:
    #     keywords = dict(
    #         host=host,
    #         port=int(port),
    #         workers=w,
    #         auto_reload=auto_reload,
    #         debug=debug,
    #         access_log=access_log,
    #     )
    #     vite = mp.Process(target=run_vite)
    #     sanic = mp.Process(target=run_sanic, args=(app,), kwargs=keywords)
    #     vite.start()
    #     sanic.start()
    #     vite.join()
    #     sanic.join()
