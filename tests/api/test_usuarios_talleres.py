"""Contrato HTTP de Usuarios y Talleres."""

from collections.abc import Sequence

import httpx
import pytest
from fastapi import FastAPI

from app.modules.talleres.application.casos_uso import ServicioTalleres
from app.modules.talleres.domain.modelos import Taller
from app.modules.talleres.presentation.router import create_router as router_talleres
from app.modules.usuarios.application.casos_uso import ServicioUsuarios
from app.modules.usuarios.domain.modelos import IdentidadOidc, Usuario
from app.modules.usuarios.presentation.router import create_router as router_usuarios
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class Generador:
    def __init__(self, valor: str):
        self.valor = valor

    def generar(self) -> str:
        return self.valor


class UsuariosMemoria:
    def __init__(self) -> None:
        self.usuario: Usuario | None = None

    async def crear(self, usuario: Usuario) -> None:
        self.usuario = usuario

    async def obtener_por_identidad(self, identidad: IdentidadOidc) -> Usuario | None:
        if self.usuario and self.usuario.identidad == identidad:
            return self.usuario
        return None

    async def obtener_por_id(self, usuario_id: str) -> Usuario | None:
        return self.usuario if self.usuario and self.usuario.id == usuario_id else None

    async def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        if self.usuario and self.usuario.nombre_usuario == nombre_usuario:
            return self.usuario
        return None

    async def actualizar(self, usuario: Usuario) -> None:
        self.usuario = usuario


class TalleresMemoria:
    def __init__(self) -> None:
        self.talleres: dict[str, Taller] = {}

    async def obtener(self, taller_id: str) -> Taller | None:
        return self.talleres.get(taller_id)

    async def listar_accesibles(
        self,
        taller_ids: Sequence[str],
        *,
        cursor: str | None,
        limite: int,
    ) -> list[Taller]:
        ids = sorted(item for item in taller_ids if cursor is None or item > cursor)
        return [self.talleres[item] for item in ids[:limite] if item in self.talleres]

    async def actualizar(self, taller: Taller) -> None:
        self.talleres[taller.id] = taller


class Accesos:
    async def listar_taller_ids(self, usuario_id: str) -> list[str]:
        return ["taller-1"]


class Unidad:
    def __init__(self, repositorio: TalleresMemoria):
        self.repositorio = repositorio

    async def __aenter__(self) -> "Unidad":
        return self

    async def __aexit__(
        self,
        tipo_error: type[BaseException] | None,
        error: BaseException | None,
        traza: object | None,
    ) -> bool | None:
        return None

    async def guardar_taller(self, taller: Taller) -> None:
        self.repositorio.talleres[taller.id] = taller

    async def crear_membresia_dueno(self, taller_id: str, usuario_id: str) -> None:
        return None


@pytest.fixture
def api() -> FastAPI:
    aplicacion = FastAPI()
    identidad_oidc = IdentidadOidc("https://issuer.example", "subject")
    contexto_identidad = ContextoIdentidad(
        "usuario-1", identidad_oidc.issuer, identidad_oidc.subject
    )
    talleres = TalleresMemoria()

    async def obtener_oidc() -> IdentidadOidc:
        return identidad_oidc

    async def obtener_identidad() -> ContextoIdentidad:
        return contexto_identidad

    async def obtener_contexto(taller_id: str) -> ContextoTaller:
        return ContextoTaller("usuario-1", taller_id, "tecnico")

    servicio_usuarios = ServicioUsuarios(UsuariosMemoria(), Generador("usuario-1"))
    unidad = Unidad(talleres)
    servicio_talleres = ServicioTalleres(
        talleres, Accesos(), lambda: unidad, Generador("taller-1")
    )
    aplicacion.include_router(
        router_usuarios(servicio_usuarios, obtener_oidc), prefix="/api/v1"
    )
    aplicacion.include_router(
        router_talleres(servicio_talleres, obtener_identidad, obtener_contexto),
        prefix="/api/v1",
    )
    return aplicacion


@pytest.mark.asyncio
async def test_flujo_http_usuario_y_taller(api: FastAPI) -> None:
    transporte = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(
        transport=transporte, base_url="http://test"
    ) as cliente:
        usuario = await cliente.post(
            "/api/v1/usuarios/me",
            json={"nombre": "Isabella", "nombre_usuario": "@ISABELLA.01"},
        )
        taller = await cliente.post(
            "/api/v1/talleres",
            json={
                "nombre": "Taller Norte",
                "pais_codigo": "CO",
                "moneda_codigo": "COP",
            },
        )
        consulta = await cliente.get("/api/v1/talleres/taller-1")

    assert usuario.status_code == 201
    assert usuario.json()["nombre_usuario"] == "isabella.01"
    assert taller.status_code == 201
    assert consulta.json() == {
        "id": "taller-1",
        "nombre": "Taller Norte",
        "pais_codigo": "CO",
        "moneda_codigo": "COP",
        "rol_actual": "tecnico",
    }


@pytest.mark.asyncio
async def test_api_rechaza_nombre_usuario_invalido_y_limite_excesivo(
    api: FastAPI,
) -> None:
    transporte = httpx.ASGITransport(app=api)
    async with httpx.AsyncClient(
        transport=transporte, base_url="http://test"
    ) as cliente:
        usuario = await cliente.post(
            "/api/v1/usuarios/me",
            json={"nombre": "Isabella", "nombre_usuario": "a-b"},
        )
        talleres = await cliente.get("/api/v1/talleres?limite=101")

    assert usuario.status_code == 422
    assert talleres.status_code == 422
