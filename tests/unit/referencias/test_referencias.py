"""Pruebas del contrato de referencias ISO."""

import pytest

from app.modules.referencias.application.servicio import (
    ReferenciaNoEncontrada,
    ServicioReferencias,
)
from app.modules.referencias.domain import Moneda, Pais


class Repositorio:
    async def listar_paises(self) -> tuple[Pais, ...]:
        return (Pais("CO", "Colombia"),)

    async def listar_monedas(self) -> tuple[Moneda, ...]:
        return (Moneda("COP", "Peso colombiano", "$", 2),)

    async def obtener_pais(self, codigo: str) -> Pais | None:
        return Pais("CO", "Colombia") if codigo == "CO" else None

    async def obtener_moneda(self, codigo: str) -> Moneda | None:
        return Moneda("COP", "Peso colombiano", "$", 2) if codigo == "COP" else None


@pytest.mark.asyncio
async def test_codigos_se_normalizan_y_ausentes_no_se_inventan() -> None:
    servicio = ServicioReferencias(Repositorio())

    assert (await servicio.obtener_pais(" co ")).nombre == "Colombia"
    assert (await servicio.obtener_moneda("cop")).decimales == 2
    with pytest.raises(ReferenciaNoEncontrada):
        await servicio.obtener_pais("XX")
