"""Router FastAPI del módulo Talleres."""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.modules.talleres.application.casos_uso import ServicioTalleres
from app.modules.talleres.presentation.esquemas import (
    PaginaTalleresSalida,
    TallerCambio,
    TallerEntrada,
    TallerSalida,
)
from app.shared.application.contexto import ContextoIdentidad, ContextoTaller


def create_router(
    servicio: ServicioTalleres,
    obtener_identidad: Callable[..., Any],
    obtener_contexto_taller: Callable[..., Any],
) -> APIRouter:
    """Construye el router con autenticación y tenancy inyectadas."""
    router = APIRouter(prefix="/talleres", tags=["talleres"])
    IdentidadDependencia = Annotated[ContextoIdentidad, Depends(obtener_identidad)]
    ContextoDependencia = Annotated[ContextoTaller, Depends(obtener_contexto_taller)]

    @router.post("", response_model=TallerSalida, status_code=status.HTTP_201_CREATED)
    async def crear(
        entrada: TallerEntrada,
        identidad: IdentidadDependencia,
    ) -> TallerSalida:
        return TallerSalida.model_validate(
            await servicio.crear(
                identidad,
                nombre=entrada.nombre,
                pais_codigo=entrada.pais_codigo,
                moneda_codigo=entrada.moneda_codigo,
            )
        )

    @router.get("", response_model=PaginaTalleresSalida)
    async def listar(
        identidad: IdentidadDependencia,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> PaginaTalleresSalida:
        pagina = await servicio.listar(identidad, cursor=cursor, limite=limite)
        return PaginaTalleresSalida(
            elementos=[TallerSalida.model_validate(item) for item in pagina.elementos],
            cursor_siguiente=pagina.cursor_siguiente,
        )

    @router.get("/{taller_id}", response_model=TallerSalida)
    async def consultar(
        contexto: ContextoDependencia,
    ) -> TallerSalida:
        return TallerSalida.model_validate(await servicio.consultar(contexto))

    @router.patch("/{taller_id}", response_model=TallerSalida)
    async def actualizar(
        entrada: TallerCambio,
        contexto: ContextoDependencia,
    ) -> TallerSalida:
        return TallerSalida.model_validate(
            await servicio.actualizar(
                contexto,
                nombre=entrada.nombre,
                pais_codigo=entrada.pais_codigo,
                moneda_codigo=entrada.moneda_codigo,
            )
        )

    return router
