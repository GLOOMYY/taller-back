"""Router FastAPI de catálogos técnicos y tipos de servicio."""

from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.modules.catalogos.application.errores import CursorCatalogoInvalido
from app.modules.catalogos.application.servicio import (
    LIMITE_MAXIMO,
    LIMITE_PREDETERMINADO,
    ServicioCatalogos,
)
from app.modules.catalogos.domain import (
    CambiosCatalogo,
    CambiosModelo,
    CambiosTipoServicio,
    EntradaCatalogo,
    ModeloDispositivo,
    TipoServicio,
)
from app.shared.application.contexto import ContextoTaller


class NombreEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El nombre es obligatorio.")
        return valor.strip()


class ModeloEntrada(NombreEntrada):
    tipo_id: str
    marca_id: str

    @field_validator("tipo_id", "marca_id")
    @classmethod
    def referencia_no_vacia(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("La referencia de catálogo es obligatoria.")
        return valor


class TipoServicioEntrada(NombreEntrada):
    descripcion: str | None = None
    precio_predeterminado: str

    def precio_decimal(self) -> Decimal:
        try:
            return Decimal(self.precio_predeterminado)
        except InvalidOperation as error:
            raise ValueError("El precio predeterminado no es decimal.") from error


class CatalogoEditarEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = None
    activo: bool | None = None

    @model_validator(mode="after")
    def validar_patch(self) -> "CatalogoEditarEntrada":
        if not self.model_fields_set:
            raise ValueError("Debe indicarse al menos un campo.")
        if "nombre" in self.model_fields_set and (
            self.nombre is None or not self.nombre.strip()
        ):
            raise ValueError("El nombre es obligatorio.")
        if "activo" in self.model_fields_set and self.activo is None:
            raise ValueError("El estado activo no puede ser nulo.")
        return self

    def a_cambios(self) -> CambiosCatalogo:
        return CambiosCatalogo(
            nombre_definido="nombre" in self.model_fields_set,
            nombre=self.nombre,
            activo_definido="activo" in self.model_fields_set,
            activo=self.activo,
        )


class TipoServicioEditarEntrada(CatalogoEditarEntrada):
    descripcion: str | None = None
    precio_predeterminado: str | None = None

    def a_cambios_servicio(self) -> CambiosTipoServicio:
        precio = None
        if "precio_predeterminado" in self.model_fields_set:
            if self.precio_predeterminado is None:
                raise ValueError("El precio predeterminado no puede ser nulo.")
            try:
                precio = Decimal(self.precio_predeterminado)
            except InvalidOperation as error:
                raise ValueError("El precio predeterminado no es decimal.") from error
        return CambiosTipoServicio(
            nombre_definido="nombre" in self.model_fields_set,
            nombre=self.nombre,
            activo_definido="activo" in self.model_fields_set,
            activo=self.activo,
            descripcion_definida="descripcion" in self.model_fields_set,
            descripcion=self.descripcion,
            precio_definido="precio_predeterminado" in self.model_fields_set,
            precio_predeterminado=precio,
        )


class ModeloEditarEntrada(CatalogoEditarEntrada):
    tipo_id: str | None = None
    marca_id: str | None = None

    @model_validator(mode="after")
    def validar_referencias(self) -> "ModeloEditarEntrada":
        if "tipo_id" in self.model_fields_set and (
            self.tipo_id is None or not self.tipo_id.strip()
        ):
            raise ValueError("El tipo es obligatorio.")
        if "marca_id" in self.model_fields_set and (
            self.marca_id is None or not self.marca_id.strip()
        ):
            raise ValueError("La marca es obligatoria.")
        return self

    def a_cambios_modelo(self) -> CambiosModelo:
        return CambiosModelo(
            nombre_definido="nombre" in self.model_fields_set,
            nombre=self.nombre,
            activo_definido="activo" in self.model_fields_set,
            activo=self.activo,
            tipo_definido="tipo_id" in self.model_fields_set,
            tipo_id=self.tipo_id,
            marca_definida="marca_id" in self.model_fields_set,
            marca_id=self.marca_id,
        )


class CatalogoSalida(BaseModel):
    id: str
    nombre: str
    activo: bool


class ModeloSalida(CatalogoSalida):
    tipo_id: str
    marca_id: str


class TipoServicioSalida(CatalogoSalida):
    descripcion: str | None
    precio_predeterminado: str


class PaginaCatalogoSalida(BaseModel):
    items: list[CatalogoSalida]
    siguiente_cursor: str | None


class PaginaModeloSalida(BaseModel):
    items: list[ModeloSalida]
    siguiente_cursor: str | None


class PaginaTipoServicioSalida(BaseModel):
    items: list[TipoServicioSalida]
    siguiente_cursor: str | None


def _salida(item: EntradaCatalogo) -> CatalogoSalida:
    if item.id is None:
        raise RuntimeError("No se puede presentar un catálogo sin id.")
    return CatalogoSalida(id=item.id, nombre=item.nombre, activo=item.activo)


def _salida_modelo(item: ModeloDispositivo) -> ModeloSalida:
    base = _salida(item)
    return ModeloSalida(
        **base.model_dump(), tipo_id=item.tipo_id, marca_id=item.marca_id
    )


def _salida_servicio(item: TipoServicio) -> TipoServicioSalida:
    base = _salida(item)
    return TipoServicioSalida(
        **base.model_dump(),
        descripcion=item.descripcion,
        precio_predeterminado=str(item.precio_predeterminado),
    )


def crear_router_catalogos(
    obtener_servicio: Callable[..., ServicioCatalogos],
    obtener_contexto: Callable[..., ContextoTaller],
) -> APIRouter:
    """Construye todos los endpoints CRUD sin DELETE físico."""
    router = APIRouter(prefix="/talleres/{taller_id}", tags=["catalogos"])
    Servicio = Annotated[ServicioCatalogos, Depends(obtener_servicio)]
    Contexto = Annotated[ContextoTaller, Depends(obtener_contexto)]
    Limite = Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)]

    @router.post(
        "/tipos-dispositivo",
        response_model=CatalogoSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def crear_tipo(
        entrada: NombreEntrada, servicio: Servicio, contexto: Contexto
    ) -> CatalogoSalida:
        return _salida(await servicio.crear_tipo(contexto, entrada.nombre))

    @router.get("/tipos-dispositivo", response_model=PaginaCatalogoSalida)
    async def listar_tipos(
        servicio: Servicio,
        contexto: Contexto,
        limite: Limite = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaCatalogoSalida:
        try:
            pagina = await servicio.listar(
                contexto, "tipo", limite=limite, cursor=cursor
            )
        except CursorCatalogoInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return PaginaCatalogoSalida(
            items=[_salida(item) for item in pagina.items],
            siguiente_cursor=pagina.siguiente_cursor,
        )

    @router.get("/tipos-dispositivo/{item_id}", response_model=CatalogoSalida)
    async def obtener_tipo(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> CatalogoSalida:
        return _salida(await servicio.obtener(contexto, "tipo", item_id))

    @router.patch("/tipos-dispositivo/{item_id}", response_model=CatalogoSalida)
    async def editar_tipo(
        item_id: str,
        entrada: CatalogoEditarEntrada,
        servicio: Servicio,
        contexto: Contexto,
    ) -> CatalogoSalida:
        return _salida(
            await servicio.actualizar(contexto, "tipo", item_id, entrada.a_cambios())
        )

    @router.delete("/tipos-dispositivo/{item_id}", status_code=204)
    async def desactivar_tipo(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> Response:
        await servicio.actualizar(
            contexto,
            "tipo",
            item_id,
            CambiosCatalogo(activo_definido=True, activo=False),
        )
        return Response(status_code=204)

    @router.post(
        "/marcas-dispositivo",
        response_model=CatalogoSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def crear_marca(
        entrada: NombreEntrada, servicio: Servicio, contexto: Contexto
    ) -> CatalogoSalida:
        return _salida(await servicio.crear_marca(contexto, entrada.nombre))

    @router.get("/marcas-dispositivo", response_model=PaginaCatalogoSalida)
    async def listar_marcas(
        servicio: Servicio,
        contexto: Contexto,
        limite: Limite = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaCatalogoSalida:
        try:
            pagina = await servicio.listar(
                contexto, "marca", limite=limite, cursor=cursor
            )
        except CursorCatalogoInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return PaginaCatalogoSalida(
            items=[_salida(item) for item in pagina.items],
            siguiente_cursor=pagina.siguiente_cursor,
        )

    @router.get("/marcas-dispositivo/{item_id}", response_model=CatalogoSalida)
    async def obtener_marca(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> CatalogoSalida:
        return _salida(await servicio.obtener(contexto, "marca", item_id))

    @router.patch("/marcas-dispositivo/{item_id}", response_model=CatalogoSalida)
    async def editar_marca(
        item_id: str,
        entrada: CatalogoEditarEntrada,
        servicio: Servicio,
        contexto: Contexto,
    ) -> CatalogoSalida:
        return _salida(
            await servicio.actualizar(contexto, "marca", item_id, entrada.a_cambios())
        )

    @router.delete("/marcas-dispositivo/{item_id}", status_code=204)
    async def desactivar_marca(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> Response:
        await servicio.actualizar(
            contexto,
            "marca",
            item_id,
            CambiosCatalogo(activo_definido=True, activo=False),
        )
        return Response(status_code=204)

    @router.post(
        "/modelos-dispositivo",
        response_model=ModeloSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def crear_modelo(
        entrada: ModeloEntrada, servicio: Servicio, contexto: Contexto
    ) -> ModeloSalida:
        item = await servicio.crear_modelo(contexto, **entrada.model_dump())
        return _salida_modelo(item)

    @router.get("/modelos-dispositivo", response_model=PaginaModeloSalida)
    async def listar_modelos(
        servicio: Servicio,
        contexto: Contexto,
        limite: Limite = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaModeloSalida:
        try:
            pagina = await servicio.listar(
                contexto, "modelo", limite=limite, cursor=cursor
            )
        except CursorCatalogoInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return PaginaModeloSalida(
            items=[_salida_modelo(item) for item in pagina.items],
            siguiente_cursor=pagina.siguiente_cursor,
        )

    @router.get("/modelos-dispositivo/{item_id}", response_model=ModeloSalida)
    async def obtener_modelo(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> ModeloSalida:
        item = await servicio.obtener(contexto, "modelo", item_id)
        assert isinstance(item, ModeloDispositivo)
        return _salida_modelo(item)

    @router.patch("/modelos-dispositivo/{item_id}", response_model=ModeloSalida)
    async def editar_modelo(
        item_id: str,
        entrada: ModeloEditarEntrada,
        servicio: Servicio,
        contexto: Contexto,
    ) -> ModeloSalida:
        try:
            item = await servicio.actualizar_modelo(
                contexto, item_id, entrada.a_cambios_modelo()
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return _salida_modelo(item)

    @router.delete("/modelos-dispositivo/{item_id}", status_code=204)
    async def desactivar_modelo(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> Response:
        await servicio.actualizar_modelo(
            contexto,
            item_id,
            CambiosModelo(activo_definido=True, activo=False),
        )
        return Response(status_code=204)

    @router.post(
        "/tipos-servicio",
        response_model=TipoServicioSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def crear_tipo_servicio(
        entrada: TipoServicioEntrada, servicio: Servicio, contexto: Contexto
    ) -> TipoServicioSalida:
        try:
            item = await servicio.crear_tipo_servicio(
                contexto,
                nombre=entrada.nombre,
                descripcion=entrada.descripcion,
                precio_predeterminado=entrada.precio_decimal(),
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return _salida_servicio(item)

    @router.get("/tipos-servicio", response_model=PaginaTipoServicioSalida)
    async def listar_tipos_servicio(
        servicio: Servicio,
        contexto: Contexto,
        limite: Limite = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaTipoServicioSalida:
        try:
            pagina = await servicio.listar(
                contexto, "tipo_servicio", limite=limite, cursor=cursor
            )
        except CursorCatalogoInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return PaginaTipoServicioSalida(
            items=[_salida_servicio(item) for item in pagina.items],
            siguiente_cursor=pagina.siguiente_cursor,
        )

    @router.get("/tipos-servicio/{item_id}", response_model=TipoServicioSalida)
    async def obtener_tipo_servicio(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> TipoServicioSalida:
        item = await servicio.obtener(contexto, "tipo_servicio", item_id)
        assert isinstance(item, TipoServicio)
        return _salida_servicio(item)

    @router.patch("/tipos-servicio/{item_id}", response_model=TipoServicioSalida)
    async def editar_tipo_servicio(
        item_id: str,
        entrada: TipoServicioEditarEntrada,
        servicio: Servicio,
        contexto: Contexto,
    ) -> TipoServicioSalida:
        try:
            cambios = entrada.a_cambios_servicio()
            item = await servicio.actualizar_tipo_servicio(contexto, item_id, cambios)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return _salida_servicio(item)

    @router.delete("/tipos-servicio/{item_id}", status_code=204)
    async def desactivar_tipo_servicio(
        item_id: str, servicio: Servicio, contexto: Contexto
    ) -> Response:
        await servicio.actualizar_tipo_servicio(
            contexto,
            item_id,
            CambiosTipoServicio(activo_definido=True, activo=False),
        )
        return Response(status_code=204)

    return router
