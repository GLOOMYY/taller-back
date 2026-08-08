"""Endpoints públicos de autenticación JWT local."""


from fastapi import APIRouter, status

from app.modules.usuarios.application.casos_uso import ServicioUsuarios
from app.modules.usuarios.presentation.auth_schemas import (
    LoginEntrada,
    RegistroEntrada,
    SesionSalida,
)
from app.security.jwt_local import ServicioJwtLocal


def crear_router_auth(
    usuarios: ServicioUsuarios,
    jwt_local: ServicioJwtLocal,
) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["autenticacion"])

    @router.post(
        "/registro",
        response_model=SesionSalida,
        status_code=status.HTTP_201_CREATED,
    )
    async def registro(entrada: RegistroEntrada) -> SesionSalida:
        usuario = await usuarios.registrar_local(
            nombre=entrada.nombre,
            nombre_usuario=entrada.nombre_usuario,
            password=entrada.password,
        )
        return SesionSalida(
            access_token=jwt_local.emitir(usuario.id),
            usuario_id=usuario.id,
            nombre=usuario.nombre,
            nombre_usuario=usuario.nombre_usuario,
        )

    @router.post("/login", response_model=SesionSalida)
    async def login(entrada: LoginEntrada) -> SesionSalida:
        usuario = await usuarios.autenticar_local(
            nombre_usuario=entrada.nombre_usuario,
            password=entrada.password,
        )
        return SesionSalida(
            access_token=jwt_local.emitir(usuario.id),
            usuario_id=usuario.id,
            nombre=usuario.nombre,
            nombre_usuario=usuario.nombre_usuario,
        )

    return router
