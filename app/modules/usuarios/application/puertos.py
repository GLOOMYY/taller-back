"""Puertos requeridos por los casos de uso de Usuarios."""

from typing import Protocol

from app.modules.usuarios.domain.modelos import IdentidadOidc, Usuario


class RepositorioUsuarios(Protocol):
    """Persistencia de Usuarios sin detalles de tecnología."""

    async def crear(self, usuario: Usuario) -> None:
        """Persiste un Usuario nuevo."""
        ...

    async def obtener_por_identidad(self, identidad: IdentidadOidc) -> Usuario | None:
        """Obtiene un Usuario por su identidad OIDC estable."""
        ...

    async def obtener_por_id(self, usuario_id: str) -> Usuario | None:
        """Obtiene un Usuario por su identificador opaco."""
        ...

    async def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        """Resuelve un identificador público global normalizado."""
        ...

    async def actualizar(self, usuario: Usuario) -> None:
        """Persiste cambios de perfil."""
        ...


class GeneradorId(Protocol):
    """Genera identificadores opacos para el dominio."""

    def generar(self) -> str:
        """Genera un identificador nuevo."""
        ...
