from typing import Optional

from pydantic import BaseModel


class UserOrm(BaseModel):
    username: str
    email: Optional[str] = None
    password: Optional[bytes] = None
    scopes: str = "user:r:w"
    is_superuser: bool = False
    is_active: bool = False

    class Config:
        orm = True
