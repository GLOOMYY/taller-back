"""Router FastAPI del módulo Usuarios."""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from app.modules.usuarios.application.casos_uso import ServicioUsuarios
from app.modules.usuarios.domain.modelos import IdentidadOidc
from app.modules.usuarios.presentation.esquemas import (
    ActualizarUsuarioEntrada,
    RegistrarUsuarioEntrada,
    UsuarioSalida,
)


def create_router(
    servicio: ServicioUsuarios,
    obtener_identidad: Callable[..., Any],
) -> APIRouter:
    """Construye el router con dependencias explícitas desde composición."""
    router = APIRouter(prefix="/usuarios", tags=["usuarios"])
    IdentidadDependencia = Annotated[IdentidadOidc, Depends(obtener_identidad)]

    @router.post(
        "/me",
        response_model=UsuarioSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def registrar(
        entrada: RegistrarUsuarioEntrada,
        identidad: IdentidadDependencia,
    ) -> UsuarioSalida:
        usuario = await servicio.registrar(
            identidad,
            nombre=entrada.nombre,
            nombre_usuario=entrada.nombre_usuario,
        )
        return UsuarioSalida.model_validate(usuario)

    @router.get("/me", response_model=UsuarioSalida)
    async def consultar(
        identidad: IdentidadDependencia,
    ) -> UsuarioSalida:
        return UsuarioSalida.model_validate(await servicio.consultar(identidad))

    @router.patch("/me", response_model=UsuarioSalida)
    async def actualizar(
        entrada: ActualizarUsuarioEntrada,
        identidad: IdentidadDependencia,
    ) -> UsuarioSalida:
        usuario = await servicio.actualizar(
            identidad,
            nombre=entrada.nombre,
            nombre_usuario=entrada.nombre_usuario,
        )
        return UsuarioSalida.model_validate(usuario)

    return router
