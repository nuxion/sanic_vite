from typing import Union

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class PasswordScript:
    """
    https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#cryptography.hazmat.primitives.kdf.scrypt.Scrypt
    """

    def __init__(self, salt: Union[bytes, str], n=2**14, r=8, p=1):
        if isinstance(salt, str):
            salt = salt.encode("utf-8")
        self.n = n
        self.r = r
        self.p = p
        self.salt = salt

    def _kdf(self):
        kdf = Scrypt(
            salt=self.salt,
            length=32,
            n=self.n,
            r=self.r,
            p=self.p,
        )
        return kdf

    def encrypt(self, pass_: str) -> bytes:
        kdf = self._kdf()

        return kdf.derive(pass_.encode("utf-8"))

    def verify(self, pass_: str, key: bytes) -> bool:
        kdf = self._kdf()
        try:
            kdf.verify(pass_.encode("utf-8"), key)
            return True
        except:
            return False
