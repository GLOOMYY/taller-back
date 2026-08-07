"""Dependencias HTTP inyectables para autenticación bearer."""

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request

from app.security.servicio import ServicioIdentidad
from app.shared.application import NoAutenticado
from app.shared.application.contexto import ContextoIdentidad

DependenciaIdentidad = Callable[[Request], Coroutine[Any, Any, ContextoIdentidad]]


def crear_dependencia_identidad(
    servicio: ServicioIdentidad,
) -> DependenciaIdentidad:
    """Crea una dependencia sin estado global ni secretos embebidos."""

    async def obtener_identidad(request: Request) -> ContextoIdentidad:
        autorizacion = request.headers.get("Authorization", "")
        esquema, separador, token = autorizacion.partition(" ")
        if not separador or esquema.lower() != "bearer" or not token.strip():
            raise NoAutenticado("Token ausente o inválido")
        return await servicio.autenticar(token.strip())

    return obtener_identidad
