"""Pruebas unitarias de los casos de uso de Clientes."""

import asyncio
from dataclasses import replace

import pytest

from app.modules.clientes.application.casos_de_uso import ServicioClientes
from app.modules.clientes.application.errores import ClienteNoEncontrado
from app.modules.clientes.application.puertos import PaginaClientes
from app.modules.clientes.domain.entidades import CambiosCliente, Cliente
from app.shared.application.contexto import ContextoTaller


class RepositorioEnMemoria:
    """Doble tenant-aware del puerto para pruebas de Application."""

    def __init__(self) -> None:
        self.items: dict[str, Cliente] = {}
        self.siguiente = 1

    async def crear(self, contexto: ContextoTaller, cliente: Cliente) -> Cliente:
        assert contexto.taller_id == cliente.taller_id
        guardado = replace(cliente, id=f"cliente-{self.siguiente}")
        self.siguiente += 1
        assert guardado.id is not None
        self.items[guardado.id] = guardado
        return guardado

    async def listar(
        self,
        contexto: ContextoTaller,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaClientes:
        del cursor
        visibles = tuple(
            item for item in self.items.values() if item.taller_id == contexto.taller_id
        )[:limite]
        return PaginaClientes(visibles, None)

    async def obtener(
        self, contexto: ContextoTaller, cliente_id: str
    ) -> Cliente | None:
        cliente = self.items.get(cliente_id)
        if cliente is None or cliente.taller_id != contexto.taller_id:
            return None
        return cliente

    async def actualizar(
        self, contexto: ContextoTaller, cliente: Cliente
    ) -> Cliente | None:
        if cliente.taller_id != contexto.taller_id or cliente.id is None:
            return None
        existente = await self.obtener(contexto, cliente.id)
        if existente is None:
            return None
        self.items[cliente.id] = cliente
        return cliente


def contexto(taller_id: str) -> ContextoTaller:
    """Crea un contexto autorizado mínimo."""
    return ContextoTaller(
        usuario_id=f"usuario-{taller_id}", taller_id=taller_id, rol="tecnico"
    )


def test_crear_y_listar_solo_devuelve_clientes_del_taller() -> None:
    """BR-005/BR-007: la misma capa Application preserva aislamiento."""

    async def escenario() -> None:
        repositorio = RepositorioEnMemoria()
        servicio = ServicioClientes(repositorio)
        await servicio.crear(contexto("taller-a"), nombre="Isabella")
        await servicio.crear(contexto("taller-b"), nombre="Beto")

        pagina = await servicio.listar(contexto("taller-a"))

        assert [cliente.nombre for cliente in pagina.items] == ["Isabella"]

    asyncio.run(escenario())


def test_id_de_otro_taller_no_se_revela() -> None:
    """AC-021: un id cruzado obtiene el mismo resultado que uno ausente."""

    async def escenario() -> None:
        repositorio = RepositorioEnMemoria()
        servicio = ServicioClientes(repositorio)
        ajeno = await servicio.crear(contexto("taller-b"), nombre="Beto")
        assert ajeno.id is not None

        with pytest.raises(ClienteNoEncontrado):
            await servicio.obtener(contexto("taller-a"), ajeno.id)
        with pytest.raises(ClienteNoEncontrado):
            await servicio.obtener(contexto("taller-a"), "inexistente")

    asyncio.run(escenario())


def test_no_se_puede_editar_cliente_de_otro_taller() -> None:
    """BR-007: la edición siempre usa el contexto tenant."""

    async def escenario() -> None:
        repositorio = RepositorioEnMemoria()
        servicio = ServicioClientes(repositorio)
        ajeno = await servicio.crear(contexto("taller-b"), nombre="Beto")
        assert ajeno.id is not None

        with pytest.raises(ClienteNoEncontrado):
            await servicio.actualizar(
                contexto("taller-a"),
                ajeno.id,
                CambiosCliente(nombre_definido=True, nombre="Intruso"),
            )

        conservado = await servicio.obtener(contexto("taller-b"), ajeno.id)
        assert conservado.nombre == "Beto"

    asyncio.run(escenario())


@pytest.mark.parametrize("limite", [0, 101])
def test_limite_fuera_de_rango_es_invalido(limite: int) -> None:
    """AC-022: el límite permitido es 1..100."""

    async def escenario() -> None:
        servicio = ServicioClientes(RepositorioEnMemoria())
        with pytest.raises(ValueError):
            await servicio.listar(contexto("taller-a"), limite=limite)

    asyncio.run(escenario())
