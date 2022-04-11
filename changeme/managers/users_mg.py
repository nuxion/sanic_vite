from datetime import datetime
from inspect import isawaitable
from typing import Union

from changeme.models.user import UserModel
from changeme.security.password import PasswordScript
from changeme.types.user import UserOrm
from sqlalchemy import select
from sqlalchemy.orm import selectinload


def select_user():
    # stmt = select(UserModel).options(
    #    selectinload(UserModel.projects),
    # )
    stmt = select(UserModel)
    return stmt


def encrypt_password(password, salt: Union[bytes, str]):

    pm = PasswordScript(salt)
    encrypted = pm.encrypt(password)
    return encrypted


def create(
        session, u: UserOrm) -> UserModel:
    if u.is_superuser and "admin:read:write" not in u.scopes:
        u.scopes = f"{u.scopes},admin:r:w"
    um = UserModel(**u.dict())
    session.add(um)
    return um


async def get_user_async(session, username: str) -> Union[UserModel, None]:
    stmt = select_user().where(UserModel.username == username).limit(1)

    rsp = await session.execute(stmt)
    return rsp.scalar_one_or_none()


def get_user(session, username: str) -> Union[UserModel, None]:
    stmt = select(UserModel).where(UserModel.username == username).limit(1)
    rsp = session.execute(stmt)

    return rsp.scalar_one_or_none()


def disable_user(session, username: str) -> Union[UserModel, None]:
    user = get_user(session, username)
    if user:
        user.is_active = False
        user.updated_at = datetime.utcnow()
        session.add(user)

        return user
    return None


async def change_pass_async(session, username: str, new_password: str, salt):
    u = await get_user_async(session, username)
    if u:
        pass_ = encrypt_password(new_password, salt=salt)
        u.password == pass_
        u.updated_at = datetime.utcnow()
        session.add(u)


def change_pass(session, user: str, new_password: str, salt) -> bool:
    obj = get_user(session, user)
    if obj:
        pass_ = encrypt_password(new_password, salt=salt)
        obj.password = pass_
        obj.updated_at = datetime.utcnow()
        session.add(obj)
        return True
    return False


async def disable_user_async(session, username: str) -> Union[UserModel, None]:
    user = await get_user_async(session, username)
    if user:
        user.is_active = False
        user.updated_at = datetime.utcnow()
        session.add(user)

        return user
    return None


def verify_password(user: UserModel, pass_provided: str, salt: bytes):
    pm = PasswordScript(salt)
    verified = pm.verify(pass_provided, user.password)
    if verified and user.is_active:
        return True
    return False
