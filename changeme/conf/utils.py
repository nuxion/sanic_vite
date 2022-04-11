import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path

from changeme import defaults
from changeme.types.config import Settings

# Server defaults
GLOBAL_MODULE = "changeme.conf.global_settings"
ENVIRONMENT_VARIABLE = "CHANGEME_SETTINGS_MODULE"
DEFAULT_MODULE = os.environ.get(ENVIRONMENT_VARIABLE, GLOBAL_MODULE)


def load_settings(settings_module=DEFAULT_MODULE) -> Settings:
    module_loaded = settings_module
    try:
        mod = importlib.import_module(settings_module)
    except ModuleNotFoundError:
        mod = importlib.import_module(GLOBAL_MODULE)
        module_loaded = GLOBAL_MODULE

    settings_dict = {}
    for m in dir(mod):
        if m.isupper():
            # sets.add(m)
            value = getattr(mod, m)
            settings_dict[m] = value

    cfg = Settings(**settings_dict)
    cfg.SETTINGS_MODULE = module_loaded

    # logging.basicConfig(format=cfg.LOGFORMAT, level=_level)

    return cfg
