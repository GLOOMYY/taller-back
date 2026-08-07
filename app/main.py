"""Application factory y composición del adaptador FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.composition import Contenedor, crear_contenedor, crear_dependencias
from app.core.config import Settings, get_settings
from app.core.http import ErrorSalida, configurar_http
from app.core.mongodb import comprobar_mongodb
from app.modules.catalogos.presentation.router import crear_router_catalogos
from app.modules.clientes.presentation.router import crear_router as router_clientes
from app.modules.dispositivos.presentation.router import crear_router_dispositivos
from app.modules.membresias.presentation.router import (
    create_router as router_membresias,
)
from app.modules.operaciones.presentation.router import (
    crear_router as router_operaciones,
)
from app.modules.referencias.presentation.router import crear_router_referencias
from app.modules.seguimiento.presentation.router import crear_router_seguimiento
from app.modules.talleres.presentation.router import create_router as router_talleres
from app.modules.usuarios.presentation.router import create_router as router_usuarios


def create_app(settings: Settings | None = None) -> FastAPI:
    """Crea una aplicación con configuración y dependencias explícitas."""

    configuracion = settings or get_settings()
    contenedor = crear_contenedor(configuracion)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.contenedor = contenedor
        yield
        await contenedor.cliente_mongodb.close()

    application = FastAPI(
        title="Taller API",
        version="0.2.0",
        lifespan=lifespan,
        responses={
            400: {"model": ErrorSalida, "description": "Solicitud inválida"},
            401: {"model": ErrorSalida, "description": "No autenticado"},
            403: {"model": ErrorSalida, "description": "Acceso prohibido"},
            404: {"model": ErrorSalida, "description": "Recurso no encontrado"},
            409: {"model": ErrorSalida, "description": "Conflicto de negocio"},
            422: {"model": ErrorSalida, "description": "Entrada inválida"},
        },
    )
    application.state.contenedor = contenedor
    application.add_middleware(
        CORSMiddleware,
        allow_origins=configuracion.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
    )
    configurar_http(application)

    (
        obtener_oidc,
        obtener_identidad,
        obtener_contexto,
        obtener_servicio_clientes,
    ) = crear_dependencias(contenedor)
    api = APIRouter(prefix="/api/v1")
    api.include_router(router_usuarios(contenedor.usuarios, obtener_oidc))
    api.include_router(
        router_talleres(
            contenedor.talleres,
            obtener_identidad,
            obtener_contexto,
        )
    )
    api.include_router(router_membresias(contenedor.membresias, obtener_identidad))
    api.include_router(router_clientes(obtener_servicio_clientes, obtener_contexto))
    api.include_router(
        crear_router_referencias(
            lambda: contenedor.referencias.servicio, obtener_identidad
        )
    )
    api.include_router(
        crear_router_catalogos(lambda: contenedor.catalogos.servicio, obtener_contexto)
    )
    api.include_router(
        crear_router_dispositivos(
            lambda: contenedor.dispositivos.servicio, obtener_contexto
        )
    )
    api.include_router(router_operaciones(contenedor.operaciones, obtener_contexto))
    router_seguimiento_privado, router_seguimiento_publico = crear_router_seguimiento(
        contenedor.seguimiento,
        contenedor.comprobantes,
        obtener_contexto,
    )
    api.include_router(router_seguimiento_privado)
    api.include_router(router_seguimiento_publico)
    application.include_router(api)

    @application.get("/", tags=["general"])
    async def root() -> dict[str, str]:
        return {"message": "Taller API"}

    @application.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready", tags=["health"])
    async def ready(request: Request) -> dict[str, str]:
        actual: Contenedor = request.app.state.contenedor
        if not await comprobar_mongodb(actual.cliente_mongodb):
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MongoDB no está disponible",
            )
        await actual.crear_indices()
        return {"status": "ok"}

    return application


app = create_app()
