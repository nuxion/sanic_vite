from changeme.types.security import KeyPairs


def open_keys(pub, priv) -> KeyPairs:
    with open(pub, "r") as f:
        pub = f.read()
        pub = pub.strip()
    with open(priv, "r") as f:
        priv = f.read()
        priv = priv.strip()
    return KeyPairs(public=pub, private=priv)

