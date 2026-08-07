"""Pruebas Application de Dispositivos."""

from dataclasses import replace

import pytest

from app.modules.dispositivos.application.puertos import PaginaDispositivos
from app.modules.dispositivos.application.servicio import (
    DispositivoNoEncontrado,
    ServicioDispositivos,
)
from app.modules.dispositivos.domain import CambiosDispositivo, Dispositivo
from app.shared.application.contexto import ContextoTaller
from app.shared.application.errores import NoEncontrado


class Repositorio:
    def __init__(self) -> None:
        self.items: dict[str, Dispositivo] = {}

    async def crear(
        self, contexto: ContextoTaller, dispositivo: Dispositivo
    ) -> Dispositivo:
        item = replace(dispositivo, id=f"d-{len(self.items) + 1}")
        assert item.id is not None and contexto.taller_id == item.taller_id
        self.items[item.id] = item
        return item

    async def listar_por_cliente(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaDispositivos:
        del cursor
        return PaginaDispositivos(
            tuple(
                item
                for item in self.items.values()
                if item.taller_id == contexto.taller_id
                and item.cliente_id == cliente_id
            )[:limite],
            None,
        )

    async def obtener(
        self, contexto: ContextoTaller, dispositivo_id: str
    ) -> Dispositivo | None:
        item = self.items.get(dispositivo_id)
        return (
            item if item is not None and item.taller_id == contexto.taller_id else None
        )

    async def actualizar(
        self, contexto: ContextoTaller, dispositivo: Dispositivo
    ) -> Dispositivo | None:
        if (
            dispositivo.id is None
            or await self.obtener(contexto, dispositivo.id) is None
        ):
            return None
        self.items[dispositivo.id] = dispositivo
        return dispositivo


def contexto(taller_id: str) -> ContextoTaller:
    return ContextoTaller("usuario", taller_id, "tecnico")


@pytest.mark.asyncio
async def test_crear_editar_sin_reasignar_cliente_y_aislar_tenant() -> None:
    async def obtener_cliente(ctx: ContextoTaller, item_id: str) -> object:
        if (ctx.taller_id, item_id) not in {("a", "cliente-a"), ("b", "cliente-b")}:
            raise NoEncontrado()
        return object()

    async def obtener_modelo(ctx: ContextoTaller, item_id: str) -> object:
        if item_id != f"modelo-{ctx.taller_id}":
            raise NoEncontrado()
        return object()

    servicio = ServicioDispositivos(Repositorio(), obtener_cliente, obtener_modelo)
    item = await servicio.crear(
        contexto("a"), "cliente-a", modelo_id="modelo-a", identificador="IMEI"
    )
    assert item.id is not None

    editado = await servicio.actualizar(
        contexto("a"), item.id, CambiosDispositivo(notas_definidas=True, notas="ok")
    )

    assert editado.cliente_id == "cliente-a"
    with pytest.raises(DispositivoNoEncontrado):
        await servicio.obtener(contexto("b"), item.id)
    with pytest.raises(NoEncontrado):
        await servicio.crear(contexto("a"), "cliente-b", modelo_id="modelo-a")
