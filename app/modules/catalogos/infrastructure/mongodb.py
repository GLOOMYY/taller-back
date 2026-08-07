"""Persistencia asíncrona y tenant-aware de catálogos."""

import base64
import binascii
import json
from collections.abc import Callable, Mapping
from typing import Any, TypeVar, cast

from bson import Decimal128, ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, ReturnDocument
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.modules.catalogos.application.errores import CursorCatalogoInvalido
from app.modules.catalogos.application.puertos import PaginaCatalogo
from app.modules.catalogos.domain import (
    EntradaCatalogo,
    MarcaDispositivo,
    ModeloDispositivo,
    TipoDispositivo,
    TipoServicio,
)
from app.shared.application.contexto import ContextoTaller
from app.shared.application.errores import Conflicto

COLECCION_TIPOS = "tipos_dispositivo"
COLECCION_MARCAS = "marcas_dispositivo"
COLECCION_MODELOS = "modelos_dispositivo"
COLECCION_SERVICIOS = "tipos_servicio"
T = TypeVar("T", bound=EntradaCatalogo)


class RepositorioCatalogosMongo:
    """Colecciones separadas con scope tenant en todos los accesos."""

    def __init__(self, base_datos: AsyncDatabase[Any]) -> None:
        self._tipos: AsyncCollection[dict[str, Any]] = base_datos[COLECCION_TIPOS]
        self._marcas: AsyncCollection[dict[str, Any]] = base_datos[COLECCION_MARCAS]
        self._modelos: AsyncCollection[dict[str, Any]] = base_datos[COLECCION_MODELOS]
        self._servicios: AsyncCollection[dict[str, Any]] = base_datos[
            COLECCION_SERVICIOS
        ]

    async def crear_indices(self) -> None:
        """Crea unicidades normalizadas y accesos tenant-scoped."""
        for coleccion, nombre in (
            (self._tipos, "tipos_dispositivo"),
            (self._marcas, "marcas_dispositivo"),
            (self._servicios, "tipos_servicio"),
        ):
            await coleccion.create_index(
                [("taller_id", ASCENDING), ("nombre_normalizado", ASCENDING)],
                unique=True,
                name=f"{nombre}_nombre_unico_por_taller",
            )
            await coleccion.create_index(
                [("taller_id", ASCENDING), ("_id", ASCENDING)],
                name=f"{nombre}_por_taller",
            )
        await self._modelos.create_index(
            [
                ("taller_id", ASCENDING),
                ("tipo_id", ASCENDING),
                ("marca_id", ASCENDING),
                ("nombre_normalizado", ASCENDING),
            ],
            unique=True,
            name="modelos_nombre_unico_por_tipo_marca_taller",
        )
        await self._modelos.create_index(
            [("taller_id", ASCENDING), ("_id", ASCENDING)],
            name="modelos_dispositivo_por_taller",
        )

    async def crear_tipo(
        self, contexto: ContextoTaller, item: TipoDispositivo
    ) -> TipoDispositivo:
        return cast(
            TipoDispositivo, await self._crear(self._tipos, contexto, item, self._tipo)
        )

    async def crear_marca(
        self, contexto: ContextoTaller, item: MarcaDispositivo
    ) -> MarcaDispositivo:
        return cast(
            MarcaDispositivo,
            await self._crear(self._marcas, contexto, item, self._marca),
        )

    async def crear_modelo(
        self, contexto: ContextoTaller, item: ModeloDispositivo
    ) -> ModeloDispositivo:
        return cast(
            ModeloDispositivo,
            await self._crear(self._modelos, contexto, item, self._modelo),
        )

    async def crear_tipo_servicio(
        self, contexto: ContextoTaller, item: TipoServicio
    ) -> TipoServicio:
        return cast(
            TipoServicio,
            await self._crear(self._servicios, contexto, item, self._servicio),
        )

    async def listar_tipos(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[TipoDispositivo]:
        return await self._listar(
            self._tipos, contexto, "tipo", limite, cursor, self._tipo
        )

    async def listar_marcas(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[MarcaDispositivo]:
        return cast(
            PaginaCatalogo[MarcaDispositivo],
            await self._listar(
                self._marcas, contexto, "marca", limite, cursor, self._marca
            ),
        )

    async def listar_modelos(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[ModeloDispositivo]:
        return cast(
            PaginaCatalogo[ModeloDispositivo],
            await self._listar(
                self._modelos, contexto, "modelo", limite, cursor, self._modelo
            ),
        )

    async def listar_tipos_servicio(
        self, contexto: ContextoTaller, *, limite: int, cursor: str | None
    ) -> PaginaCatalogo[TipoServicio]:
        return cast(
            PaginaCatalogo[TipoServicio],
            await self._listar(
                self._servicios,
                contexto,
                "tipo_servicio",
                limite,
                cursor,
                self._servicio,
            ),
        )

    async def obtener_tipo(
        self, contexto: ContextoTaller, item_id: str
    ) -> TipoDispositivo | None:
        return cast(
            TipoDispositivo | None,
            await self._obtener(self._tipos, contexto, item_id, self._tipo),
        )

    async def obtener_marca(
        self, contexto: ContextoTaller, item_id: str
    ) -> MarcaDispositivo | None:
        return cast(
            MarcaDispositivo | None,
            await self._obtener(self._marcas, contexto, item_id, self._marca),
        )

    async def obtener_modelo(
        self, contexto: ContextoTaller, item_id: str
    ) -> ModeloDispositivo | None:
        return cast(
            ModeloDispositivo | None,
            await self._obtener(self._modelos, contexto, item_id, self._modelo),
        )

    async def obtener_tipo_servicio(
        self, contexto: ContextoTaller, item_id: str
    ) -> TipoServicio | None:
        return cast(
            TipoServicio | None,
            await self._obtener(self._servicios, contexto, item_id, self._servicio),
        )

    async def actualizar_tipo(
        self, contexto: ContextoTaller, item: TipoDispositivo
    ) -> TipoDispositivo | None:
        return cast(
            TipoDispositivo | None,
            await self._actualizar(self._tipos, contexto, item, self._tipo),
        )

    async def actualizar_marca(
        self, contexto: ContextoTaller, item: MarcaDispositivo
    ) -> MarcaDispositivo | None:
        return cast(
            MarcaDispositivo | None,
            await self._actualizar(self._marcas, contexto, item, self._marca),
        )

    async def actualizar_modelo(
        self, contexto: ContextoTaller, item: ModeloDispositivo
    ) -> ModeloDispositivo | None:
        return cast(
            ModeloDispositivo | None,
            await self._actualizar(self._modelos, contexto, item, self._modelo),
        )

    async def actualizar_tipo_servicio(
        self, contexto: ContextoTaller, item: TipoServicio
    ) -> TipoServicio | None:
        return cast(
            TipoServicio | None,
            await self._actualizar(self._servicios, contexto, item, self._servicio),
        )

    async def _crear(
        self,
        coleccion: AsyncCollection[dict[str, Any]],
        contexto: ContextoTaller,
        item: EntradaCatalogo,
        traductor: Callable[[Mapping[str, Any]], T],
    ) -> T:
        self._validar_scope(contexto, item)
        documento = self._documento(item)
        try:
            resultado = await coleccion.insert_one(documento)
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un valor de catálogo con ese nombre.") from error
        documento["_id"] = resultado.inserted_id
        return traductor(documento)

    async def _listar(
        self,
        coleccion: AsyncCollection[dict[str, Any]],
        contexto: ContextoTaller,
        clase: str,
        limite: int,
        cursor: str | None,
        traductor: Callable[[Mapping[str, Any]], T],
    ) -> PaginaCatalogo[T]:
        filtro: dict[str, Any] = {"taller_id": contexto.taller_id}
        if cursor is not None:
            filtro["_id"] = {
                "$gt": self._decodificar_cursor(cursor, contexto.taller_id, clase)
            }
        consulta = coleccion.find(filtro).sort("_id", ASCENDING).limit(limite + 1)
        documentos = [item async for item in consulta]
        visibles = documentos[:limite]
        siguiente = None
        if len(documentos) > limite and visibles:
            siguiente = self._codificar_cursor(
                contexto.taller_id, clase, visibles[-1]["_id"]
            )
        return PaginaCatalogo(tuple(traductor(item) for item in visibles), siguiente)

    async def _obtener(
        self,
        coleccion: AsyncCollection[dict[str, Any]],
        contexto: ContextoTaller,
        item_id: str,
        traductor: Callable[[Mapping[str, Any]], T],
    ) -> T | None:
        identificador = self._object_id(item_id)
        if identificador is None:
            return None
        documento = await coleccion.find_one(
            {"_id": identificador, "taller_id": contexto.taller_id}
        )
        return traductor(documento) if documento is not None else None

    async def _actualizar(
        self,
        coleccion: AsyncCollection[dict[str, Any]],
        contexto: ContextoTaller,
        item: EntradaCatalogo,
        traductor: Callable[[Mapping[str, Any]], T],
    ) -> T | None:
        self._validar_scope(contexto, item)
        identificador = self._object_id(item.id)
        if identificador is None:
            return None
        cambios = self._documento(item)
        cambios.pop("taller_id")
        try:
            documento = await coleccion.find_one_and_update(
                {"_id": identificador, "taller_id": contexto.taller_id},
                {"$set": cambios},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un valor de catálogo con ese nombre.") from error
        return traductor(documento) if documento is not None else None

    @staticmethod
    def _documento(item: EntradaCatalogo) -> dict[str, Any]:
        documento: dict[str, Any] = {
            "taller_id": item.taller_id,
            "nombre": item.nombre,
            "nombre_normalizado": item.nombre_normalizado,
            "activo": item.activo,
        }
        if isinstance(item, ModeloDispositivo):
            documento.update(tipo_id=item.tipo_id, marca_id=item.marca_id)
        if isinstance(item, TipoServicio):
            documento["precio_predeterminado"] = Decimal128(item.precio_predeterminado)
            if item.descripcion is not None:
                documento["descripcion"] = item.descripcion
            else:
                documento["descripcion"] = None
        return documento

    @staticmethod
    def _base(item: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "id": str(item["_id"]),
            "taller_id": str(item["taller_id"]),
            "nombre": str(item["nombre"]),
            "nombre_normalizado": str(item["nombre_normalizado"]),
            "activo": bool(item["activo"]),
        }

    @classmethod
    def _tipo(cls, item: Mapping[str, Any]) -> TipoDispositivo:
        return TipoDispositivo(**cls._base(item))

    @classmethod
    def _marca(cls, item: Mapping[str, Any]) -> MarcaDispositivo:
        return MarcaDispositivo(**cls._base(item))

    @classmethod
    def _modelo(cls, item: Mapping[str, Any]) -> ModeloDispositivo:
        return ModeloDispositivo(
            **cls._base(item),
            tipo_id=str(item["tipo_id"]),
            marca_id=str(item["marca_id"]),
        )

    @classmethod
    def _servicio(cls, item: Mapping[str, Any]) -> TipoServicio:
        precio = item["precio_predeterminado"]
        return TipoServicio(
            **cls._base(item),
            descripcion=cast(str | None, item.get("descripcion")),
            precio_predeterminado=(
                precio.to_decimal() if isinstance(precio, Decimal128) else precio
            ),
        )

    @staticmethod
    def _validar_scope(contexto: ContextoTaller, item: EntradaCatalogo) -> None:
        if item.taller_id != contexto.taller_id:
            raise ValueError("El valor no pertenece al contexto de Taller.")

    @staticmethod
    def _object_id(valor: str | None) -> ObjectId | None:
        try:
            return ObjectId(valor) if valor is not None else None
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def _codificar_cursor(taller_id: str, clase: str, item_id: ObjectId) -> str:
        contenido = json.dumps(
            {"v": 1, "t": taller_id, "c": clase, "id": str(item_id)},
            separators=(",", ":"),
        ).encode()
        return base64.urlsafe_b64encode(contenido).decode().rstrip("=")

    @staticmethod
    def _decodificar_cursor(cursor: str, taller_id: str, clase: str) -> ObjectId:
        try:
            contenido = base64.b64decode(
                cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True
            )
            datos = json.loads(contenido)
            if not isinstance(datos, dict) or datos != {
                "v": 1,
                "t": taller_id,
                "c": clase,
                "id": datos.get("id"),
            }:
                raise CursorCatalogoInvalido("Cursor de catálogo inválido.")
            return ObjectId(datos["id"])
        except (
            binascii.Error,
            UnicodeDecodeError,
            json.JSONDecodeError,
            InvalidId,
            KeyError,
            TypeError,
        ) as error:
            raise CursorCatalogoInvalido("Cursor de catálogo inválido.") from error
