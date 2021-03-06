from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class KeyPairs(BaseModel):
    public: str
    private: str


class JWTConfig(BaseModel):
    alg: str
    exp_min: int = 30
    keys: Optional[KeyPairs] = None
    secret: Optional[str] = None
    issuer: Optional[str] = None
    audience: Optional[str] = None
    requires_claims: List[str] = ["exp"]


class UserLogin(BaseModel):
    username: str
    password: str


class JWTResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str]
