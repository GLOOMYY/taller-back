"""Punto de composición público del módulo Referencias."""

from dataclasses import dataclass
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.modules.referencias.application import ServicioReferencias
from app.modules.referencias.infrastructure import RepositorioReferenciasMongo


@dataclass(frozen=True, slots=True)
class ModuloReferencias:
    servicio: ServicioReferencias
    repositorio: RepositorioReferenciasMongo


def componer_referencias(base_datos: AsyncDatabase[Any]) -> ModuloReferencias:
    """Conecta el servicio con sus colecciones sin modificar composición global."""
    repositorio = RepositorioReferenciasMongo(base_datos)
    return ModuloReferencias(ServicioReferencias(repositorio), repositorio)
