"""Lectura asíncrona de referencias ISO desde MongoDB."""

from collections.abc import Mapping
from typing import Any

from pymongo import ASCENDING, UpdateOne
from pymongo.asynchronous.database import AsyncDatabase

from app.modules.referencias.domain import Moneda, Pais

COLECCION_PAISES = "referencias_paises"
COLECCION_MONEDAS = "referencias_monedas"


class RepositorioReferenciasMongo:
    """Repositorio global de catálogos ISO de solo lectura funcional."""

    def __init__(self, base_datos: AsyncDatabase[Any]) -> None:
        self._paises = base_datos[COLECCION_PAISES]
        self._monedas = base_datos[COLECCION_MONEDAS]

    async def crear_indices(self) -> None:
        """Materializa códigos únicos y orden de listados."""
        await self._paises.create_index(
            [("codigo", ASCENDING)], unique=True, name="paises_codigo_iso"
        )
        await self._monedas.create_index(
            [("codigo", ASCENDING)], unique=True, name="monedas_codigo_iso"
        )

    async def sincronizar_catalogos(
        self, paises: tuple[Pais, ...], monedas: tuple[Moneda, ...]
    ) -> None:
        """Carga idempotentemente una fuente ISO; la API continúa siendo read-only."""
        operaciones_paises = [
            UpdateOne(
                {"codigo": item.codigo},
                {"$set": {"codigo": item.codigo, "nombre": item.nombre}},
                upsert=True,
            )
            for item in paises
        ]
        operaciones_monedas = [
            UpdateOne(
                {"codigo": item.codigo},
                {
                    "$set": {
                        "codigo": item.codigo,
                        "nombre": item.nombre,
                        "simbolo": item.simbolo,
                        "decimales": item.decimales,
                    }
                },
                upsert=True,
            )
            for item in monedas
        ]
        if operaciones_paises:
            await self._paises.bulk_write(operaciones_paises, ordered=False)
        if operaciones_monedas:
            await self._monedas.bulk_write(operaciones_monedas, ordered=False)

    async def listar_paises(self) -> tuple[Pais, ...]:
        cursor = self._paises.find({}).sort("codigo", ASCENDING)
        return tuple([self._a_pais(item) async for item in cursor])

    async def listar_monedas(self) -> tuple[Moneda, ...]:
        cursor = self._monedas.find({}).sort("codigo", ASCENDING)
        return tuple([self._a_moneda(item) async for item in cursor])

    async def obtener_pais(self, codigo: str) -> Pais | None:
        item = await self._paises.find_one({"codigo": codigo})
        return self._a_pais(item) if item is not None else None

    async def obtener_moneda(self, codigo: str) -> Moneda | None:
        item = await self._monedas.find_one({"codigo": codigo})
        return self._a_moneda(item) if item is not None else None

    @staticmethod
    def _a_pais(item: Mapping[str, Any]) -> Pais:
        return Pais(codigo=str(item["codigo"]), nombre=str(item["nombre"]))

    @staticmethod
    def _a_moneda(item: Mapping[str, Any]) -> Moneda:
        return Moneda(
            codigo=str(item["codigo"]),
            nombre=str(item["nombre"]),
            simbolo=str(item["simbolo"]),
            decimales=int(item["decimales"]),
        )
