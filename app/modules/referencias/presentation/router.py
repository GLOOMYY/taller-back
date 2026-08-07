"""Router FastAPI de los catálogos ISO globales."""

from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.modules.referencias.application import ServicioReferencias
from app.shared.application.contexto import ContextoIdentidad


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
    obtener_identidad: Callable[..., ContextoIdentidad],
) -> APIRouter:
    """Construye rutas autenticadas sin acoplarlas a composición concreta."""
    router = APIRouter(prefix="/referencias", tags=["referencias"])

    @router.get("/paises", response_model=list[PaisSalida])
    async def listar_paises(
        servicio: Annotated[ServicioReferencias, Depends(obtener_servicio)],
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> list[PaisSalida]:
        del identidad
        return [
            PaisSalida(codigo=item.codigo, nombre=item.nombre)
            for item in await servicio.listar_paises()
        ]

    @router.get("/monedas", response_model=list[MonedaSalida])
    async def listar_monedas(
        servicio: Annotated[ServicioReferencias, Depends(obtener_servicio)],
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> list[MonedaSalida]:
        del identidad
        return [
            MonedaSalida(
                codigo=item.codigo,
                nombre=item.nombre,
                simbolo=item.simbolo,
                decimales=item.decimales,
            )
            for item in await servicio.listar_monedas()
        ]

    @router.get("/paises/{codigo}", response_model=PaisSalida)
    async def obtener_pais(
        codigo: str,
        servicio: Annotated[ServicioReferencias, Depends(obtener_servicio)],
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> PaisSalida:
        del identidad
        item = await servicio.obtener_pais(codigo)
        return PaisSalida(codigo=item.codigo, nombre=item.nombre)

    @router.get("/monedas/{codigo}", response_model=MonedaSalida)
    async def obtener_moneda(
        codigo: str,
        servicio: Annotated[ServicioReferencias, Depends(obtener_servicio)],
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> MonedaSalida:
        del identidad
        item = await servicio.obtener_moneda(codigo)
        return MonedaSalida(
            codigo=item.codigo,
            nombre=item.nombre,
            simbolo=item.simbolo,
            decimales=item.decimales,
        )

    return router
