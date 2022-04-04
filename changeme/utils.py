import codecs
import json
import os
import subprocess
from pathlib import Path

from changeme import defaults
from changeme.errors import CommandExecutionException


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path="__version__.py"):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def get_query_param(request, key, default_val=None):
    val = request.args.get(key, default_val)
    return val


def mkdir_p(fp):
    """Make the fullpath
    similar to mkdir -p in unix systems.
    """
    Path(fp).mkdir(parents=True, exist_ok=True)


def open_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
        dict_ = json.loads(data)
    return dict_


def execute_cmd(cmd) -> str:
    """Wrapper around subprocess"""
    with subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as p:

        out, err = p.communicate()
        if err:
            raise CommandExecutionException(err.decode())

        return out.decode().strip()


def path_norm(fp):
    """Given a  filepath returns a normalized a path"""
    return str(Path(fp))
