"""Mapeo de identidad OIDC verificada a Usuario interno."""

from typing import Protocol

from app.security.oidc import IdentidadOidc
from app.shared.application import NoAutenticado
from app.shared.application.contexto import ContextoIdentidad


class UsuarioIdentidadReferencia(Protocol):
    """Vista mínima del Usuario para autenticación."""

    @property
    def id(self) -> str:
        """Identificador interno opaco."""


class ResolverUsuarioPorIdentidad(Protocol):
    """Contrato público consumidor del módulo Usuarios."""

    async def obtener_por_identidad(
        self, issuer: str, subject: str
    ) -> UsuarioIdentidadReferencia | None:
        """Busca el Usuario enlazado a ``issuer + subject``."""


class VerificadorToken(Protocol):
    """Puerto para verificar un bearer token administrado."""

    async def verificar(self, token: str) -> IdentidadOidc:
        """Verifica el token y devuelve su identidad estable."""


class ServicioIdentidad:
    """Construye ``ContextoIdentidad`` desde un bearer token."""

    def __init__(
        self,
        verificador: VerificadorToken,
        usuarios: ResolverUsuarioPorIdentidad,
    ) -> None:
        self._verificador = verificador
        self._usuarios = usuarios

    async def autenticar(self, token: str) -> ContextoIdentidad:
        """Exige token válido y Usuario interno registrado."""
        oidc = await self._verificador.verificar(token)
        usuario = await self._usuarios.obtener_por_identidad(oidc.issuer, oidc.subject)
        if usuario is None:
            raise NoAutenticado("La identidad no corresponde a un Usuario registrado")
        return ContextoIdentidad(
            usuario_id=usuario.id,
            issuer=oidc.issuer,
            subject=oidc.subject,
        )
