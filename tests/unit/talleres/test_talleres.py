"""Pruebas unitarias del módulo Talleres."""

from dataclasses import dataclass, field
from types import TracebackType

import pytest

from app.modules.talleres.application.casos_uso import ServicioTalleres
from app.modules.talleres.domain.modelos import Taller
from app.shared.application import NoEncontrado
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class RepositorioTalleresMemoria:
    def __init__(self, talleres: list[Taller] | None = None) -> None:
        self.talleres = {item.id: item for item in talleres or []}

    async def obtener(self, taller_id: str) -> Taller | None:
        return self.talleres.get(taller_id)

    async def listar_accesibles(
        self,
        taller_ids: list[str],
        *,
        cursor: str | None,
        limite: int,
    ) -> list[Taller]:
        ids = sorted(item for item in taller_ids if cursor is None or item > cursor)
        return [self.talleres[item] for item in ids[:limite] if item in self.talleres]

    async def actualizar(self, taller: Taller) -> None:
        self.talleres[taller.id] = taller


@dataclass
class AccesosMemoria:
    ids: list[str]

    async def listar_taller_ids(self, usuario_id: str) -> list[str]:
        return self.ids


@dataclass
class GeneradorFijo:
    valor: str = "taller-1"

    def generar(self) -> str:
        return self.valor


@dataclass
class UnidadMemoria:
    repositorio: RepositorioTalleresMemoria
    operaciones: list[tuple[str, ...]] = field(default_factory=list)

    async def __aenter__(self) -> "UnidadMemoria":
        self.operaciones.append(("iniciar",))
        return self

    async def __aexit__(
        self,
        tipo_error: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> bool | None:
        self.operaciones.append(("cerrar", "error" if error else "confirmar"))
        return None

    async def guardar_taller(self, taller: Taller) -> None:
        self.repositorio.talleres[taller.id] = taller
        self.operaciones.append(("taller", taller.id))

    async def crear_membresia_dueno(self, taller_id: str, usuario_id: str) -> None:
        self.operaciones.append(("dueno", taller_id, usuario_id))


def crear_servicio(
    repositorio: RepositorioTalleresMemoria,
    accesos: list[str],
    unidad: UnidadMemoria | None = None,
) -> tuple[ServicioTalleres, UnidadMemoria]:
    unidad = unidad or UnidadMemoria(repositorio)
    servicio = ServicioTalleres(
        repositorio,
        AccesosMemoria(accesos),
        lambda: unidad,
        GeneradorFijo(),
    )
    return servicio, unidad


@pytest.mark.asyncio
async def test_crear_taller_incluye_dueno_en_la_misma_unidad() -> None:
    repositorio = RepositorioTalleresMemoria()
    servicio, unidad = crear_servicio(repositorio, [])
    identidad = ContextoIdentidad("usuario-1", "issuer", "subject")

    taller = await servicio.crear(identidad, nombre=" Taller Norte ")

    assert taller == Taller("taller-1", "Taller Norte")
    assert unidad.operaciones == [
        ("iniciar",),
        ("taller", "taller-1"),
        ("dueno", "taller-1", "usuario-1"),
        ("cerrar", "confirmar"),
    ]


@pytest.mark.asyncio
async def test_lista_solo_talleres_accesibles_con_cursor() -> None:
    repositorio = RepositorioTalleresMemoria(
        [Taller("a", "A"), Taller("b", "B"), Taller("c", "C")]
    )
    servicio, _ = crear_servicio(repositorio, ["a", "b", "c"])
    identidad = ContextoIdentidad("usuario-1", "issuer", "subject")

    primera = await servicio.listar(identidad, limite=2)
    segunda = await servicio.listar(
        identidad, cursor=primera.cursor_siguiente, limite=2
    )

    assert [item.id for item in primera.elementos] == ["a", "b"]
    assert primera.cursor_siguiente == "b"
    assert [item.id for item in segunda.elementos] == ["c"]
    assert segunda.cursor_siguiente is None


@pytest.mark.asyncio
async def test_contexto_de_otro_taller_no_revela_recurso() -> None:
    repositorio = RepositorioTalleresMemoria([Taller("taller-b", "B")])
    servicio, _ = crear_servicio(repositorio, ["taller-a"])
    contexto = ContextoTaller("usuario-1", "taller-a", "tecnico")

    with pytest.raises(NoEncontrado):
        await servicio.consultar(contexto)


@pytest.mark.asyncio
async def test_tecnico_autorizado_puede_editar_taller() -> None:
    repositorio = RepositorioTalleresMemoria([Taller("taller-a", "Anterior")])
    servicio, _ = crear_servicio(repositorio, ["taller-a"])
    contexto = ContextoTaller("usuario-1", "taller-a", "tecnico")

    actualizado = await servicio.actualizar(contexto, nombre="Nuevo")

    assert actualizado.nombre == "Nuevo"
