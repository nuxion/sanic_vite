import importlib
import os
import shutil
import subprocess
import sys
from getpass import getpass
from pathlib import Path

import click
from changeme.conf import load_settings
from changeme.db.sync import SQL
from changeme.db.utils import alembic_revision, alembic_ugprade
from changeme.managers import users_mg
from changeme.types.user import UserOrm
from changeme.utils import execute_cmd, mkdir_p
from rich.console import Console
from rich.prompt import Confirm, Prompt

settings = load_settings()
console = Console()


@click.group(name="manager")
def managercli():
    """
    Managment tasks like user creation and db init
    """
    pass


@managercli.command(name="collectstatic")
@click.option(
    "--vite-build", "-v", default=True, is_flag=True, help="Also do a yarn build"
)
@click.argument("outputdir")
def collectcli(outputdir, vite_build):
    """ Collects statics files into one folder """
    root = Path.cwd()
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

    for _, v in settings.STATICFILES_DIRS.items():
        dst = Path(f"{output}/{v['localdir']}")
        console.print(f"Copying from {v['localdir']} to {dst}")
        shutil.copytree(v['localdir'], str(dst))
        # for file_or_dir in Path(v).glob("**/*"):
        #    print(file_or_dir)

    if vite_build:
        res = execute_cmd("yarn build")
        console.print(res)

    dst = Path(f"{output}/{settings.VITE_BASE}")

    console.print(f"Copying from {settings.VITE_OUTPUT_DIR} to {dst}")
    shutil.copytree(settings.VITE_OUTPUT_DIR, str(dst))


@managercli.command(name="db")
@click.option("--sql", "-s", default=settings.SQL, help="SQL Database")
@click.option("--message", "-m", default=None, help="Revision name")
@click.option("--rev-id", "-R", help="Revision id")
@click.option("--migration", "-M", help="Migration name defined in settings")
@click.argument("action", type=click.Choice(["create", "drop", "upgrade", "revision"]))
def dbcli(sql, action, message, rev_id, migration):
    """Create or Drop tables from a database"""
    db = SQL(sql)
    settings.SQL = sql

    if action == "create":
        db.create_all()
        click.echo("Created...")
    elif action == "drop":
        db.drop_all()
        click.echo("Droped...")
    elif action == "upgrade":
        if migration:
            m = settings.MIGRATIONS[migration]
            alembic_ugprade(sql, m)
        else:
            for k, m in settings.MIGRATIONS.items():
                console.print(f"[bold magenta]Upgrading {k}[/]")
                alembic_ugprade(sql, m)

    elif action == "revision":
        if migration:
            m = settings.MIGRATIONS[migration]
            alembic_revision(
                sql,
                rev_id,
                message,
                m)
        else:
            for k, m in settings.MIGRATIONS.items():
                console.print(f"[bold magenta]Migrating {k}[/]")
                alembic_revision(
                    sql,
                    rev_id,
                    message,
                    m)

    else:
        console.print("[red bold]Wrong param...[/]")


@managercli.command(name="users")
@click.option("--sql", "-s", default=settings.SQL, help="SQL Database")
@click.option("--is-superuser", "-S", default=False, help="Is a superuser")
@click.option("--scopes", "-C", default="user:r:w", help="Is a superuser")
@click.argument("action", type=click.Choice(["create", "disable", "reset"]))
def userscli(sql, action, is_superuser, scopes):
    """Create a user"""
    db = SQL(sql)
    S = db.sessionmaker()
    settings.SQL = sql
    os.environ["CHANGEME_SQL"] = sql

    if action == "create":
        name = Prompt.ask("Username")
        email = Prompt.ask("Email (optional)", default=None)
        password = getpass("Password: ")
        repeat = getpass("Paswword (repeat): ")
        if password != repeat:
            console.print("[bold red]Paswords doesn't match[/]")
            sys.exit(-1)
        key = users_mg.encrypt_password(password, salt=settings.AUTH_SALT)
        with S() as session:
            obj = UserOrm(
                username=name,
                password=key,
                email=email,
                scopes=scopes,
                is_superuser=is_superuser
            )
            user = users_mg.create(session, obj)
            session.commit()
        console.print(f"[bold magenta]Congrats!! user {name} created")

    elif action == "reset":
        name = Prompt.ask("Username")
        _p = getpass("Password: ")
        with S() as session:
            changed = users_mg.change_pass(
                session, name, _p, salt=settings.AUTH_SALT)
            session.commit()
        if changed:
            console.print("[bold magenta]Pasword changed[/]")
        else:
            console.print("[bold red]User may not exist [/]")
    else:
        console.print("[red bold]Wrongs params[/]")
