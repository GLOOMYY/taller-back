"""Casos de uso del módulo Usuarios."""

from app.modules.usuarios.application.puertos import GeneradorId, RepositorioUsuarios
from app.modules.usuarios.domain.modelos import (
    IdentidadOidc,
    Usuario,
    normalizar_nombre_usuario,
)
from app.shared.application.errores import Conflicto, NoAutenticado


class ServicioUsuarios:
    """Registra y administra el perfil del Usuario autenticado."""

    def __init__(self, repositorio: RepositorioUsuarios, generador_id: GeneradorId):
        self._repositorio = repositorio
        self._generador_id = generador_id

    async def registrar(
        self,
        identidad: IdentidadOidc,
        *,
        nombre: str,
        nombre_usuario: str,
    ) -> Usuario:
        """Registra la identidad OIDC verificada como Usuario interno."""
        if await self._repositorio.obtener_por_identidad(identidad) is not None:
            raise Conflicto("El Usuario ya está registrado")
        usuario = Usuario(
            id=self._generador_id.generar(),
            identidad=identidad,
            nombre=nombre,
            nombre_usuario=nombre_usuario,
        )
        if (
            await self._repositorio.obtener_por_nombre_usuario(usuario.nombre_usuario)
            is not None
        ):
            raise Conflicto(
                "El nombre de usuario no está disponible",
            )
        try:
            await self._repositorio.crear(usuario)
        except NombreUsuarioDuplicado as error:
            raise Conflicto(
                "El nombre de usuario no está disponible",
            ) from error
        except IdentidadDuplicada as error:
            raise Conflicto("El Usuario ya está registrado") from error
        return usuario

    async def consultar(self, identidad: IdentidadOidc) -> Usuario:
        """Consulta el perfil asociado a una identidad OIDC verificada."""
        usuario = await self._repositorio.obtener_por_identidad(identidad)
        if usuario is None:
            raise NoAutenticado("La identidad no corresponde a un Usuario")
        return usuario

    async def actualizar(
        self,
        identidad: IdentidadOidc,
        *,
        nombre: str | None = None,
        nombre_usuario: str | None = None,
    ) -> Usuario:
        """Actualiza los campos suministrados del perfil actual."""
        usuario = await self.consultar(identidad)
        actualizado = usuario.actualizar(
            nombre=nombre,
            nombre_usuario=nombre_usuario,
        )
        if actualizado == usuario:
            return usuario
        if (
            actualizado.nombre_usuario != usuario.nombre_usuario
            and await self._repositorio.obtener_por_nombre_usuario(
                actualizado.nombre_usuario
            )
            is not None
        ):
            raise Conflicto(
                "El nombre de usuario no está disponible",
            )
        try:
            await self._repositorio.actualizar(actualizado)
        except NombreUsuarioDuplicado as error:
            raise Conflicto(
                "El nombre de usuario no está disponible",
            ) from error
        return actualizado

    async def obtener_por_identidad(self, issuer: str, subject: str) -> Usuario | None:
        """Expone la vista pública consumida por autenticación."""
        return await self._repositorio.obtener_por_identidad(
            IdentidadOidc(issuer=issuer, subject=subject)
        )

    async def buscar_por_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        """Expone la resolución pública consumida por Membresías."""
        return await self._repositorio.obtener_por_nombre_usuario(
            normalizar_nombre_usuario(nombre_usuario)
        )


class NombreUsuarioDuplicado(Exception):
    """Conflicto de persistencia por unicidad del identificador público."""


class IdentidadDuplicada(Exception):
    """Conflicto de persistencia por unicidad de issuer y subject."""
