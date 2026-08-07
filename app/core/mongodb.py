"""Ciclo de vida y comprobación de MongoDB."""

from typing import Any

from pymongo import AsyncMongoClient

from app.core.config import Settings


def crear_cliente_mongodb(settings: Settings) -> AsyncMongoClient[Any]:
    """Crea un cliente lazy; la conexión se comprueba en readiness."""

    return AsyncMongoClient(
        settings.mongodb_uri,
        appname="taller-api",
        serverSelectionTimeoutMS=2_000,
    )


async def comprobar_mongodb(cliente: AsyncMongoClient[Any]) -> bool:
    try:
        await cliente.admin.command("ping")
    except Exception:  # PyMongo expone varias subclases según el fallo de red.
        return False
    return True
