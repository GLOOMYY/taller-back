"""Adaptador MongoDB asíncrono para Usuarios."""

from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from pymongo.errors import DuplicateKeyError

from app.modules.usuarios.application.casos_uso import (
    IdentidadDuplicada,
    NombreUsuarioDuplicado,
)
from app.modules.usuarios.domain.modelos import IdentidadOidc, Usuario


class GeneradorUuid:
    """Genera UUID opacos sin acoplar el dominio al formato de MongoDB."""

    def generar(self) -> str:
        """Genera un UUID aleatorio serializado."""
        return str(uuid4())


class RepositorioUsuariosMongo:
    """Persiste Usuarios en una colección async compatible con PyMongo."""

    def __init__(self, coleccion: Any):
        self._coleccion = coleccion

    async def crear_indices(self) -> None:
        """Crea los índices que sostienen las dos unicidades globales."""
        await self._coleccion.create_index(
            [("issuer", 1), ("subject", 1)],
            unique=True,
            name="uq_usuarios_identidad_oidc",
        )
        await self._coleccion.create_index(
            [("nombre_usuario", 1)],
            unique=True,
            name="uq_usuarios_nombre_usuario",
        )

    async def crear(self, usuario: Usuario) -> None:
        """Inserta un Usuario y traduce conflictos tecnológicos."""
        try:
            await self._coleccion.insert_one(self._a_documento(usuario))
        except DuplicateKeyError as error:
            self._traducir_duplicado(error)

    async def obtener_por_identidad(self, identidad: IdentidadOidc) -> Usuario | None:
        documento = await self._coleccion.find_one(
            {"issuer": identidad.issuer, "subject": identidad.subject}
        )
        return self._a_entidad(documento) if documento is not None else None

    async def obtener_por_id(self, usuario_id: str) -> Usuario | None:
        documento = await self._coleccion.find_one({"_id": usuario_id})
        return self._a_entidad(documento) if documento is not None else None

    async def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        documento = await self._coleccion.find_one({"nombre_usuario": nombre_usuario})
        return self._a_entidad(documento) if documento is not None else None

    async def actualizar(self, usuario: Usuario) -> None:
        try:
            await self._coleccion.update_one(
                {"_id": usuario.id},
                {
                    "$set": {
                        "nombre": usuario.nombre,
                        "nombre_usuario": usuario.nombre_usuario,
                    }
                },
            )
        except DuplicateKeyError as error:
            self._traducir_duplicado(error)

    @staticmethod
    def _a_documento(usuario: Usuario) -> dict[str, str]:
        return {
            "_id": usuario.id,
            "issuer": usuario.identidad.issuer,
            "subject": usuario.identidad.subject,
            "nombre": usuario.nombre,
            "nombre_usuario": usuario.nombre_usuario,
        }

    @staticmethod
    def _a_entidad(documento: Mapping[str, Any]) -> Usuario:
        return Usuario(
            id=str(documento["_id"]),
            identidad=IdentidadOidc(
                issuer=str(documento["issuer"]),
                subject=str(documento["subject"]),
            ),
            nombre=str(documento["nombre"]),
            nombre_usuario=str(documento["nombre_usuario"]),
        )

    @staticmethod
    def _traducir_duplicado(error: DuplicateKeyError) -> None:
        detalles = getattr(error, "details", None) or {}
        patron = detalles.get("keyPattern", {})
        if "nombre_usuario" in patron:
            raise NombreUsuarioDuplicado from error
        raise IdentidadDuplicada from error
