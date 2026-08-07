"""Puertos requeridos por los casos de uso de Talleres."""

from collections.abc import Sequence
from typing import Protocol, Self

from app.modules.talleres.domain.modelos import Taller


class RepositorioTalleres(Protocol):
    """Consultas y mutaciones tenant-aware de Talleres."""

    async def obtener(self, taller_id: str) -> Taller | None:
        """Obtiene un Taller por identificador opaco."""
        ...

    async def listar_accesibles(
        self,
        taller_ids: Sequence[str],
        *,
        cursor: str | None,
        limite: int,
    ) -> list[Taller]:
        """Lista solo Talleres previamente autorizados, con un elemento extra."""
        ...

    async def actualizar(self, taller: Taller) -> None:
        """Persiste cambios sobre un Taller autorizado."""
        ...

    async def referencias_validas(self, pais_codigo: str, moneda_codigo: str) -> bool:
        """Comprueba catálogos ISO globales sin relacionar país con moneda."""
        ...


class DirectorioAccesoTalleres(Protocol):
    """Vista pública de Membresías para descubrir Talleres accesibles."""

    async def listar_taller_ids(self, usuario_id: str) -> Sequence[str]:
        """Devuelve identificadores de Talleres con Membresía vigente."""
        ...


class UnidadCreacionTaller(Protocol):
    """Transacción Taller–Membresía dueño provista desde composición."""

    async def __aenter__(self) -> Self:
        """Inicia la unidad transaccional."""
        ...

    async def __aexit__(
        self,
        tipo_error: type[BaseException] | None,
        error: BaseException | None,
        traza: object | None,
    ) -> bool | None:
        """Confirma o revierte la unidad transaccional."""
        ...

    async def guardar_taller(self, taller: Taller) -> None:
        """Persiste el Taller en la transacción actual."""
        ...

    async def crear_membresia_dueno(self, taller_id: str, usuario_id: str) -> None:
        """Crea al creador como dueño en la misma transacción."""
        ...

    async def crear_metodo_efectivo(self, taller_id: str) -> None:
        """Crea el método inicial dentro de la misma transacción."""
        ...


class GeneradorId(Protocol):
    """Genera identificadores opacos."""

    def generar(self) -> str:
        """Genera un identificador nuevo."""
        ...
