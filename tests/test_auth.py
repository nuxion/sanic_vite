from datetime import datetime, timedelta
import pytest
import jwt
from changeme import defaults
from changeme.security.authentication import Auth
from changeme.security.utils import open_keys
from changeme.types.security import JWTConfig, KeyPairs


def test_auth_open_keys():
    keys = open_keys("tests/ecdsa.pub.pem", "tests/ecdsa.priv.pem")
    assert isinstance(keys, KeyPairs)
    assert "GSM49Ag" in keys.public


def test_auth_Auth_encode():
    keys = open_keys("tests/ecdsa.pub.pem", "tests/ecdsa.priv.pem")
    conf = JWTConfig(alg=defaults.JWT_ALG, keys=keys)
    a = Auth(conf)
    encoded = a.encode({"test": "hi"})
    original = a.decode(encoded)

    _exp = datetime.utcnow() - timedelta(minutes=1)
    encoded_invalid = a.encode({}, exp=_exp)
    with pytest.raises(jwt.ExpiredSignatureError):
        a.decode(encoded_invalid)

    assert isinstance(encoded, str)
    assert original["test"] == "hi"
    assert "exp" in original.keys()
