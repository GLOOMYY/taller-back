"""Casos de uso del módulo Talleres."""

from collections.abc import Callable
from dataclasses import dataclass

from app.modules.talleres.application.puertos import (
    DirectorioAccesoTalleres,
    GeneradorId,
    RepositorioTalleres,
    UnidadCreacionTaller,
)
from app.modules.talleres.domain.modelos import Taller
from app.shared.application import NoEncontrado
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


@dataclass(frozen=True, slots=True)
class PaginaTalleres:
    """Página determinista de Talleres accesibles."""

    elementos: tuple[Taller, ...]
    cursor_siguiente: str | None


class ServicioTalleres:
    """Administra Talleres usando identidad y contexto ya validados."""

    def __init__(
        self,
        repositorio: RepositorioTalleres,
        accesos: DirectorioAccesoTalleres,
        crear_unidad: Callable[[], UnidadCreacionTaller],
        generador_id: GeneradorId,
    ) -> None:
        self._repositorio = repositorio
        self._accesos = accesos
        self._crear_unidad = crear_unidad
        self._generador_id = generador_id

    async def crear(
        self,
        identidad: ContextoIdentidad,
        *,
        nombre: str,
        pais_codigo: str = "CO",
        moneda_codigo: str = "COP",
    ) -> Taller:
        """Crea Taller, dueño y Efectivo en una única transacción."""
        validar = getattr(self._repositorio, "referencias_validas", None)
        if validar is not None and not await validar(pais_codigo, moneda_codigo):
            raise NoEncontrado("País o moneda no encontrados")
        taller = Taller(
            id=self._generador_id.generar(),
            nombre=nombre,
            pais_codigo=pais_codigo,
            moneda_codigo=moneda_codigo,
        )
        async with self._crear_unidad() as unidad:
            await unidad.guardar_taller(taller)
            await unidad.crear_membresia_dueno(taller.id, identidad.usuario_id)
            crear_efectivo = getattr(unidad, "crear_metodo_efectivo", None)
            if crear_efectivo is not None:
                await crear_efectivo(taller.id)
        return taller

    async def listar(
        self,
        identidad: ContextoIdentidad,
        *,
        cursor: str | None = None,
        limite: int = 20,
    ) -> PaginaTalleres:
        """Lista solo Talleres vinculados al Usuario autenticado."""
        if limite < 1 or limite > 100:
            raise ValueError("limite debe estar entre 1 y 100")
        ids = await self._accesos.listar_taller_ids(identidad.usuario_id)
        encontrados = await self._repositorio.listar_accesibles(
            ids,
            cursor=cursor,
            limite=limite + 1,
        )
        hay_siguiente = len(encontrados) > limite
        elementos = tuple(encontrados[:limite])
        cursor_siguiente = elementos[-1].id if hay_siguiente and elementos else None
        return PaginaTalleres(elementos, cursor_siguiente)

    async def consultar(self, contexto: ContextoTaller) -> Taller:
        """Consulta el Taller del contexto autorizado sin revelar otros tenants."""
        taller = await self._repositorio.obtener(contexto.taller_id)
        if taller is None:
            raise NoEncontrado("Taller no encontrado")
        return taller

    async def actualizar(
        self,
        contexto: ContextoTaller,
        *,
        nombre: str | None = None,
        pais_codigo: str | None = None,
        moneda_codigo: str | None = None,
    ) -> Taller:
        """Edita el Taller del contexto ya autorizado."""
        taller = await self.consultar(contexto)
        pais = pais_codigo or taller.pais_codigo
        moneda = moneda_codigo or taller.moneda_codigo
        validar = getattr(self._repositorio, "referencias_validas", None)
        if validar is not None and not await validar(pais, moneda):
            raise NoEncontrado("País o moneda no encontrados")
        actualizado = taller.renombrar(nombre) if nombre is not None else taller
        actualizado = actualizado.actualizar_referencias(
            pais_codigo=pais_codigo, moneda_codigo=moneda_codigo
        )
        await self._repositorio.actualizar(actualizado)
        return actualizado
