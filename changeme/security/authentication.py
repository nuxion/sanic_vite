from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

import jwt
from changeme import defaults
from changeme.errors.security import AuthValidationFailed
from changeme.types.config import Settings
from changeme.types.security import JWTConfig, UserLogin
from sanic import Request

from .utils import open_keys


def _get_delta(delta_min: int) -> int:
    """ Returns a timestamp addding a delta_min value to the utc now date. """
    delta = datetime.utcnow() + timedelta(minutes=delta_min)
    return int(delta.timestamp())


class BaseAuth:

    def __init__(self, conf: JWTConfig):
        """
        It is a wrapper around jwt which produces jwt tokens.
        By default it will add a "exp" claim, other claims.

        Standard claims could be configurated from JWTConfing or when passing
        a payload to encode. In that case if both configurations exists, it will
        prioritize the payload configuration.
        """
        self.conf = conf
        # self.auth_method = auth_method
        # self.retrieve_refresh_token = retrieve_refresh_token
        # self.store_refresh_token = store_refresh_token

    def _get_secret_encode(self):
        """ because jwt allows the use of a simple secret or a pairs of keys 
        this function will look at the configuration to determine a secret to be used
        """
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

    def encode(self, payload: Dict[str, Any],
               exp=None,
               iss=None,
               aud=None) -> str:
        """ Encode a payload into a JWT Token.

        Some standards claims like exp, iss and aud could be 
        overwritten using this params.

        :param payload: a dictionary with any k/v pairs to add
        :param exp:  the “exp” (expiration time) claim identifies the expiration 
        time on or after which the JWT MUST NOT be accepted for processing.
        if date or int is given it will overwrite the default configuration.
        :param iss: the “iss” (issuer) claim identifies the principal that issued the JWT.
        :param aud: The “aud” (audience) claim identifies the recipients that the JWT 
        is intended for.
        """
        _secret = self._get_secret_encode()

        final = self._build_payload(payload, exp, iss, aud)

        encoded = jwt.encode(final, _secret,
                             algorithm=self.conf.alg,
                             )
        return encoded

    def decode(self, encoded, verify_signature=True, iss=None, aud=None) \
            -> Dict[str, Any]:
        _secret = self._get_secret_decode()

        _iss = iss or self.conf.issuer
        _aud = aud or self.conf.audience

        return jwt.decode(encoded,
                          _secret,
                          options={
                              "verify_signature": verify_signature,
                              "require": self.conf.requires_claims
                          },
                          aud=_aud,
                          iss=_iss,
                          algorithms=self.conf.alg
                          )

    def init_app(self, app):
        app.ctx.auth = self

    def validate(self, token: str,
                 required_scopes: Optional[List[str]],
                 require_all=True,
                 iss=None, aud=None
                 ) -> Dict[str, Any]:
        raise NotImplementedError()


class Auth(BaseAuth):

    def validate(self, token: str,
                 required_scopes: Optional[List[str]],
                 require_all=True,
                 iss=None, aud=None
                 ) -> Dict[str, Any]:
        try:
            decoded = self.decode(token, iss=iss, aud=aud)
            if required_scopes:
                user_scopes: List[str] = decoded["scopes"]
                valid = validate_scopes(required_scopes, user_scopes,
                                        require_all=require_all)
                if not valid:
                    raise AuthValidationFailed()
        except jwt.InvalidTokenError as e:
            raise AuthValidationFailed()

        return decoded

    @classmethod
    def from_settings(cls, settings: Settings) -> Auth:
        """ Intiliazie a `Auth` based on settings. """
        keys = open_keys(settings.JWT_PUBLIC, settings.JWT_PRIVATE)
        conf = JWTConfig(
            alg=settings.JWT_ALG,
            exp_min=settings.JWT_EXP,
            keys=keys,
            issuer=settings.JWT_ISS,
            audience=settings.JWT_AUD,
            requires_claims=settings.JWT_REQUIRES_CLAIMS
        )
        return cls(conf)

    async def authenticate(request: Request):
        pass


def scope2dict(scopes: List[str]) -> Dict[str, Set]:
    """ Given a list of scopes like ["admin:write", "user:read"]
    it will returns a dictionary where the namespace is the key and the actions
    turns into a set """
    permissions: Dict[str, Set] = {}
    for s in scopes:
        try:
            ns, action = s.split(":", maxsplit=1)
        except ValueError:
            ns = s
            action = "any"
        ns = ns if ns else "any"
        actions = {a for a in action.split(":")}
        permissions[ns] = actions
    return permissions


def validate_scopes(scopes: List[str],
                    user_scopes: List[str],
                    require_all=True,
                    require_all_actions=True) -> bool:
    """ 
    from sanic_jwt
    the idea is to provide a scoped access to different resources
    """
    user_perms = scope2dict(user_scopes)
    required = scope2dict(scopes)
    names = {k for k in user_perms.keys()}
    required_names = {k for k in required.keys()}
    intersection = required_names.intersection(names)
    if require_all:
        if len(required_names) != len(intersection) \
           and "any" not in required.keys():
            return False
    elif intersection == 0 and "any" not in required.keys():
        return False

    _match = 0
    for ns in intersection:
        actions_matched = required[ns].intersection(user_perms[ns])
        if len(actions_matched) > 0 or "any" in required[ns]:
            _match += 1
    if _match == 0:
        return False
    return True
