"""Router FastAPI de los catálogos ISO globales."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.modules.referencias.application import ServicioReferencias
from app.shared.application.contexto import ContextoTaller


class PaisSalida(BaseModel):
    codigo: str
    nombre: str


class MonedaSalida(BaseModel):
    codigo: str
    nombre: str
    simbolo: str
    decimales: int


def crear_router_referencias(
    obtener_servicio: Callable[..., ServicioReferencias],
    obtener_contexto: Callable[..., ContextoTaller],
) -> APIRouter:
    """Construye rutas autenticadas sin acoplarlas a composición concreta."""
    router = APIRouter(prefix="/talleres/{taller_id}/referencias", tags=["referencias"])

    @router.get("/paises", response_model=list[PaisSalida])
    async def listar_paises(
        servicio: Annotated[ServicioReferencias, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> list[PaisSalida]:
        del contexto
        return [
            PaisSalida(codigo=item.codigo, nombre=item.nombre)
            for item in await servicio.listar_paises()
        ]

    @router.get("/monedas", response_model=list[MonedaSalida])
    async def listar_monedas(
        servicio: Annotated[ServicioReferencias, Depends(obtener_servicio)],
        contexto: Annotated[ContextoTaller, Depends(obtener_contexto)],
    ) -> list[MonedaSalida]:
        del contexto
        return [
            MonedaSalida(
                codigo=item.codigo,
                nombre=item.nombre,
                simbolo=item.simbolo,
                decimales=item.decimales,
            )
            for item in await servicio.listar_monedas()
        ]

    return router
