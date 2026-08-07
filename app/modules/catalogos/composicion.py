"""Punto de composición público del módulo Catálogos."""

from dataclasses import dataclass
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.modules.catalogos.application import ServicioCatalogos
from app.modules.catalogos.infrastructure import RepositorioCatalogosMongo


@dataclass(frozen=True, slots=True)
class ModuloCatalogos:
    servicio: ServicioCatalogos
    repositorio: RepositorioCatalogosMongo


def componer_catalogos(base_datos: AsyncDatabase[Any]) -> ModuloCatalogos:
    """Conecta Catálogos con sus colecciones propietarias."""
    repositorio = RepositorioCatalogosMongo(base_datos)
    return ModuloCatalogos(ServicioCatalogos(repositorio), repositorio)
