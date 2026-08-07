"""Pruebas de reglas, permisos y aislamiento de Membresías."""

from dataclasses import dataclass

import pytest

from app.modules.membresias.application.puertos import UsuarioReferencia
from app.modules.membresias.application.servicio import ServicioMembresias
from app.modules.membresias.domain.modelos import Membresia, RolMembresia
from app.shared.application import Conflicto, NoEncontrado, Prohibido
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


class RepositorioMemoria:
    """Doble observable que conserva las reglas atómicas del puerto."""

    def __init__(self, membresias: list[Membresia]) -> None:
        self.items = {(item.taller_id, item.usuario_id): item for item in membresias}

    async def obtener(self, taller_id: str, usuario_id: str) -> Membresia | None:
        return self.items.get((taller_id, usuario_id))

    async def listar(
        self, taller_id: str, limite: int, despues_de: str | None
    ) -> list[Membresia]:
        items = sorted(
            (item for item in self.items.values() if item.taller_id == taller_id),
            key=lambda item: item.id,
        )
        if despues_de:
            items = [item for item in items if item.id > despues_de]
        return items[:limite]

    async def listar_taller_ids(self, usuario_id: str) -> list[str]:
        return sorted(
            item.taller_id
            for item in self.items.values()
            if item.usuario_id == usuario_id
        )

    async def crear(self, membresia: Membresia, session: object | None = None) -> None:
        del session
        clave = (membresia.taller_id, membresia.usuario_id)
        if clave in self.items:
            raise Conflicto()
        self.items[clave] = membresia

    async def cambiar_rol_protegiendo_ultimo_dueno(
        self, taller_id: str, usuario_id: str, rol: RolMembresia
    ) -> Membresia | None:
        actual = self.items.get((taller_id, usuario_id))
        if actual is None:
            return None
        self._proteger_ultimo_dueno(actual, rol)
        actualizado = Membresia(actual.id, taller_id, usuario_id, rol)
        self.items[(taller_id, usuario_id)] = actualizado
        return actualizado

    async def retirar_protegiendo_ultimo_dueno(
        self, taller_id: str, usuario_id: str
    ) -> bool:
        actual = self.items.get((taller_id, usuario_id))
        if actual is None:
            return False
        self._proteger_ultimo_dueno(actual, None)
        del self.items[(taller_id, usuario_id)]
        return True

    def _proteger_ultimo_dueno(
        self, actual: Membresia, nuevo_rol: RolMembresia | None
    ) -> None:
        if actual.rol is not RolMembresia.DUENO:
            return
        if nuevo_rol is RolMembresia.DUENO:
            return
        duenos = [
            item
            for item in self.items.values()
            if item.taller_id == actual.taller_id and item.rol is RolMembresia.DUENO
        ]
        if len(duenos) == 1:
            raise Conflicto("El Taller no puede quedar sin dueño")


@dataclass
class DirectorioMemoria:
    usuarios: dict[str, UsuarioReferencia]

    async def buscar_por_nombre_usuario(
        self, nombre_usuario: str
    ) -> UsuarioReferencia | None:
        return self.usuarios.get(nombre_usuario)


@dataclass(frozen=True)
class UsuarioPrueba:
    id: str
    nombre_usuario: str


def crear_servicio(
    membresias: list[Membresia],
) -> tuple[ServicioMembresias, RepositorioMemoria]:
    repositorio = RepositorioMemoria(membresias)
    servicio = ServicioMembresias(
        repositorio,
        DirectorioMemoria(
            {"nuevo": UsuarioPrueba(id="usuario-nuevo", nombre_usuario="nuevo")}
        ),
        lambda: "membresia-nueva",
    )
    return servicio, repositorio


def miembro(taller_id: str, usuario_id: str, rol: RolMembresia) -> Membresia:
    return Membresia(f"mem-{taller_id}-{usuario_id}", taller_id, usuario_id, rol)


@pytest.mark.asyncio
async def test_contexto_se_deriva_de_membresia_del_taller() -> None:
    servicio, _ = crear_servicio(
        [miembro("taller-a", "usuario-a", RolMembresia.TECNICO)]
    )
    identidad = ContextoIdentidad("usuario-a", "https://issuer", "subject-a")

    contexto = await servicio.resolver_contexto_taller(identidad, "taller-a")

    assert contexto == ContextoTaller("usuario-a", "taller-a", "tecnico")


@pytest.mark.asyncio
async def test_cross_tenant_se_oculta_como_no_encontrado() -> None:
    servicio, _ = crear_servicio([miembro("taller-b", "usuario-a", RolMembresia.DUENO)])
    identidad = ContextoIdentidad("usuario-a", "https://issuer", "subject-a")

    with pytest.raises(NoEncontrado):
        await servicio.resolver_contexto_taller(identidad, "taller-a")


@pytest.mark.asyncio
async def test_tecnico_miembro_recibe_prohibido_al_administrar() -> None:
    servicio, _ = crear_servicio([])
    contexto = ContextoTaller("tecnico", "taller-a", "tecnico")

    with pytest.raises(Prohibido):
        await servicio.agregar(contexto, "nuevo", RolMembresia.TECNICO)

    with pytest.raises(Prohibido):
        await servicio.listar(contexto)


@pytest.mark.asyncio
async def test_dueno_agrega_usuario_existente_por_arroba() -> None:
    servicio, repositorio = crear_servicio([])
    contexto = ContextoTaller("dueno", "taller-a", "dueno")

    creada = await servicio.agregar(contexto, "nuevo", RolMembresia.TECNICO)

    assert creada.usuario_id == "usuario-nuevo"
    assert await repositorio.obtener("taller-a", "usuario-nuevo") == creada


@pytest.mark.asyncio
async def test_agregar_membresia_duplicada_es_conflicto() -> None:
    existente = miembro("taller-a", "usuario-nuevo", RolMembresia.TECNICO)
    servicio, _ = crear_servicio([existente])
    contexto = ContextoTaller("dueno", "taller-a", "dueno")

    with pytest.raises(Conflicto):
        await servicio.agregar(contexto, "nuevo", RolMembresia.TECNICO)


@pytest.mark.asyncio
@pytest.mark.parametrize("accion", ["degradar", "retirar"])
async def test_no_permite_dejar_taller_sin_dueno(accion: str) -> None:
    unico = miembro("taller-a", "dueno", RolMembresia.DUENO)
    servicio, _ = crear_servicio([unico])
    contexto = ContextoTaller("dueno", "taller-a", "dueno")

    with pytest.raises(Conflicto):
        if accion == "degradar":
            await servicio.cambiar_rol(contexto, "dueno", RolMembresia.TECNICO)
        else:
            await servicio.retirar(contexto, "dueno")


@pytest.mark.asyncio
async def test_puede_retirar_dueno_si_existe_otro() -> None:
    servicio, repositorio = crear_servicio(
        [
            miembro("taller-a", "dueno-a", RolMembresia.DUENO),
            miembro("taller-a", "dueno-b", RolMembresia.DUENO),
        ]
    )
    contexto = ContextoTaller("dueno-a", "taller-a", "dueno")

    await servicio.retirar(contexto, "dueno-b")

    assert await repositorio.obtener("taller-a", "dueno-b") is None
