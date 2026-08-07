"""Contrato HTTP aislado de referencias, catálogos y Dispositivos."""

from decimal import Decimal
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.http import configurar_http
from app.modules.catalogos.application.puertos import PaginaCatalogo
from app.modules.catalogos.application.servicio import ServicioCatalogos
from app.modules.catalogos.domain import (
    MarcaDispositivo,
    ModeloDispositivo,
    TipoDispositivo,
    TipoServicio,
)
from app.modules.catalogos.presentation.router import crear_router_catalogos
from app.modules.dispositivos.application.puertos import PaginaDispositivos
from app.modules.dispositivos.application.servicio import ServicioDispositivos
from app.modules.dispositivos.domain import Dispositivo
from app.modules.dispositivos.presentation.router import crear_router_dispositivos
from app.modules.referencias.application.servicio import ServicioReferencias
from app.modules.referencias.domain import Moneda, Pais
from app.modules.referencias.presentation.router import crear_router_referencias
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class ReferenciasStub:
    async def listar_paises(self) -> tuple[Pais, ...]:
        return (Pais("CO", "Colombia"),)

    async def listar_monedas(self) -> tuple[Moneda, ...]:
        return (Moneda("COP", "Peso colombiano", "$", 2),)


class CatalogosStub:
    async def crear_tipo(
        self, contexto: ContextoTaller, nombre: str
    ) -> TipoDispositivo:
        return TipoDispositivo("tipo-1", contexto.taller_id, nombre, nombre.casefold())

    async def crear_marca(
        self, contexto: ContextoTaller, nombre: str
    ) -> MarcaDispositivo:
        return MarcaDispositivo(
            "marca-1", contexto.taller_id, nombre, nombre.casefold()
        )

    async def crear_modelo(
        self,
        contexto: ContextoTaller,
        *,
        nombre: str,
        tipo_id: str,
        marca_id: str,
    ) -> ModeloDispositivo:
        return ModeloDispositivo(
            "modelo-1",
            contexto.taller_id,
            nombre,
            nombre.casefold(),
            True,
            tipo_id,
            marca_id,
        )

    async def crear_tipo_servicio(
        self,
        contexto: ContextoTaller,
        *,
        nombre: str,
        descripcion: str | None,
        precio_predeterminado: Decimal,
    ) -> TipoServicio:
        return TipoServicio(
            "servicio-1",
            contexto.taller_id,
            nombre,
            nombre.casefold(),
            True,
            descripcion,
            precio_predeterminado,
        )

    async def listar(
        self,
        contexto: ContextoTaller,
        clase: str,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaCatalogo[TipoDispositivo]:
        del contexto, clase, limite, cursor
        return PaginaCatalogo((), None)


class DispositivosStub:
    async def crear(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        modelo_id: str,
        identificador: str | None,
        notas: str | None,
    ) -> Dispositivo:
        return Dispositivo(
            "dispositivo-1",
            contexto.taller_id,
            cliente_id,
            modelo_id,
            identificador,
            notas,
        )

    async def listar_por_cliente(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaDispositivos:
        del contexto, cliente_id, limite, cursor
        return PaginaDispositivos((), None)


def construir_api() -> TestClient:
    referencias = ReferenciasStub()
    catalogos = CatalogosStub()
    dispositivos = DispositivosStub()

    def contexto(taller_id: str) -> ContextoTaller:
        return ContextoTaller("usuario", taller_id, "tecnico")

    def identidad() -> ContextoIdentidad:
        return ContextoIdentidad("usuario", "https://issuer.example/", "subject")

    def servicio_referencias() -> ServicioReferencias:
        return cast(ServicioReferencias, referencias)

    def servicio_catalogos() -> ServicioCatalogos:
        return cast(ServicioCatalogos, catalogos)

    def servicio_dispositivos() -> ServicioDispositivos:
        return cast(ServicioDispositivos, dispositivos)

    app = FastAPI()
    configurar_http(app)
    app.include_router(
        crear_router_referencias(servicio_referencias, identidad), prefix="/api/v1"
    )
    app.include_router(
        crear_router_catalogos(servicio_catalogos, contexto), prefix="/api/v1"
    )
    app.include_router(
        crear_router_dispositivos(servicio_dispositivos, contexto), prefix="/api/v1"
    )
    return TestClient(app)


def test_referencias_son_legibles_y_catalogos_crean_recursos() -> None:
    cliente = construir_api()

    paises = cliente.get("/api/v1/referencias/paises")
    tipo = cliente.post(
        "/api/v1/talleres/taller-a/tipos-dispositivo", json={"nombre": "Celular"}
    )
    marca = cliente.post(
        "/api/v1/talleres/taller-a/marcas-dispositivo", json={"nombre": "Samsung"}
    )
    modelo = cliente.post(
        "/api/v1/talleres/taller-a/modelos-dispositivo",
        json={"nombre": "A55", "tipo_id": "tipo-1", "marca_id": "marca-1"},
    )
    servicio = cliente.post(
        "/api/v1/talleres/taller-a/tipos-servicio",
        json={"nombre": "Domicilio", "precio_predeterminado": "25000.00"},
    )

    assert paises.json() == [{"codigo": "CO", "nombre": "Colombia"}]
    assert tipo.status_code == marca.status_code == modelo.status_code == 201
    assert servicio.json()["precio_predeterminado"] == "25000.00"


def test_dispositivo_se_crea_bajo_cliente_sin_endpoint_delete() -> None:
    cliente = construir_api()
    creado = cliente.post(
        "/api/v1/talleres/taller-a/clientes/cliente-1/dispositivos",
        json={"modelo_id": "modelo-1", "identificador": "SN-1"},
    )

    assert creado.status_code == 201
    assert creado.json()["cliente_id"] == "cliente-1"
    assert (
        cliente.delete(
            "/api/v1/talleres/taller-a/dispositivos/dispositivo-1"
        ).status_code
        == 405
    )
