"""Rutas HTTP para administrar Membresías."""

import re
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.membresias.application.servicio import ServicioMembresias
from app.modules.membresias.domain.modelos import Membresia, RolMembresia
from app.security.dependencias import DependenciaIdentidad
from app.shared.application.contexto import ContextoIdentidad

IdPath = Annotated[str, Path(min_length=1, max_length=128)]


class CrearMembresiaRequest(BaseModel):
    """Entrada para agregar un Usuario existente por arroba."""

    model_config = ConfigDict(extra="forbid")
    nombre_usuario: str
    rol: RolMembresia

    @field_validator("nombre_usuario")
    @classmethod
    def normalizar_nombre_usuario(cls, valor: str) -> str:
        """Acepta la representación con arroba y envía el valor canónico."""
        normalizado = valor.strip().lower()
        if normalizado.startswith("@"):
            normalizado = normalizado[1:]
        if re.fullmatch(r"[a-z0-9._]{3,30}", normalizado, re.ASCII) is None:
            raise ValueError("nombre_usuario no cumple el formato aceptado")
        return normalizado


class CambiarRolRequest(BaseModel):
    """Entrada para modificar el rol de un miembro."""

    model_config = ConfigDict(extra="forbid")
    rol: RolMembresia


class MembresiaResponse(BaseModel):
    """Representación pública sin detalles de MongoDB."""

    id: str
    taller_id: str
    usuario_id: str
    rol: RolMembresia

    @classmethod
    def desde_dominio(cls, membresia: Membresia) -> "MembresiaResponse":
        """Traduce una entidad al contrato HTTP."""
        return cls(
            id=membresia.id,
            taller_id=membresia.taller_id,
            usuario_id=membresia.usuario_id,
            rol=membresia.rol,
        )


class ListaMembresiasResponse(BaseModel):
    """Página cursor-based de Membresías."""

    items: list[MembresiaResponse]
    siguiente_cursor: str | None


def create_router(
    servicio: ServicioMembresias,
    obtener_identidad: DependenciaIdentidad,
) -> APIRouter:
    """Crea el router con dependencias explícitas para composición."""
    router = APIRouter(prefix="/talleres/{taller_id}/miembros", tags=["miembros"])

    @router.get("")
    async def listar_miembros(
        taller_id: IdPath,
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
        cursor: Annotated[str | None, Query(max_length=128)] = None,
    ) -> ListaMembresiasResponse:
        contexto = await servicio.resolver_contexto_taller(identidad, taller_id)
        miembros = await servicio.listar(contexto, limite + 1, cursor)
        hay_mas = len(miembros) > limite
        pagina = miembros[:limite]
        return ListaMembresiasResponse(
            items=[MembresiaResponse.desde_dominio(item) for item in pagina],
            siguiente_cursor=pagina[-1].id if hay_mas and pagina else None,
        )

    @router.post("", status_code=status.HTTP_201_CREATED)
    async def agregar_miembro(
        taller_id: IdPath,
        entrada: CrearMembresiaRequest,
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> MembresiaResponse:
        contexto = await servicio.resolver_contexto_taller(identidad, taller_id)
        membresia = await servicio.agregar(
            contexto, entrada.nombre_usuario, entrada.rol
        )
        return MembresiaResponse.desde_dominio(membresia)

    @router.patch("/{usuario_id}")
    async def cambiar_rol(
        taller_id: IdPath,
        usuario_id: IdPath,
        entrada: CambiarRolRequest,
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> MembresiaResponse:
        contexto = await servicio.resolver_contexto_taller(identidad, taller_id)
        membresia = await servicio.cambiar_rol(contexto, usuario_id, entrada.rol)
        return MembresiaResponse.desde_dominio(membresia)

    @router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def retirar_miembro(
        taller_id: IdPath,
        usuario_id: IdPath,
        identidad: Annotated[ContextoIdentidad, Depends(obtener_identidad)],
    ) -> Response:
        contexto = await servicio.resolver_contexto_taller(identidad, taller_id)
        await servicio.retirar(contexto, usuario_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
