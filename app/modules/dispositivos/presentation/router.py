"""Router FastAPI de Dispositivos."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.dispositivos.application.errores import CursorDispositivosInvalido
from app.modules.dispositivos.application.servicio import (
    LIMITE_MAXIMO,
    LIMITE_PREDETERMINADO,
    ServicioDispositivos,
)
from app.modules.dispositivos.domain import CambiosDispositivo, Dispositivo
from app.shared.application.contexto import ContextoTaller


class DispositivoCrearEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")
    modelo_id: str
    identificador: str | None = None
    notas: str | None = None


class DispositivoEditarEntrada(BaseModel):
    """Cliente no aparece en el PATCH porque es inmutable."""

    model_config = ConfigDict(extra="forbid")
    modelo_id: str | None = None
    identificador: str | None = None
    notas: str | None = None

    @model_validator(mode="after")
    def validar_patch(self) -> "DispositivoEditarEntrada":
        if not self.model_fields_set:
            raise ValueError("Debe indicarse al menos un campo.")
        if "modelo_id" in self.model_fields_set and (
            self.modelo_id is None or not self.modelo_id.strip()
        ):
            raise ValueError("El modelo es obligatorio.")
        return self

    def a_cambios(self) -> CambiosDispositivo:
        return CambiosDispositivo(
            modelo_definido="modelo_id" in self.model_fields_set,
            modelo_id=self.modelo_id,
            identificador_definido="identificador" in self.model_fields_set,
            identificador=self.identificador,
            notas_definidas="notas" in self.model_fields_set,
            notas=self.notas,
        )


class DispositivoSalida(BaseModel):
    id: str
    cliente_id: str
    modelo_id: str
    identificador: str | None
    notas: str | None

    @classmethod
    def desde_entidad(cls, item: Dispositivo) -> "DispositivoSalida":
        if item.id is None:
            raise RuntimeError("No se puede presentar un Dispositivo sin id.")
        return cls(
            id=item.id,
            cliente_id=item.cliente_id,
            modelo_id=item.modelo_id,
            identificador=item.identificador,
            notas=item.notas,
        )


class PaginaDispositivosSalida(BaseModel):
    items: list[DispositivoSalida]
    siguiente_cursor: str | None


def crear_router_dispositivos(
    obtener_servicio: Callable[..., ServicioDispositivos],
    obtener_contexto: Callable[..., ContextoTaller],
) -> APIRouter:
    """Construye rutas bajo Cliente y Taller con dependencias inyectadas."""
    router = APIRouter(prefix="/talleres/{taller_id}", tags=["dispositivos"])

    @router.post(
        "/clientes/{cliente_id}/dispositivos",
        response_model=DispositivoSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def crear_dispositivo(
        cliente_id: str,
        entrada: DispositivoCrearEntrada,
        servicio: Annotated[ServicioDispositivos, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> DispositivoSalida:
        try:
            item = await servicio.crear(contexto, cliente_id, **entrada.model_dump())
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return DispositivoSalida.desde_entidad(item)

    @router.get(
        "/clientes/{cliente_id}/dispositivos",
        response_model=PaginaDispositivosSalida,
    )
    async def listar_dispositivos(
        cliente_id: str,
        servicio: Annotated[ServicioDispositivos, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
        limite: Annotated[int, Query(ge=1, le=LIMITE_MAXIMO)] = LIMITE_PREDETERMINADO,
        cursor: str | None = None,
    ) -> PaginaDispositivosSalida:
        try:
            pagina = await servicio.listar_por_cliente(
                contexto, cliente_id, limite=limite, cursor=cursor
            )
        except CursorDispositivosInvalido as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return PaginaDispositivosSalida(
            items=[DispositivoSalida.desde_entidad(item) for item in pagina.items],
            siguiente_cursor=pagina.siguiente_cursor,
        )

    @router.get("/dispositivos/{dispositivo_id}", response_model=DispositivoSalida)
    async def obtener_dispositivo(
        dispositivo_id: str,
        servicio: Annotated[ServicioDispositivos, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> DispositivoSalida:
        return DispositivoSalida.desde_entidad(
            await servicio.obtener(contexto, dispositivo_id)
        )

    @router.patch("/dispositivos/{dispositivo_id}", response_model=DispositivoSalida)
    async def editar_dispositivo(
        dispositivo_id: str,
        entrada: DispositivoEditarEntrada,
        servicio: Annotated[ServicioDispositivos, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> DispositivoSalida:
        try:
            item = await servicio.actualizar(
                contexto, dispositivo_id, entrada.a_cambios()
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return DispositivoSalida.desde_entidad(item)

    return router
