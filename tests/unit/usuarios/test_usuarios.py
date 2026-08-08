"""Pruebas unitarias del módulo Usuarios."""

from dataclasses import dataclass

import pytest

from app.modules.usuarios.application.casos_uso import ServicioUsuarios
from app.modules.usuarios.domain.modelos import (
    IdentidadOidc,
    NombreUsuarioInvalido,
    Usuario,
    normalizar_nombre_usuario,
)
from app.shared.application import Conflicto, NoAutenticado


class RepositorioUsuariosMemoria:
    def __init__(self) -> None:
        self.usuarios: dict[str, Usuario] = {}

    async def crear(self, usuario: Usuario) -> None:
        self.usuarios[usuario.id] = usuario

    async def obtener_por_identidad(self, identidad: IdentidadOidc) -> Usuario | None:
        return next(
            (item for item in self.usuarios.values() if item.identidad == identidad),
            None,
        )

    async def obtener_por_id(self, usuario_id: str) -> Usuario | None:
        return self.usuarios.get(usuario_id)

    async def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Usuario | None:
        return next(
            (
                item
                for item in self.usuarios.values()
                if item.nombre_usuario == nombre_usuario
            ),
            None,
        )

    async def actualizar(self, usuario: Usuario) -> None:
        self.usuarios[usuario.id] = usuario


@dataclass
class GeneradorFijo:
    valor: str = "usuario-1"

    def generar(self) -> str:
        return self.valor


def test_normaliza_arroba_mayusculas_y_espacios() -> None:
    """BR-015/AC-016: el identificador global usa forma canónica."""
    assert normalizar_nombre_usuario("  @Isabella.01 ") == "isabella.01"


@pytest.mark.parametrize("valor", ["ab", "a-b", "ábc", "nombre usuario", "a" * 31])
def test_rechaza_nombre_usuario_fuera_del_contrato(valor: str) -> None:
    with pytest.raises(NombreUsuarioInvalido):
        normalizar_nombre_usuario(valor)


@pytest.mark.asyncio
async def test_registra_y_actualiza_el_perfil_actual() -> None:
    repositorio = RepositorioUsuariosMemoria()
    servicio = ServicioUsuarios(repositorio, GeneradorFijo())
    identidad = IdentidadOidc("https://issuer.example", "sub-1")

    creado = await servicio.registrar(
        identidad, nombre=" Isabella ", nombre_usuario="@Isabella.01"
    )
    actualizado = await servicio.actualizar(
        identidad, nombre="Isabella María", nombre_usuario="isabella_01"
    )

    assert creado.nombre_usuario == "isabella.01"
    assert actualizado.nombre == "Isabella María"
    assert actualizado.nombre_usuario == "isabella_01"


@pytest.mark.asyncio
async def test_nombre_usuario_es_unico_globalmente() -> None:
    repositorio = RepositorioUsuariosMemoria()
    servicio = ServicioUsuarios(repositorio, GeneradorFijo())
    await servicio.registrar(
        IdentidadOidc("issuer", "uno"), nombre="Uno", nombre_usuario="global"
    )

    with pytest.raises(Conflicto):
        await ServicioUsuarios(repositorio, GeneradorFijo("usuario-2")).registrar(
            IdentidadOidc("issuer", "dos"),
            nombre="Dos",
            nombre_usuario="@GLOBAL",
        )


@pytest.mark.asyncio
async def test_identidad_oidc_es_unica() -> None:
    repositorio = RepositorioUsuariosMemoria()
    servicio = ServicioUsuarios(repositorio, GeneradorFijo())
    identidad = IdentidadOidc("issuer", "subject")
    await servicio.registrar(identidad, nombre="Uno", nombre_usuario="uno")

    with pytest.raises(Conflicto):
        await servicio.registrar(identidad, nombre="Otro", nombre_usuario="otro")


@pytest.mark.asyncio
async def test_identidad_no_registrada_no_construye_usuario_interno() -> None:
    servicio = ServicioUsuarios(RepositorioUsuariosMemoria(), GeneradorFijo())

    with pytest.raises(NoAutenticado):
        await servicio.consultar(IdentidadOidc("issuer", "desconocido"))
