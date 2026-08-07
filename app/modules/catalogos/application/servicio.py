"""Orquestación tenant-scoped de catálogos."""

from decimal import Decimal
from typing import Literal, overload

from app.modules.catalogos.application.puertos import (
    PaginaCatalogo,
    RepositorioCatalogos,
)
from app.modules.catalogos.domain import (
    CambiosCatalogo,
    CambiosModelo,
    CambiosTipoServicio,
    MarcaDispositivo,
    ModeloDispositivo,
    TipoDispositivo,
    TipoServicio,
)
from app.shared.application.contexto import ContextoTaller
from app.shared.application.errores import NoEncontrado

LIMITE_PREDETERMINADO = 20
LIMITE_MAXIMO = 100
ClaseCatalogo = Literal["tipo", "marca", "modelo", "tipo_servicio"]


class CatalogoNoEncontrado(NoEncontrado):
    """El valor no existe en el Taller autorizado."""


class ServicioCatalogos:
    """Gestiona catálogos aislados por Taller y valida sus referencias."""

    def __init__(self, repositorio: RepositorioCatalogos) -> None:
        self._repositorio = repositorio

    async def crear_tipo(
        self, contexto: ContextoTaller, nombre: str
    ) -> TipoDispositivo:
        return await self._repositorio.crear_tipo(
            contexto, TipoDispositivo.nueva_simple(contexto.taller_id, nombre)
        )

    async def crear_marca(
        self, contexto: ContextoTaller, nombre: str
    ) -> MarcaDispositivo:
        return await self._repositorio.crear_marca(
            contexto, MarcaDispositivo.nueva_simple(contexto.taller_id, nombre)
        )

    async def crear_modelo(
        self,
        contexto: ContextoTaller,
        *,
        nombre: str,
        tipo_id: str,
        marca_id: str,
    ) -> ModeloDispositivo:
        await self._exigir_activo(contexto, "tipo", tipo_id)
        await self._exigir_activo(contexto, "marca", marca_id)
        return await self._repositorio.crear_modelo(
            contexto,
            ModeloDispositivo.nueva(contexto.taller_id, nombre, tipo_id, marca_id),
        )

    async def crear_tipo_servicio(
        self,
        contexto: ContextoTaller,
        *,
        nombre: str,
        descripcion: str | None,
        precio_predeterminado: Decimal,
    ) -> TipoServicio:
        return await self._repositorio.crear_tipo_servicio(
            contexto,
            TipoServicio.nueva(
                contexto.taller_id, nombre, descripcion, precio_predeterminado
            ),
        )

    @overload
    async def listar(
        self,
        contexto: ContextoTaller,
        clase: Literal["tipo"],
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaCatalogo[TipoDispositivo]: ...

    @overload
    async def listar(
        self,
        contexto: ContextoTaller,
        clase: Literal["marca"],
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaCatalogo[MarcaDispositivo]: ...

    @overload
    async def listar(
        self,
        contexto: ContextoTaller,
        clase: Literal["modelo"],
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaCatalogo[ModeloDispositivo]: ...

    @overload
    async def listar(
        self,
        contexto: ContextoTaller,
        clase: Literal["tipo_servicio"],
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaCatalogo[TipoServicio]: ...

    async def listar(
        self,
        contexto: ContextoTaller,
        clase: ClaseCatalogo,
        *,
        limite: int = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> (
        PaginaCatalogo[TipoDispositivo]
        | PaginaCatalogo[MarcaDispositivo]
        | PaginaCatalogo[ModeloDispositivo]
        | PaginaCatalogo[TipoServicio]
    ):
        if limite < 1 or limite > LIMITE_MAXIMO:
            raise ValueError("El límite debe estar entre 1 y 100.")
        if clase == "tipo":
            return await self._repositorio.listar_tipos(
                contexto, limite=limite, cursor=cursor
            )
        if clase == "marca":
            return await self._repositorio.listar_marcas(
                contexto, limite=limite, cursor=cursor
            )
        if clase == "modelo":
            return await self._repositorio.listar_modelos(
                contexto, limite=limite, cursor=cursor
            )
        return await self._repositorio.listar_tipos_servicio(
            contexto, limite=limite, cursor=cursor
        )

    async def obtener(
        self, contexto: ContextoTaller, clase: ClaseCatalogo, item_id: str
    ) -> TipoDispositivo | MarcaDispositivo | ModeloDispositivo | TipoServicio:
        item: (
            TipoDispositivo | MarcaDispositivo | ModeloDispositivo | TipoServicio | None
        )
        if clase == "tipo":
            item = await self._repositorio.obtener_tipo(contexto, item_id)
        elif clase == "marca":
            item = await self._repositorio.obtener_marca(contexto, item_id)
        elif clase == "modelo":
            item = await self._repositorio.obtener_modelo(contexto, item_id)
        else:
            item = await self._repositorio.obtener_tipo_servicio(contexto, item_id)
        if item is None:
            raise CatalogoNoEncontrado("El valor de catálogo no está disponible.")
        return item

    async def actualizar(
        self,
        contexto: ContextoTaller,
        clase: Literal["tipo", "marca", "modelo"],
        item_id: str,
        cambios: CambiosCatalogo,
    ) -> TipoDispositivo | MarcaDispositivo | ModeloDispositivo:
        item = await self.obtener(contexto, clase, item_id)
        actualizado = item.actualizar(cambios)
        resultado: TipoDispositivo | MarcaDispositivo | ModeloDispositivo | None
        if clase == "tipo":
            assert isinstance(actualizado, TipoDispositivo)
            resultado = await self._repositorio.actualizar_tipo(contexto, actualizado)
        elif clase == "marca":
            assert isinstance(actualizado, MarcaDispositivo)
            resultado = await self._repositorio.actualizar_marca(contexto, actualizado)
        else:
            assert isinstance(actualizado, ModeloDispositivo)
            resultado = await self._repositorio.actualizar_modelo(contexto, actualizado)
        if resultado is None:
            raise CatalogoNoEncontrado()
        return resultado

    async def actualizar_tipo_servicio(
        self,
        contexto: ContextoTaller,
        item_id: str,
        cambios: CambiosTipoServicio,
    ) -> TipoServicio:
        item = await self.obtener(contexto, "tipo_servicio", item_id)
        assert isinstance(item, TipoServicio)
        resultado = await self._repositorio.actualizar_tipo_servicio(
            contexto, item.actualizar_servicio(cambios)
        )
        if resultado is None:
            raise CatalogoNoEncontrado()
        return resultado

    async def actualizar_modelo(
        self,
        contexto: ContextoTaller,
        item_id: str,
        cambios: CambiosModelo,
    ) -> ModeloDispositivo:
        item = await self.obtener(contexto, "modelo", item_id)
        assert isinstance(item, ModeloDispositivo)
        actualizado = item.actualizar_modelo(cambios)
        if cambios.tipo_definido or (cambios.activo_definido and cambios.activo):
            await self._exigir_activo(contexto, "tipo", actualizado.tipo_id)
        if cambios.marca_definida or (cambios.activo_definido and cambios.activo):
            await self._exigir_activo(contexto, "marca", actualizado.marca_id)
        resultado = await self._repositorio.actualizar_modelo(contexto, actualizado)
        if resultado is None:
            raise CatalogoNoEncontrado()
        return resultado

    async def obtener_modelo_seleccionable(
        self, contexto: ContextoTaller, modelo_id: str
    ) -> ModeloDispositivo:
        modelo = await self.obtener(contexto, "modelo", modelo_id)
        assert isinstance(modelo, ModeloDispositivo)
        if not modelo.activo:
            raise CatalogoNoEncontrado("El modelo no está activo.")
        await self._exigir_activo(contexto, "tipo", modelo.tipo_id)
        await self._exigir_activo(contexto, "marca", modelo.marca_id)
        return modelo

    async def _exigir_activo(
        self,
        contexto: ContextoTaller,
        clase: Literal["tipo", "marca"],
        item_id: str,
    ) -> None:
        item = await self.obtener(contexto, clase, item_id)
        if not item.activo:
            raise CatalogoNoEncontrado("El valor de catálogo no está activo.")
