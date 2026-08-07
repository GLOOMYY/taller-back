"""Adaptador MongoDB asíncrono para Talleres."""

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import uuid4

from app.modules.talleres.domain.modelos import Taller


class GeneradorUuid:
    """Genera UUID opacos para Talleres."""

    def generar(self) -> str:
        """Genera un UUID aleatorio serializado."""
        return str(uuid4())


class RepositorioTalleresMongo:
    """Persistencia Mongo de Talleres, sin exponer documentos al núcleo."""

    def __init__(
        self,
        coleccion: Any,
        paises: Any | None = None,
        monedas: Any | None = None,
    ):
        self._coleccion = coleccion
        self._paises = paises
        self._monedas = monedas

    async def crear(self, taller: Taller, *, session: Any | None = None) -> None:
        """Inserta un Taller; la UoW debe aportar la sesión transaccional."""
        await self._coleccion.insert_one(
            {
                "_id": taller.id,
                "nombre": taller.nombre,
                "pais_codigo": taller.pais_codigo,
                "moneda_codigo": taller.moneda_codigo,
            },
            session=session,
        )

    async def obtener(self, taller_id: str) -> Taller | None:
        documento = await self._coleccion.find_one({"_id": taller_id})
        return self._a_entidad(documento) if documento is not None else None

    async def listar_accesibles(
        self,
        taller_ids: Sequence[str],
        *,
        cursor: str | None,
        limite: int,
    ) -> list[Taller]:
        if not taller_ids:
            return []
        filtro: dict[str, Any] = {"$in": list(taller_ids)}
        if cursor is not None:
            filtro["$gt"] = cursor
        cursor_mongo = (
            self._coleccion.find({"_id": filtro}).sort("_id", 1).limit(limite)
        )
        return [self._a_entidad(documento) async for documento in cursor_mongo]

    async def actualizar(self, taller: Taller) -> None:
        await self._coleccion.update_one(
            {"_id": taller.id},
            {
                "$set": {
                    "nombre": taller.nombre,
                    "pais_codigo": taller.pais_codigo,
                    "moneda_codigo": taller.moneda_codigo,
                }
            },
        )

    async def referencias_validas(self, pais_codigo: str, moneda_codigo: str) -> bool:
        if self._paises is None or self._monedas is None:
            return False
        pais = await self._paises.find_one({"codigo": pais_codigo.upper()})
        moneda = await self._monedas.find_one({"codigo": moneda_codigo.upper()})
        return pais is not None and moneda is not None

    @staticmethod
    def _a_entidad(documento: Mapping[str, Any]) -> Taller:
        return Taller(
            id=str(documento["_id"]),
            nombre=str(documento["nombre"]),
            pais_codigo=str(documento.get("pais_codigo", "CO")),
            moneda_codigo=str(documento.get("moneda_codigo", "COP")),
        )
