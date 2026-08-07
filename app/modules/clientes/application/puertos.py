"""Puertos de persistencia requeridos por Clientes."""

from dataclasses import dataclass
from typing import Protocol

from app.modules.clientes.domain.entidades import Cliente
from app.shared.application.contexto import ContextoTaller


@dataclass(frozen=True, slots=True)
class PaginaClientes:
    """Página estable de Clientes y cursor opaco de continuación."""

    items: tuple[Cliente, ...]
    siguiente_cursor: str | None


class RepositorioClientes(Protocol):
    """Persistencia tenant-scoped requerida por los casos de uso."""

    async def crear(self, contexto: ContextoTaller, cliente: Cliente) -> Cliente:
        """Persiste un Cliente nuevo dentro del Taller autorizado."""
        ...

    async def listar(
        self,
        contexto: ContextoTaller,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaClientes:
        """Lista Clientes del Taller con orden determinista."""
        ...

    async def obtener(
        self, contexto: ContextoTaller, cliente_id: str
    ) -> Cliente | None:
        """Obtiene un Cliente solo si pertenece al Taller autorizado."""
        ...

    async def actualizar(
        self, contexto: ContextoTaller, cliente: Cliente
    ) -> Cliente | None:
        """Actualiza un Cliente solo si pertenece al Taller autorizado."""
        ...
