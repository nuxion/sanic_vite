import binascii
import importlib
import os

from changeme.types.security import KeyPairs


def open_keys(pub, priv) -> KeyPairs:
    with open(pub, "r") as f:
        pub = f.read()
        pub = pub.strip()
    with open(priv, "r") as f:
        priv = f.read()
        priv = priv.strip()
    return KeyPairs(public=pub, private=priv)


def generate_token(n=24, *args, **kwargs):
    return str(binascii.hexlify(os.urandom(n)), "utf-8")


def load_auth_class(class_path):
    module, class_name = class_path.rsplit(".", maxsplit=1)
    mod = importlib.import_module(module)
    obj = getattr(mod, class_name)
    return obj
