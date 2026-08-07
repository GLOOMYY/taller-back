"""Puertos de Dispositivos y contratos explícitos entre módulos."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol

from app.modules.dispositivos.domain import Dispositivo
from app.shared.application.contexto import ContextoTaller

BuscadorReferencia = Callable[[ContextoTaller, str], Awaitable[object]]


@dataclass(frozen=True, slots=True)
class PaginaDispositivos:
    items: tuple[Dispositivo, ...]
    siguiente_cursor: str | None


class RepositorioDispositivos(Protocol):
    async def crear(
        self, contexto: ContextoTaller, dispositivo: Dispositivo
    ) -> Dispositivo: ...

    async def listar_por_cliente(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaDispositivos: ...

    async def obtener(
        self, contexto: ContextoTaller, dispositivo_id: str
    ) -> Dispositivo | None: ...

    async def actualizar(
        self, contexto: ContextoTaller, dispositivo: Dispositivo
    ) -> Dispositivo | None: ...
