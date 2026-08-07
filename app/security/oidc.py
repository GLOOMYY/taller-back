"""Adaptador de verificación para access tokens OIDC firmados."""

import asyncio
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Protocol, cast

from app.shared.application import NoAutenticado


@dataclass(frozen=True, slots=True)
class IdentidadOidc:
    """Identificador estable obtenido de claims verificados."""

    issuer: str
    subject: str


class ClienteJwks(Protocol):
    """Parte de ``PyJWKClient`` usada por el adaptador."""

    def get_signing_key_from_jwt(self, token: str) -> Any:
        """Obtiene la clave que corresponde al ``kid`` del token."""


class VerificadorOidcPyJwt:
    """Verifica firma, emisor, audiencia y claims temporales con PyJWT.

    La obtención y caché de JWKS pertenecen a ``PyJWKClient``. Como su API es
    síncrona, todo el trabajo se ejecuta fuera del event loop.
    """

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_url: str,
        algoritmos: tuple[str, ...] = ("RS256",),
        cliente_jwks: ClienteJwks | None = None,
        modulo_jwt: ModuleType | Any | None = None,
    ) -> None:
        if not issuer or not audience or not jwks_url:
            raise ValueError("issuer, audience y jwks_url son obligatorios")
        if not algoritmos or any(alg.lower() == "none" for alg in algoritmos):
            raise ValueError("Debe configurarse un algoritmo de firma seguro")
        # OIDC exige coincidencia exacta del issuer. Auth0 publica normalmente
        # el valor con slash final; eliminarlo invalidaría tokens legítimos.
        self._issuer = issuer
        self._audience = audience
        self._algoritmos = algoritmos
        self._jwt = modulo_jwt or _importar_pyjwt()
        self._cliente_jwks = cliente_jwks or self._jwt.PyJWKClient(jwks_url)

    async def verificar(self, token: str) -> IdentidadOidc:
        """Devuelve identidad solo después de validar criptografía y claims."""
        if not token or not token.strip():
            raise NoAutenticado("Token ausente o inválido")
        try:
            claims = await asyncio.to_thread(self._decodificar, token)
        except self._jwt.PyJWTError as exc:
            raise NoAutenticado("Token ausente o inválido") from exc
        except (KeyError, TypeError, ValueError) as exc:
            raise NoAutenticado("Token ausente o inválido") from exc

        subject = claims.get("sub")
        issuer = claims.get("iss")
        if not isinstance(subject, str) or not subject.strip():
            raise NoAutenticado("Token ausente o inválido")
        if issuer != self._issuer:
            raise NoAutenticado("Token ausente o inválido")
        return IdentidadOidc(issuer=self._issuer, subject=subject)

    def _decodificar(self, token: str) -> dict[str, Any]:
        clave = self._cliente_jwks.get_signing_key_from_jwt(token).key
        resultado = self._jwt.decode(
            token,
            clave,
            algorithms=list(self._algoritmos),
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iat", "iss", "sub", "aud"]},
        )
        return cast(dict[str, Any], resultado)


def _importar_pyjwt() -> ModuleType:
    """Carga la dependencia opcional con un error de configuración claro."""
    try:
        import jwt
    except ModuleNotFoundError as exc:  # pragma: no cover - fallo de instalación
        raise RuntimeError("PyJWT[crypto] es necesario para verificar OIDC") from exc
    return jwt
