"""Punto de composición público del módulo Dispositivos."""

from dataclasses import dataclass
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.modules.dispositivos.application.puertos import BuscadorReferencia
from app.modules.dispositivos.application.servicio import ServicioDispositivos
from app.modules.dispositivos.infrastructure import RepositorioDispositivosMongo


@dataclass(frozen=True, slots=True)
class ModuloDispositivos:
    servicio: ServicioDispositivos
    repositorio: RepositorioDispositivosMongo


def componer_dispositivos(
    base_datos: AsyncDatabase[Any],
    *,
    obtener_cliente: BuscadorReferencia,
    obtener_modelo_seleccionable: BuscadorReferencia,
) -> ModuloDispositivos:
    """Conecta persistencia y contratos públicos de Cliente/Modelo."""
    repositorio = RepositorioDispositivosMongo(base_datos)
    servicio = ServicioDispositivos(
        repositorio, obtener_cliente, obtener_modelo_seleccionable
    )
    return ModuloDispositivos(servicio, repositorio)
