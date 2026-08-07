"""Puertos de persistencia y contratos públicos de catálogos."""

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from app.modules.catalogos.domain import (
    EntradaCatalogo,
    MarcaDispositivo,
    ModeloDispositivo,
    TipoDispositivo,
    TipoServicio,
)
from app.shared.application.contexto import ContextoTaller

T = TypeVar("T", bound=EntradaCatalogo)


@dataclass(frozen=True, slots=True)
class PaginaCatalogo(Generic[T]):
    items: tuple[T, ...]
    siguiente_cursor: str | None


class RepositorioCatalogos(Protocol):
    async def crear_tipo(
        self, contexto: ContextoTaller, item: TipoDispositivo
    ) -> TipoDispositivo: ...

    async def crear_marca(
        self, contexto: ContextoTaller, item: MarcaDispositivo
    ) -> MarcaDispositivo: ...

    async def crear_modelo(
        self, contexto: ContextoTaller, item: ModeloDispositivo
    ) -> ModeloDispositivo: ...

    async def crear_tipo_servicio(
        self, contexto: ContextoTaller, item: TipoServicio
    ) -> TipoServicio: ...

    async def listar_tipos(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[TipoDispositivo]: ...

    async def listar_marcas(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[MarcaDispositivo]: ...

    async def listar_modelos(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[ModeloDispositivo]: ...

    async def listar_tipos_servicio(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[TipoServicio]: ...

    async def obtener_tipo(
        self, contexto: ContextoTaller, item_id: str
    ) -> TipoDispositivo | None: ...

    async def obtener_marca(
        self, contexto: ContextoTaller, item_id: str
    ) -> MarcaDispositivo | None: ...

    async def obtener_modelo(
        self, contexto: ContextoTaller, item_id: str
    ) -> ModeloDispositivo | None: ...

    async def obtener_tipo_servicio(
        self, contexto: ContextoTaller, item_id: str
    ) -> TipoServicio | None: ...

    async def actualizar_tipo(
        self, contexto: ContextoTaller, item: TipoDispositivo
    ) -> TipoDispositivo | None: ...

    async def actualizar_marca(
        self, contexto: ContextoTaller, item: MarcaDispositivo
    ) -> MarcaDispositivo | None: ...

    async def actualizar_modelo(
        self, contexto: ContextoTaller, item: ModeloDispositivo
    ) -> ModeloDispositivo | None: ...

    async def actualizar_tipo_servicio(
        self, contexto: ContextoTaller, item: TipoServicio
    ) -> TipoServicio | None: ...
