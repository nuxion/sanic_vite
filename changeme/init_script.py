from pathlib import Path
from typing import List

from changeme.conf.jtemplates import render_to_file
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from changeme.utils import get_parent_folder, mkdir_p, normalize_name

console = Console()

DIRECTORIES = [
    "templates",
    "sanic_app",
]
PROJECT_FILES = [
    {"tpl": "gitignore", "dst": ".gitignore"},
]

VITE_FILES = [
    {"tpl": "vite/vite.config.js", "dst": "vite.config.js"},
    {"tpl": "vite/package.json", "dst": "package.json"},
    {"tpl": "vite/jsconfig.json", "dst": "jsconfig.json"},
]


def _empty_file(filename):
    with open(filename, "w", encoding="utf-8") as f:
        pass
    return True


def ask_project_name() -> str:
    parent = get_parent_folder()
    _default = normalize_name(parent)
    project_name = Prompt.ask(
        f"Write a name for this project, [yellow]please, avoid spaces and capital "
        "letters[/yellow]: ",
        default=_default,
    )
    name = normalize_name(project_name)
    console.print(
        f"The final name for the project is: [bold magenta]{name}[/bold magenta]"
    )
    return name


def init_vite(root, vite_files, extra_data=None):
    for vite in vite_files:
        render_to_file(
            vite["tpl"],
            str((root / vite["dst"]).resolve()),
            data=extra_data
        )


def init_sanic_app(root, extra_data=None):
    # _pkg_dir = get_package_dir("nb_workflows")
    p = root / "sanic_app"
    _empty_file(p / "__init__.py")
    render_to_file(
        "global_settings.py",
        str((p / "settings.py").resolve()),
        data=extra_data
    )


def init_lib_folder(root, name):
    fp = str(root / name)
    mkdir_p(fp)
    _empty_file((root / name / "__init__.py"))


def init_project_files(root, files):
    for f in files:
        render_to_file(
            f["tpl"],
            str((root / f["dst"]).resolve()),
        )


def create_folders(root, folders: List[str]):
    for f in folders:
        mkdir_p(root / f)


def init(base_path: str, with_vite=True):
    root = Path(base_path)

    name = ask_project_name()
    init_lib_folder(root, name)
    create_folders(root, DIRECTORIES)
    init_sanic_app(root)
    if with_vite:
        init_vite(root, VITE_FILES)
    init_project_files(root, PROJECT_FILES)
