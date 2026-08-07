"""Repositorio asíncrono de Clientes para MongoDB."""

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

from app.modules.clientes.application.errores import CursorClientesInvalido
from app.modules.clientes.application.puertos import PaginaClientes
from app.modules.clientes.domain.entidades import Cliente
from app.shared.application.contexto import ContextoTaller

COLECCION_CLIENTES = "clientes"


class RepositorioClientesMongo:
    """Implementa persistencia reforzando el scope por Taller en cada consulta."""

    def __init__(self, base_datos: AsyncDatabase[Any]) -> None:
        self._coleccion: AsyncCollection[dict[str, Any]] = base_datos[
            COLECCION_CLIENTES
        ]

    async def crear_indices(self) -> None:
        """Crea el índice que soporta listado tenant-scoped y paginación."""
        await self._coleccion.create_index(
            [("taller_id", ASCENDING), ("_id", ASCENDING)],
            name="clientes_por_taller_id",
        )

    async def crear(self, contexto: ContextoTaller, cliente: Cliente) -> Cliente:
        """Persiste un Cliente en el Taller autorizado."""
        self._validar_scope(contexto, cliente)
        documento = self._a_documento(cliente)
        resultado = await self._coleccion.insert_one(documento)
        documento["_id"] = resultado.inserted_id
        return self._a_entidad(documento)

    async def listar(
        self,
        contexto: ContextoTaller,
        *,
        limite: int,
        cursor: str | None,
    ) -> PaginaClientes:
        """Lista por Taller y `_id` ascendente con cursor estable."""
        filtro: dict[str, Any] = {"taller_id": contexto.taller_id}
        if cursor is not None:
            ultimo_id = self._decodificar_cursor(cursor, contexto.taller_id)
            filtro["_id"] = {"$gt": ultimo_id}

        cursor_mongo = (
            self._coleccion.find(filtro).sort("_id", ASCENDING).limit(limite + 1)
        )
        documentos = [documento async for documento in cursor_mongo]
        hay_siguiente = len(documentos) > limite
        visibles = documentos[:limite]
        siguiente = None
        if hay_siguiente and visibles:
            siguiente = self._codificar_cursor(contexto.taller_id, visibles[-1]["_id"])
        return PaginaClientes(
            items=tuple(self._a_entidad(documento) for documento in visibles),
            siguiente_cursor=siguiente,
        )

    async def obtener(
        self, contexto: ContextoTaller, cliente_id: str
    ) -> Cliente | None:
        """Busca por identificador y Taller en una misma consulta."""
        identificador = self._object_id_o_none(cliente_id)
        if identificador is None:
            return None
        documento = await self._coleccion.find_one(
            {"_id": identificador, "taller_id": contexto.taller_id}
        )
        return self._a_entidad(documento) if documento is not None else None

    async def actualizar(
        self, contexto: ContextoTaller, cliente: Cliente
    ) -> Cliente | None:
        """Actualiza por identificador y Taller en una operación atómica."""
        self._validar_scope(contexto, cliente)
        identificador = self._object_id_o_none(cliente.id)
        if identificador is None:
            return None

        cambios: dict[str, Any] = {"nombre": cliente.nombre}
        eliminados: dict[str, str] = {}
        for campo in ("telefono", "correo", "notas"):
            valor = getattr(cliente, campo)
            if valor is None:
                eliminados[campo] = ""
            else:
                cambios[campo] = valor

        actualizacion: dict[str, Any] = {"$set": cambios}
        if eliminados:
            actualizacion["$unset"] = eliminados
        documento = await self._coleccion.find_one_and_update(
            {"_id": identificador, "taller_id": contexto.taller_id},
            actualizacion,
            return_document=ReturnDocument.AFTER,
        )
        return self._a_entidad(documento) if documento is not None else None

    @staticmethod
    def _validar_scope(contexto: ContextoTaller, cliente: Cliente) -> None:
        if cliente.taller_id != contexto.taller_id:
            raise ValueError("El Cliente no pertenece al contexto de Taller.")

    @staticmethod
    def _object_id_o_none(valor: str | None) -> ObjectId | None:
        if valor is None:
            return None
        try:
            return ObjectId(valor)
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def _a_documento(cliente: Cliente) -> dict[str, Any]:
        documento: dict[str, Any] = {
            "taller_id": cliente.taller_id,
            "nombre": cliente.nombre,
        }
        for campo in ("telefono", "correo", "notas"):
            valor = getattr(cliente, campo)
            if valor is not None:
                documento[campo] = valor
        return documento

    @staticmethod
    def _a_entidad(documento: Mapping[str, Any]) -> Cliente:
        return Cliente(
            id=str(documento["_id"]),
            taller_id=str(documento["taller_id"]),
            nombre=str(documento["nombre"]),
            telefono=documento.get("telefono"),
            correo=documento.get("correo"),
            notas=documento.get("notas"),
        )

    @staticmethod
    def _codificar_cursor(taller_id: str, identificador: ObjectId) -> str:
        contenido = json.dumps(
            {"v": 1, "taller_id": taller_id, "id": str(identificador)},
            separators=(",", ":"),
        ).encode("utf-8")
        return base64.urlsafe_b64encode(contenido).decode("ascii").rstrip("=")

    @classmethod
    def _decodificar_cursor(cls, cursor: str, taller_id: str) -> ObjectId:
        try:
            relleno = "=" * (-len(cursor) % 4)
            contenido = base64.b64decode(
                cursor + relleno, altchars=b"-_", validate=True
            )
            datos = json.loads(contenido)
            if (
                not isinstance(datos, dict)
                or datos.get("v") != 1
                or datos.get("taller_id") != taller_id
                or not isinstance(datos.get("id"), str)
            ):
                raise CursorClientesInvalido("Cursor de Clientes inválido.")
            return ObjectId(datos["id"])
        except (
            binascii.Error,
            UnicodeDecodeError,
            json.JSONDecodeError,
            InvalidId,
            TypeError,
        ) as error:
            raise CursorClientesInvalido("Cursor de Clientes inválido.") from error
