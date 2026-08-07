"""Repositorio PyMongo Async de Dispositivos."""

import base64
import binascii
import json
from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, ReturnDocument
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from app.modules.dispositivos.application.errores import CursorDispositivosInvalido
from app.modules.dispositivos.application.puertos import PaginaDispositivos
from app.modules.dispositivos.domain import Dispositivo
from app.shared.application.contexto import ContextoTaller

COLECCION_DISPOSITIVOS = "dispositivos"


class RepositorioDispositivosMongo:
    """Persiste equipos y aplica Taller en todos los filtros."""

    def __init__(self, base_datos: AsyncDatabase[Any]) -> None:
        self._coleccion: AsyncCollection[dict[str, Any]] = base_datos[
            COLECCION_DISPOSITIVOS
        ]

    async def crear_indices(self) -> None:
        await self._coleccion.create_index(
            [
                ("taller_id", ASCENDING),
                ("cliente_id", ASCENDING),
                ("_id", ASCENDING),
            ],
            name="dispositivos_por_taller_cliente",
        )
        await self._coleccion.create_index(
            [("taller_id", ASCENDING), ("modelo_id", ASCENDING)],
            name="dispositivos_por_taller_modelo",
        )

    async def crear(
        self, contexto: ContextoTaller, dispositivo: Dispositivo
    ) -> Dispositivo:
        self._validar_scope(contexto, dispositivo)
        documento = self._documento(dispositivo)
        resultado = await self._coleccion.insert_one(documento)
        documento["_id"] = resultado.inserted_id
        return self._entidad(documento)

    async def listar_por_cliente(
        self,
        contexto: ContextoTaller,
        cliente_id: str,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaDispositivos:
        filtro: dict[str, Any] = {
            "taller_id": contexto.taller_id,
            "cliente_id": cliente_id,
        }
        if cursor is not None:
            filtro["_id"] = {
                "$gt": self._decodificar_cursor(cursor, contexto.taller_id, cliente_id)
            }
        consulta = self._coleccion.find(filtro).sort("_id", ASCENDING).limit(limite + 1)
        documentos = [item async for item in consulta]
        visibles = documentos[:limite]
        siguiente = None
        if len(documentos) > limite and visibles:
            siguiente = self._codificar_cursor(
                contexto.taller_id, cliente_id, visibles[-1]["_id"]
            )
        return PaginaDispositivos(
            tuple(self._entidad(item) for item in visibles), siguiente
        )

    async def obtener(
        self, contexto: ContextoTaller, dispositivo_id: str
    ) -> Dispositivo | None:
        identificador = self._object_id(dispositivo_id)
        if identificador is None:
            return None
        documento = await self._coleccion.find_one(
            {"_id": identificador, "taller_id": contexto.taller_id}
        )
        return self._entidad(documento) if documento is not None else None

    async def actualizar(
        self, contexto: ContextoTaller, dispositivo: Dispositivo
    ) -> Dispositivo | None:
        self._validar_scope(contexto, dispositivo)
        identificador = self._object_id(dispositivo.id)
        if identificador is None:
            return None
        documento = await self._coleccion.find_one_and_update(
            {"_id": identificador, "taller_id": contexto.taller_id},
            {
                "$set": {
                    "modelo_id": dispositivo.modelo_id,
                    "identificador": dispositivo.identificador,
                    "notas": dispositivo.notas,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return self._entidad(documento) if documento is not None else None

    @staticmethod
    def _documento(dispositivo: Dispositivo) -> dict[str, Any]:
        return {
            "taller_id": dispositivo.taller_id,
            "cliente_id": dispositivo.cliente_id,
            "modelo_id": dispositivo.modelo_id,
            "identificador": dispositivo.identificador,
            "notas": dispositivo.notas,
        }

    @staticmethod
    def _entidad(documento: Mapping[str, Any]) -> Dispositivo:
        return Dispositivo(
            id=str(documento["_id"]),
            taller_id=str(documento["taller_id"]),
            cliente_id=str(documento["cliente_id"]),
            modelo_id=str(documento["modelo_id"]),
            identificador=documento.get("identificador"),
            notas=documento.get("notas"),
        )

    @staticmethod
    def _validar_scope(contexto: ContextoTaller, dispositivo: Dispositivo) -> None:
        if dispositivo.taller_id != contexto.taller_id:
            raise ValueError("El Dispositivo no pertenece al contexto de Taller.")

    @staticmethod
    def _object_id(valor: str | None) -> ObjectId | None:
        try:
            return ObjectId(valor) if valor is not None else None
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def _codificar_cursor(
        taller_id: str, cliente_id: str, dispositivo_id: ObjectId
    ) -> str:
        contenido = json.dumps(
            {"v": 1, "t": taller_id, "c": cliente_id, "id": str(dispositivo_id)},
            separators=(",", ":"),
        ).encode()
        return base64.urlsafe_b64encode(contenido).decode().rstrip("=")

    @staticmethod
    def _decodificar_cursor(cursor: str, taller_id: str, cliente_id: str) -> ObjectId:
        try:
            contenido = base64.b64decode(
                cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True
            )
            datos = json.loads(contenido)
            if not isinstance(datos, dict) or datos != {
                "v": 1,
                "t": taller_id,
                "c": cliente_id,
                "id": datos.get("id"),
            }:
                raise CursorDispositivosInvalido("Cursor de Dispositivos inválido.")
            return ObjectId(datos["id"])
        except (
            binascii.Error,
            UnicodeDecodeError,
            json.JSONDecodeError,
            InvalidId,
            KeyError,
            TypeError,
        ) as error:
            raise CursorDispositivosInvalido(
                "Cursor de Dispositivos inválido."
            ) from error
