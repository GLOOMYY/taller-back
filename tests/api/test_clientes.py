"""Pruebas del contrato HTTP de Clientes con dependencias inyectadas."""

from dataclasses import replace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.http import configurar_http
from app.modules.clientes.application.casos_de_uso import ServicioClientes
from app.modules.clientes.application.puertos import PaginaClientes
from app.modules.clientes.domain.entidades import Cliente
from app.modules.clientes.presentation.router import crear_router
from app.shared.application.contexto import ContextoTaller


class RepositorioApi:
    """Doble tenant-aware usado solo por las pruebas de contrato."""

    def __init__(self) -> None:
        self.items: dict[str, Cliente] = {}
        self.secuencia = 1

    async def crear(self, contexto: ContextoTaller, cliente: Cliente) -> Cliente:
        assert cliente.taller_id == contexto.taller_id
        guardado = replace(cliente, id=f"cliente-{self.secuencia}")
        self.secuencia += 1
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
        items = tuple(
            cliente
            for cliente in self.items.values()
            if cliente.taller_id == contexto.taller_id
        )[:limite]
        return PaginaClientes(items, None)

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
        if cliente.id is None or await self.obtener(contexto, cliente.id) is None:
            return None
        self.items[cliente.id] = cliente
        return cliente


def construir_cliente() -> tuple[TestClient, RepositorioApi]:
    """Compone una API aislada como lo hará la application factory."""
    repositorio = RepositorioApi()
    servicio = ServicioClientes(repositorio)

    def obtener_servicio() -> ServicioClientes:
        return servicio

    def obtener_contexto(taller_id: str) -> ContextoTaller:
        return ContextoTaller(
            usuario_id="usuario-1", taller_id=taller_id, rol="tecnico"
        )

    app = FastAPI()
    configurar_http(app)
    app.include_router(
        crear_router(obtener_servicio, obtener_contexto), prefix="/api/v1"
    )
    return TestClient(app), repositorio


def test_flujo_crear_listar_obtener_y_editar() -> None:
    """RF-CLI-001/002: el contrato expone las operaciones aceptadas."""
    cliente_http, _ = construir_cliente()

    creado = cliente_http.post(
        "/api/v1/talleres/taller-a/clientes",
        json={"nombre": "Isabella", "telefono": "123"},
    )
    cliente_id = creado.json()["id"]
    listado = cliente_http.get("/api/v1/talleres/taller-a/clientes")
    obtenido = cliente_http.get(f"/api/v1/talleres/taller-a/clientes/{cliente_id}")
    editado = cliente_http.patch(
        f"/api/v1/talleres/taller-a/clientes/{cliente_id}",
        json={"telefono": None, "notas": "Prefiere la tarde"},
    )

    assert creado.status_code == 201
    assert len(listado.json()["items"]) == 1
    assert obtenido.json()["nombre"] == "Isabella"
    assert editado.json()["telefono"] is None
    assert editado.json()["notas"] == "Prefiere la tarde"


def test_cliente_cross_tenant_responde_404() -> None:
    """AC-021: no se revela la existencia en otro Taller."""
    cliente_http, _ = construir_cliente()
    creado = cliente_http.post(
        "/api/v1/talleres/taller-b/clientes", json={"nombre": "Beto"}
    )
    cliente_id = creado.json()["id"]

    respuesta = cliente_http.get(f"/api/v1/talleres/taller-a/clientes/{cliente_id}")

    assert respuesta.status_code == 404


def test_no_existe_delete_y_entradas_invalidas_son_422() -> None:
    """RF-CLI-002: no hay borrado; nombre y patch vacío se validan."""
    cliente_http, _ = construir_cliente()
    creado = cliente_http.post(
        "/api/v1/talleres/taller-a/clientes", json={"nombre": "Isabella"}
    )
    cliente_id = creado.json()["id"]

    assert (
        cliente_http.delete(
            f"/api/v1/talleres/taller-a/clientes/{cliente_id}"
        ).status_code
        == 405
    )
    assert (
        cliente_http.post(
            "/api/v1/talleres/taller-a/clientes", json={"nombre": " "}
        ).status_code
        == 422
    )
    assert (
        cliente_http.patch(
            f"/api/v1/talleres/taller-a/clientes/{cliente_id}", json={}
        ).status_code
        == 422
    )
