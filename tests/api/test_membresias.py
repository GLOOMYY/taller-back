"""Contrato HTTP y política de divulgación de Membresías."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.http import configurar_http
from app.modules.membresias.domain.modelos import Membresia, RolMembresia
from app.modules.membresias.presentation.router import create_router
from app.shared.application import NoEncontrado, Prohibido
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class ServicioFalso:
    """Doble enfocado en traducción y wiring del router."""

    async def resolver_contexto_taller(
        self, identidad: ContextoIdentidad, taller_id: str
    ) -> ContextoTaller:
        if taller_id == "ajeno":
            raise NoEncontrado("Taller no encontrado")
        rol = "tecnico" if identidad.usuario_id == "tecnico" else "dueno"
        return ContextoTaller(identidad.usuario_id, taller_id, rol)

    async def listar(
        self, contexto: ContextoTaller, limite: int, cursor: str | None
    ) -> list[Membresia]:
        del limite, cursor
        return [Membresia("mem-1", contexto.taller_id, "dueno", RolMembresia.DUENO)]

    async def agregar(
        self,
        contexto: ContextoTaller,
        nombre_usuario: str,
        rol: RolMembresia,
    ) -> Membresia:
        if contexto.rol != "dueno":
            raise Prohibido()
        assert nombre_usuario == "nuevo.usuario"
        return Membresia("mem-2", contexto.taller_id, "nuevo", rol)

    async def cambiar_rol(
        self, contexto: ContextoTaller, usuario_id: str, rol: RolMembresia
    ) -> Membresia:
        return Membresia("mem-2", contexto.taller_id, usuario_id, rol)

    async def retirar(self, contexto: ContextoTaller, usuario_id: str) -> None:
        assert contexto.taller_id == "taller-a"
        assert usuario_id == "nuevo"


def crear_cliente(usuario_id: str = "dueno") -> TestClient:
    app = FastAPI()
    configurar_http(app)

    async def identidad(request: Request) -> ContextoIdentidad:
        del request
        return ContextoIdentidad(usuario_id, "https://issuer", f"sub-{usuario_id}")

    app.include_router(
        create_router(ServicioFalso(), identidad),
        prefix="/api/v1",  # type: ignore[arg-type]
    )
    return TestClient(app)


def test_flujo_http_listar_agregar_cambiar_y_retirar() -> None:
    cliente = crear_cliente()

    listado = cliente.get("/api/v1/talleres/taller-a/miembros")
    creado = cliente.post(
        "/api/v1/talleres/taller-a/miembros",
        json={"nombre_usuario": "  @NUEVO.USUARIO ", "rol": "tecnico"},
    )
    cambiado = cliente.patch(
        "/api/v1/talleres/taller-a/miembros/nuevo", json={"rol": "dueno"}
    )
    retirado = cliente.delete("/api/v1/talleres/taller-a/miembros/nuevo")

    assert listado.status_code == 200
    assert listado.json()["items"][0]["taller_id"] == "taller-a"
    assert creado.status_code == 201
    assert creado.json()["rol"] == "tecnico"
    assert cambiado.status_code == 200
    assert cambiado.json()["rol"] == "dueno"
    assert retirado.status_code == 204


def test_tecnico_miembro_recibe_403_al_administrar() -> None:
    respuesta = crear_cliente("tecnico").post(
        "/api/v1/talleres/taller-a/miembros",
        json={"nombre_usuario": "nuevo.usuario", "rol": "tecnico"},
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"


def test_taller_sin_membresia_se_oculta_como_404() -> None:
    respuesta = crear_cliente().get("/api/v1/talleres/ajeno/miembros")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "no_encontrado"


def test_nombre_usuario_invalido_es_422() -> None:
    respuesta = crear_cliente().post(
        "/api/v1/talleres/taller-a/miembros",
        json={"nombre_usuario": "No Valido", "rol": "tecnico"},
    )

    assert respuesta.status_code == 422
