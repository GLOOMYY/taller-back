"""Casos de uso de referencias ISO."""

from app.modules.referencias.application.puertos import RepositorioReferencias
from app.modules.referencias.domain import Moneda, Pais
from app.shared.application.errores import NoEncontrado


class ReferenciaNoEncontrada(NoEncontrado):
    """Una referencia ISO solicitada no existe."""


class ServicioReferencias:
    """Expone catálogos ISO globales como lecturas de solo consulta."""

    def __init__(self, repositorio: RepositorioReferencias) -> None:
        self._repositorio = repositorio

    async def listar_paises(self) -> tuple[Pais, ...]:
        return await self._repositorio.listar_paises()

    async def listar_monedas(self) -> tuple[Moneda, ...]:
        return await self._repositorio.listar_monedas()

    async def obtener_pais(self, codigo: str) -> Pais:
        pais = await self._repositorio.obtener_pais(codigo.strip().upper())
        if pais is None:
            raise ReferenciaNoEncontrada("El país no está disponible.")
        return pais

    async def obtener_moneda(self, codigo: str) -> Moneda:
        moneda = await self._repositorio.obtener_moneda(codigo.strip().upper())
        if moneda is None:
            raise ReferenciaNoEncontrada("La moneda no está disponible.")
        return moneda
