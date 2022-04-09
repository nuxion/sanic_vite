from typing import Any, Dict, Optional, List

from pydantic import BaseModel


class KeyPairs(BaseModel):
    public: str
    private: str


class JWTConfig(BaseModel):
    alg: str
    exp_min: int = 5
    header_name: str = "authorization"
    keys: Optional[KeyPairs] = None
    secret: Optional[str] = None
    issuer: Optional[str] = None
    audience: Optional[str] = None
    requires_claims: List[str] = ["exp"]
