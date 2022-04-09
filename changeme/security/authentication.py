from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from copy import deepcopy

import jwt
from changeme import defaults
from changeme.types.security import JWTConfig


def _get_delta(delta_min: int) -> float:
    delta = datetime.utcnow() + timedelta(minutes=delta_min)
    return delta.timestamp()


class Auth:

    def __init__(self, conf: JWTConfig):
        self.conf = conf

    def _get_secret_encode(self):
        if self.conf.keys:
            _secret = self.conf.keys.private
        else:
            _secret = self.conf.secret
        return _secret

    def _get_secret_decode(self):
        if self.conf.keys:
            _secret = self.conf.keys.public
        else:
            _secret = self.conf.secret
        return _secret

    def _build_payload(self, payload: Dict[str, Any], exp=None, iss=None, aud=None):
        _payload = deepcopy(payload)
        if not exp:
            exp = _get_delta(self.conf.exp_min)
        _iss = iss or self.conf.issuer
        if _iss:
            _payload.update({"iss": _iss})

        _aud = aud or self.conf.audience
        if _aud:
            _payload.update({"aud": _aud})

        _payload.update({"exp": exp})
        return _payload

    def encode(self, payload: Dict[str, Any], exp=None, iss=None, aud=None):
        _secret = self._get_secret_encode()

        final = self._build_payload(payload, exp, iss, aud)

        encoded = jwt.encode(final, _secret,
                             algorithm=self.conf.alg,
                             )
        return encoded

    def decode(self, encoded, verify_signature=True):
        _secret = self._get_secret_decode()

        return jwt.decode(encoded,
                          _secret,
                          options={
                              "verify_signature": verify_signature,
                              "require": self.conf.requires_claims
                          },
                          algorithms=self.conf.alg
                          )
