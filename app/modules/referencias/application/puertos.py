"""Puertos de lectura del catálogo ISO global."""

from typing import Protocol

from app.modules.referencias.domain import Moneda, Pais


class RepositorioReferencias(Protocol):
    """Lecturas globales de referencias administradas por el sistema."""

    async def listar_paises(self) -> tuple[Pais, ...]: ...

    async def listar_monedas(self) -> tuple[Moneda, ...]: ...

    async def obtener_pais(self, codigo: str) -> Pais | None: ...

    async def obtener_moneda(self, codigo: str) -> Moneda | None: ...
