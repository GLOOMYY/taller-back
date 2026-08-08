"""Emisión y verificación de JWT propios de Taller."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.security.oidc import IdentidadOidc
from app.shared.application import NoAutenticado


class ServicioJwtLocal:
    """Firma tokens HS256 y deriva la identidad interna desde ``sub``."""

    def __init__(self, secreto: str, *, emisor: str, minutos_expiracion: int) -> None:
        if len(secreto) < 32:
            raise ValueError("JWT_SECRET debe tener al menos 32 caracteres")
        if minutos_expiracion < 5:
            raise ValueError("JWT_EXPIRACION_MINUTOS debe ser de al menos 5")
        self._secreto = secreto
        self._emisor = emisor
        self._minutos_expiracion = minutos_expiracion

    def emitir(self, usuario_id: str) -> str:
        ahora = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": usuario_id,
                "iss": self._emisor,
                "iat": ahora,
                "exp": ahora + timedelta(minutes=self._minutos_expiracion),
                "typ": "access",
            },
            self._secreto,
            algorithm="HS256",
        )

    async def verificar(self, token: str) -> IdentidadOidc:
        if not token.strip():
            raise NoAutenticado("Token ausente o inválido")
        try:
            claims: dict[str, Any] = jwt.decode(
                token, self._secreto, algorithms=["HS256"], issuer=self._emisor,
                options={"require": ["exp", "iat", "iss", "sub"]},
            )
        except jwt.PyJWTError as error:
            raise NoAutenticado("Token ausente o inválido") from error
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise NoAutenticado("Token ausente o inválido")
        return IdentidadOidc(issuer=self._emisor, subject=subject)
