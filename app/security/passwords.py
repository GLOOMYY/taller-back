"""Hash de contraseñas sin almacenar secretos en claro."""

import base64
import hashlib
import hmac
import os


def hash_password(password: str) -> str:
    """Genera un hash scrypt con sal aleatoria."""
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    salt = os.urandom(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$" + base64.urlsafe_b64encode(salt + derived).decode()


def verify_password(password: str, encoded: str) -> bool:
    """Compara una contraseña con su hash de forma constante."""
    try:
        scheme, raw = encoded.split("$", 1)
        if scheme != "scrypt":
            return False
        data = base64.urlsafe_b64decode(raw.encode())
        salt, expected = data[:16], data[16:]
        actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
