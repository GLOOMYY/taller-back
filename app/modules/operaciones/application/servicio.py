"""Casos de uso asíncronos para Órdenes, stock y Pagos."""

from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

from bson import ObjectId
from bson.decimal128 import Decimal128
from bson.errors import InvalidId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.modules.operaciones.domain.dinero import Dinero, calcular_totales
from app.shared.application import Conflicto, NoEncontrado
from app.shared.application.contexto import ContextoTaller

TRANSICIONES: dict[str, set[str]] = {
    "abierta": {"en_proceso"},
    "en_proceso": {"espera_repuesto", "pendiente_recogida"},
    "espera_repuesto": {"en_proceso"},
    "pendiente_recogida": {"entregado"},
    "entregado": set(),
}


def _ahora() -> datetime:
    return datetime.now(UTC)


def _decimal(valor: Any) -> Decimal:
    if isinstance(valor, Decimal128):
        return valor.to_decimal()
    return Decimal(str(valor))


def _id_mongo(valor: str) -> str | ObjectId:
    """Traduce IDs opacos de módulos que persisten mediante ObjectId."""
    try:
        return ObjectId(valor)
    except (InvalidId, TypeError):
        return valor


def _serializar(valor: Any) -> Any:
    if isinstance(valor, Decimal128):
        return format(valor.to_decimal(), "f")
    if isinstance(valor, Decimal):
        return format(valor, "f")
    if isinstance(valor, datetime):
        return valor.isoformat()
    if isinstance(valor, ObjectId):
        return str(valor)
    if isinstance(valor, list):
        return [_serializar(item) for item in valor]
    if isinstance(valor, Mapping):
        return {
            ("id" if clave == "_id" else str(clave)): _serializar(item)
            for clave, item in valor.items()
        }
    return valor


def _salida(documento: Any) -> dict[str, Any]:
    """Acota el documento serializado en el límite de aplicación."""
    return cast(dict[str, Any], _serializar(documento))


class ServicioOperaciones:
    """Coordina invariantes que atraviesan Órdenes, inventario y finanzas."""

    def __init__(self, base_datos: Any, cliente_mongodb: Any) -> None:
        self._db = base_datos
        self._cliente = cliente_mongodb

    async def crear_indices(self) -> None:
        """Crea índices tenant-first y unicidades operativas."""
        await self._db.proveedores.create_index(
            [("taller_id", 1), ("nombre_normalizado", 1)], unique=True
        )
        await self._db.repuestos.create_index(
            [("taller_id", 1), ("codigo", 1)],
            unique=True,
            partialFilterExpression={"codigo": {"$type": "string"}},
        )
        await self._db.repuestos.create_index([("taller_id", 1), ("_id", 1)])
        await self._db.movimientos_stock.create_index(
            [("taller_id", 1), ("repuesto_id", 1), ("_id", 1)]
        )
        await self._db.metodos_pago.create_index(
            [("taller_id", 1), ("nombre_normalizado", 1)], unique=True
        )
        await self._db.ordenes.create_index(
            [("taller_id", 1), ("consecutivo", 1)], unique=True
        )
        await self._db.ordenes.create_index(
            [("taller_id", 1), ("dispositivo_id", 1), ("_id", 1)]
        )
        await self._db.historial_ordenes.create_index(
            [("taller_id", 1), ("orden_id", 1), ("_id", 1)]
        )
        await self._db.pagos.create_index(
            [("taller_id", 1), ("orden_id", 1), ("_id", 1)]
        )

    async def crear_proveedor(
        self, contexto: ContextoTaller, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        nombre = str(datos["nombre"]).strip()
        documento = {
            "_id": str(uuid4()),
            "taller_id": contexto.taller_id,
            "nombre": nombre,
            "nombre_normalizado": nombre.casefold(),
            "contacto": datos.get("contacto"),
            "notas": datos.get("notas"),
            "activo": True,
        }
        try:
            await self._db.proveedores.insert_one(documento)
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un Proveedor con ese nombre") from error
        return _salida(documento)

    async def listar_proveedores(
        self, contexto: ContextoTaller, activo: bool | None = None
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {"taller_id": contexto.taller_id}
        if activo is not None:
            filtro["activo"] = activo
        cursor = self._db.proveedores.find(filtro).sort("_id", 1)
        return [_serializar(item) async for item in cursor]

    async def obtener_proveedor(
        self, contexto: ContextoTaller, proveedor_id: str
    ) -> dict[str, Any]:
        documento = await self._db.proveedores.find_one(
            {"_id": proveedor_id, "taller_id": contexto.taller_id}
        )
        if documento is None:
            raise NoEncontrado("Proveedor no encontrado")
        return _salida(documento)

    async def actualizar_proveedor(
        self,
        contexto: ContextoTaller,
        proveedor_id: str,
        cambios: Mapping[str, Any],
    ) -> dict[str, Any]:
        permitidos = {"nombre", "contacto", "notas", "activo"}
        actualizacion = {k: v for k, v in cambios.items() if k in permitidos}
        if "nombre" in actualizacion:
            actualizacion["nombre"] = str(actualizacion["nombre"]).strip()
            actualizacion["nombre_normalizado"] = actualizacion["nombre"].casefold()
        try:
            documento = await self._db.proveedores.find_one_and_update(
                {"_id": proveedor_id, "taller_id": contexto.taller_id},
                {"$set": actualizacion},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un Proveedor con ese nombre") from error
        if documento is None:
            raise NoEncontrado("Proveedor no encontrado")
        return _salida(documento)

    async def crear_repuesto(
        self, contexto: ContextoTaller, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        precio = Dinero.desde_texto(
            str(datos["precio_venta"]),
            str(datos.get("moneda_codigo", "COP")),
            int(datos.get("moneda_decimales", 2)),
        )
        codigo = datos.get("codigo")
        documento = {
            "_id": str(uuid4()),
            "taller_id": contexto.taller_id,
            "codigo": str(codigo).strip() if codigo else None,
            "nombre": str(datos["nombre"]).strip(),
            "descripcion": datos.get("descripcion"),
            "precio_venta": Decimal128(precio.importe),
            "existencia": 0,
            "activo": True,
        }
        try:
            await self._db.repuestos.insert_one(documento)
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un Repuesto con ese código") from error
        return _salida(documento)

    async def listar_repuestos(
        self, contexto: ContextoTaller, activo: bool | None = None
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {"taller_id": contexto.taller_id}
        if activo is not None:
            filtro["activo"] = activo
        cursor = self._db.repuestos.find(filtro).sort("_id", 1)
        return [_serializar(item) async for item in cursor]

    async def obtener_repuesto(
        self, contexto: ContextoTaller, repuesto_id: str
    ) -> dict[str, Any]:
        documento = await self._db.repuestos.find_one(
            {"_id": repuesto_id, "taller_id": contexto.taller_id}
        )
        if documento is None:
            raise NoEncontrado("Repuesto no encontrado")
        return _salida(documento)

    async def actualizar_repuesto(
        self,
        contexto: ContextoTaller,
        repuesto_id: str,
        cambios: Mapping[str, Any],
    ) -> dict[str, Any]:
        permitidos = {"codigo", "nombre", "descripcion", "activo"}
        actualizacion = {k: v for k, v in cambios.items() if k in permitidos}
        if "precio_venta" in cambios:
            actualizacion["precio_venta"] = Decimal128(
                Dinero.desde_texto(
                    str(cambios["precio_venta"]),
                    str(cambios.get("moneda_codigo", "COP")),
                    int(cambios.get("moneda_decimales", 2)),
                ).importe
            )
        try:
            documento = await self._db.repuestos.find_one_and_update(
                {"_id": repuesto_id, "taller_id": contexto.taller_id},
                {"$set": actualizacion},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un Repuesto con ese código") from error
        if documento is None:
            raise NoEncontrado("Repuesto no encontrado")
        return _salida(documento)

    async def entrada_stock(
        self, contexto: ContextoTaller, repuesto_id: str, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        cantidad = int(datos["cantidad"])
        if cantidad <= 0:
            raise ValueError("la cantidad debe ser positiva")
        proveedor_id = datos.get("proveedor_id")
        if proveedor_id and not await self._db.proveedores.find_one(
            {"_id": proveedor_id, "taller_id": contexto.taller_id, "activo": True}
        ):
            raise NoEncontrado("Proveedor no encontrado")
        costo = Dinero.desde_texto(
            str(datos["costo_unitario"]),
            str(datos.get("moneda_codigo", "COP")),
            int(datos.get("moneda_decimales", 2)),
        )
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                repuesto = await self._db.repuestos.find_one_and_update(
                    {
                        "_id": repuesto_id,
                        "taller_id": contexto.taller_id,
                        "activo": True,
                    },
                    {"$inc": {"existencia": cantidad}},
                    return_document=ReturnDocument.AFTER,
                    session=sesion,
                )
                if repuesto is None:
                    raise NoEncontrado("Repuesto no encontrado")
                movimiento = await self._movimiento(
                    contexto,
                    repuesto_id,
                    "entrada",
                    cantidad,
                    session=sesion,
                    costo_unitario=costo.importe,
                    proveedor_id=proveedor_id,
                    nota=datos.get("nota"),
                )
        return _salida(movimiento)

    async def ajustar_stock(
        self, contexto: ContextoTaller, repuesto_id: str, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        delta = int(datos["delta"])
        motivo = str(datos["motivo"]).strip()
        if delta == 0 or not motivo:
            raise ValueError("delta no cero y motivo son obligatorios")
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                repuesto = await self._db.repuestos.find_one_and_update(
                    {
                        "_id": repuesto_id,
                        "taller_id": contexto.taller_id,
                        "existencia": {"$gte": -delta} if delta < 0 else {"$gte": 0},
                    },
                    {"$inc": {"existencia": delta}},
                    return_document=ReturnDocument.AFTER,
                    session=sesion,
                )
                if repuesto is None:
                    raise Conflicto("El ajuste dejaría existencia negativa")
                movimiento = await self._movimiento(
                    contexto,
                    repuesto_id,
                    "ajuste",
                    delta,
                    session=sesion,
                    motivo=motivo,
                )
        return _salida(movimiento)

    async def listar_movimientos(
        self, contexto: ContextoTaller, repuesto_id: str
    ) -> list[dict[str, Any]]:
        if not await self._db.repuestos.find_one(
            {"_id": repuesto_id, "taller_id": contexto.taller_id}
        ):
            raise NoEncontrado("Repuesto no encontrado")
        cursor = self._db.movimientos_stock.find(
            {"taller_id": contexto.taller_id, "repuesto_id": repuesto_id}
        ).sort([("creado_en", 1), ("_id", 1)])
        return [_serializar(item) async for item in cursor]

    async def _movimiento(
        self,
        contexto: ContextoTaller,
        repuesto_id: str,
        tipo: str,
        cantidad: int,
        *,
        session: Any,
        **detalles: Any,
    ) -> dict[str, Any]:
        documento = {
            "_id": str(uuid4()),
            "taller_id": contexto.taller_id,
            "repuesto_id": repuesto_id,
            "tipo": tipo,
            "cantidad": cantidad,
            "creado_en": _ahora(),
            **{
                clave: Decimal128(valor) if isinstance(valor, Decimal) else valor
                for clave, valor in detalles.items()
                if valor is not None
            },
        }
        await self._db.movimientos_stock.insert_one(documento, session=session)
        return documento

    async def crear_metodo_pago(
        self, contexto: ContextoTaller, nombre: str
    ) -> dict[str, Any]:
        limpio = nombre.strip()
        documento = {
            "_id": str(uuid4()),
            "taller_id": contexto.taller_id,
            "nombre": limpio,
            "nombre_normalizado": limpio.casefold(),
            "activo": True,
        }
        try:
            await self._db.metodos_pago.insert_one(documento)
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un método de pago con ese nombre") from error
        return _salida(documento)

    async def listar_metodos_pago(
        self, contexto: ContextoTaller, activo: bool | None = None
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {"taller_id": contexto.taller_id}
        if activo is not None:
            filtro["activo"] = activo
        cursor = self._db.metodos_pago.find(filtro).sort("_id", 1)
        return [_serializar(item) async for item in cursor]

    async def actualizar_metodo_pago(
        self,
        contexto: ContextoTaller,
        metodo_id: str,
        cambios: Mapping[str, Any],
    ) -> dict[str, Any]:
        actualizacion: dict[str, Any] = {}
        if "nombre" in cambios:
            nombre = str(cambios["nombre"]).strip()
            actualizacion.update(nombre=nombre, nombre_normalizado=nombre.casefold())
        if "activo" in cambios:
            actualizacion["activo"] = bool(cambios["activo"])
        try:
            documento = await self._db.metodos_pago.find_one_and_update(
                {"_id": metodo_id, "taller_id": contexto.taller_id},
                {"$set": actualizacion},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError as error:
            raise Conflicto("Ya existe un método de pago con ese nombre") from error
        if documento is None:
            raise NoEncontrado("Método de pago no encontrado")
        return _salida(documento)

    async def crear_orden(
        self,
        contexto: ContextoTaller,
        datos: Mapping[str, Any],
        moneda: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if moneda is None:
            taller = await self._db.talleres.find_one({"_id": contexto.taller_id})
            if taller is None:
                raise NoEncontrado("Taller no encontrado")
            codigo = str(taller["moneda_codigo"])
            referencia = await self._db.referencias_monedas.find_one({"codigo": codigo})
            if referencia is None:
                raise NoEncontrado("Moneda no encontrada")
            moneda = referencia
        dispositivo_id = str(datos["dispositivo_id"])
        dispositivo = await self._db.dispositivos.find_one(
            {"_id": _id_mongo(dispositivo_id), "taller_id": contexto.taller_id}
        )
        if dispositivo is None:
            raise NoEncontrado("Dispositivo no encontrado")
        falla = str(datos["falla_reportada"]).strip()
        if not falla:
            raise ValueError("falla_reportada es obligatoria")
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                contador = await self._db.contadores.find_one_and_update(
                    {"taller_id": contexto.taller_id, "tipo": "orden"},
                    {"$inc": {"valor": 1}},
                    upsert=True,
                    return_document=ReturnDocument.AFTER,
                    session=sesion,
                )
                consecutivo = int(contador["valor"])
                orden_id = str(uuid4())
                documento: dict[str, Any] = {
                    "_id": orden_id,
                    "taller_id": contexto.taller_id,
                    "consecutivo": consecutivo,
                    "dispositivo_id": dispositivo_id,
                    "estado": "abierta",
                    "falla_reportada": falla,
                    "diagnostico": datos.get("diagnostico"),
                    "trabajo_realizado": datos.get("trabajo_realizado"),
                    "accesorios_recibidos": datos.get("accesorios_recibidos"),
                    "notas": datos.get("notas"),
                    "servicios": [],
                    "repuestos": [],
                    "descuento": None,
                    "subtotal": Decimal128("0"),
                    "descuento_total": Decimal128("0"),
                    "total": Decimal128("0"),
                    "moneda": {
                        "codigo": str(moneda["codigo"]),
                        "nombre": str(moneda["nombre"]),
                        "simbolo": str(moneda["simbolo"]),
                        "decimales": int(moneda["decimales"]),
                    },
                    "seguimiento_version": 0,
                    "seguimiento_habilitado": False,
                    "creado_en": _ahora(),
                    "actualizado_en": _ahora(),
                }
                await self._db.ordenes.insert_one(documento, session=sesion)
                await self._db.finanzas_ordenes.insert_one(
                    {
                        "_id": orden_id,
                        "taller_id": contexto.taller_id,
                        "total": Decimal128("0"),
                        "pagado": Decimal128("0"),
                        "saldo": Decimal128("0"),
                    },
                    session=sesion,
                )
                await self._historial(
                    contexto, orden_id, "creacion", {}, session=sesion
                )
        return _salida(documento)

    async def listar_ordenes(
        self, contexto: ContextoTaller, dispositivo_id: str | None = None
    ) -> list[dict[str, Any]]:
        filtro: dict[str, Any] = {"taller_id": contexto.taller_id}
        if dispositivo_id:
            filtro["dispositivo_id"] = dispositivo_id
        cursor = self._db.ordenes.find(filtro).sort("consecutivo", 1)
        return [_serializar(item) async for item in cursor]

    async def obtener_orden(
        self, contexto: ContextoTaller, orden_id: str
    ) -> dict[str, Any]:
        documento = await self._orden(contexto, orden_id)
        finanzas = await self._db.finanzas_ordenes.find_one(
            {"_id": orden_id, "taller_id": contexto.taller_id}
        )
        salida = _salida(documento)
        salida["pagado"] = _serializar(finanzas["pagado"] if finanzas else 0)
        salida["saldo"] = _serializar(finanzas["saldo"] if finanzas else 0)
        return salida

    async def actualizar_orden(
        self,
        contexto: ContextoTaller,
        orden_id: str,
        cambios: Mapping[str, Any],
    ) -> dict[str, Any]:
        orden = await self._orden(contexto, orden_id)
        self._mutable(orden)
        permitidos = {
            "falla_reportada",
            "diagnostico",
            "trabajo_realizado",
            "accesorios_recibidos",
            "notas",
        }
        actualizacion = {k: v for k, v in cambios.items() if k in permitidos}
        if (
            "falla_reportada" in actualizacion
            and not str(actualizacion["falla_reportada"]).strip()
        ):
            raise ValueError("falla_reportada es obligatoria")
        actualizacion["actualizado_en"] = _ahora()
        documento = await self._db.ordenes.find_one_and_update(
            {"_id": orden_id, "taller_id": contexto.taller_id},
            {"$set": actualizacion},
            return_document=ReturnDocument.AFTER,
        )
        await self._historial(contexto, orden_id, "campos", actualizacion)
        return _salida(documento)

    async def transicionar(
        self, contexto: ContextoTaller, orden_id: str, estado: str
    ) -> dict[str, Any]:
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                actual = str(orden["estado"])
                if estado not in TRANSICIONES.get(actual, set()):
                    raise Conflicto(f"Transición {actual} -> {estado} no permitida")
                if estado == "entregado":
                    finanzas = await self._db.finanzas_ordenes.find_one(
                        {"_id": orden_id, "taller_id": contexto.taller_id},
                        session=sesion,
                    )
                    if finanzas is None or _decimal(finanzas["saldo"]) != 0:
                        raise Conflicto("La Orden requiere saldo cero para entregarse")
                await self._db.ordenes.update_one(
                    {"_id": orden_id, "taller_id": contexto.taller_id},
                    {"$set": {"estado": estado, "actualizado_en": _ahora()}},
                    session=sesion,
                )
                await self._historial(
                    contexto,
                    orden_id,
                    "estado",
                    {"anterior": actual, "nuevo": estado},
                    session=sesion,
                )
                orden["estado"] = estado
        return _salida(orden)

    async def reabrir_garantia(
        self, contexto: ContextoTaller, orden_id: str, motivo: str
    ) -> dict[str, Any]:
        if not motivo.strip():
            raise ValueError("el motivo es obligatorio")
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                if orden["estado"] != "entregado":
                    raise Conflicto(
                        "Solo una Orden entregada puede reabrirse por garantía"
                    )
                await self._db.ordenes.update_one(
                    {"_id": orden_id, "taller_id": contexto.taller_id},
                    {"$set": {"estado": "en_proceso", "actualizado_en": _ahora()}},
                    session=sesion,
                )
                await self._historial(
                    contexto,
                    orden_id,
                    "garantia",
                    {"motivo": motivo.strip()},
                    session=sesion,
                )
                orden["estado"] = "en_proceso"
        return _salida(orden)

    async def agregar_servicio(
        self, contexto: ContextoTaller, orden_id: str, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        tipo_id = str(datos["tipo_servicio_id"])
        tipo = await self._db.tipos_servicio.find_one(
            {
                "_id": _id_mongo(tipo_id),
                "taller_id": contexto.taller_id,
                "activo": True,
            }
        )
        if tipo is None:
            raise NoEncontrado("Tipo de servicio no encontrado")
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                self._mutable(orden)
                dinero = self._dinero_orden(
                    orden,
                    str(
                        datos.get("precio_unitario")
                        or _decimal(tipo["precio_predeterminado"])
                    ),
                )
                linea: dict[str, Any] = {
                    "id": str(uuid4()),
                    "tipo_servicio_id": tipo_id,
                    "nombre": str(tipo["nombre"]),
                    "cantidad": int(datos.get("cantidad", 1)),
                    "precio_unitario": Decimal128(dinero.importe),
                    "domicilio": bool(datos.get("domicilio", False)),
                }
                if linea["cantidad"] <= 0:
                    raise ValueError("la cantidad debe ser positiva")
                orden["servicios"].append(linea)
                await self._guardar_totales(contexto, orden, session=sesion)
                await self._historial(
                    contexto, orden_id, "servicio_agregado", linea, session=sesion
                )
        return _salida(linea)

    async def retirar_servicio(
        self, contexto: ContextoTaller, orden_id: str, linea_id: str
    ) -> None:
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                self._mutable(orden)
                restantes = [x for x in orden["servicios"] if x["id"] != linea_id]
                if len(restantes) == len(orden["servicios"]):
                    raise NoEncontrado("Línea de servicio no encontrada")
                orden["servicios"] = restantes
                await self._guardar_totales(contexto, orden, session=sesion)
                await self._historial(
                    contexto,
                    orden_id,
                    "servicio_retirado",
                    {"linea_id": linea_id},
                    session=sesion,
                )

    async def agregar_repuesto_orden(
        self, contexto: ContextoTaller, orden_id: str, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        repuesto_id = str(datos["repuesto_id"])
        cantidad = int(datos.get("cantidad", 1))
        if cantidad <= 0:
            raise ValueError("la cantidad debe ser positiva")
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                self._mutable(orden)
                repuesto = await self._db.repuestos.find_one_and_update(
                    {
                        "_id": repuesto_id,
                        "taller_id": contexto.taller_id,
                        "activo": True,
                        "existencia": {"$gte": cantidad},
                    },
                    {"$inc": {"existencia": -cantidad}},
                    return_document=ReturnDocument.AFTER,
                    session=sesion,
                )
                if repuesto is None:
                    raise Conflicto(
                        "Repuesto inactivo, inexistente o sin stock suficiente"
                    )
                dinero = self._dinero_orden(
                    orden,
                    str(
                        datos.get("precio_unitario")
                        or _decimal(repuesto["precio_venta"])
                    ),
                )
                linea: dict[str, Any] = {
                    "id": str(uuid4()),
                    "repuesto_id": repuesto_id,
                    "nombre": str(repuesto["nombre"]),
                    "cantidad": cantidad,
                    "precio_unitario": Decimal128(dinero.importe),
                }
                orden["repuestos"].append(linea)
                await self._guardar_totales(contexto, orden, session=sesion)
                await self._movimiento(
                    contexto,
                    repuesto_id,
                    "consumo_orden",
                    -cantidad,
                    session=sesion,
                    orden_id=orden_id,
                    linea_id=linea["id"],
                )
                await self._historial(
                    contexto, orden_id, "repuesto_agregado", linea, session=sesion
                )
        return _salida(linea)

    async def retirar_repuesto_orden(
        self, contexto: ContextoTaller, orden_id: str, linea_id: str
    ) -> None:
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                self._mutable(orden)
                linea = next(
                    (x for x in orden["repuestos"] if x["id"] == linea_id), None
                )
                if linea is None:
                    raise NoEncontrado("Línea de Repuesto no encontrada")
                orden["repuestos"] = [
                    x for x in orden["repuestos"] if x["id"] != linea_id
                ]
                await self._guardar_totales(contexto, orden, session=sesion)
                await self._db.repuestos.update_one(
                    {"_id": linea["repuesto_id"], "taller_id": contexto.taller_id},
                    {"$inc": {"existencia": int(linea["cantidad"])}},
                    session=sesion,
                )
                await self._movimiento(
                    contexto,
                    str(linea["repuesto_id"]),
                    "reversion_consumo",
                    int(linea["cantidad"]),
                    session=sesion,
                    orden_id=orden_id,
                    linea_id=linea_id,
                )
                await self._historial(
                    contexto,
                    orden_id,
                    "repuesto_retirado",
                    {"linea_id": linea_id},
                    session=sesion,
                )

    async def aplicar_descuento(
        self, contexto: ContextoTaller, orden_id: str, tipo: str, valor: str
    ) -> dict[str, Any]:
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                self._mutable(orden)
                dinero = self._dinero_orden(orden, valor)
                if tipo not in {"fijo", "porcentaje"}:
                    raise ValueError("tipo de descuento inválido")
                orden["descuento"] = {
                    "tipo": tipo,
                    "valor": Decimal128(dinero.importe),
                }
                await self._guardar_totales(contexto, orden, session=sesion)
                await self._historial(
                    contexto,
                    orden_id,
                    "descuento",
                    orden["descuento"],
                    session=sesion,
                )
        return _salida(orden)

    async def registrar_pago(
        self, contexto: ContextoTaller, orden_id: str, datos: Mapping[str, Any]
    ) -> dict[str, Any]:
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                orden = await self._orden(contexto, orden_id, session=sesion)
                self._mutable(orden)
                lineas_entrada = list(datos["lineas"])
                if not lineas_entrada:
                    raise ValueError("el Pago requiere al menos una línea")
                lineas: list[dict[str, Any]] = []
                suma = Decimal("0")
                for entrada in lineas_entrada:
                    metodo = await self._db.metodos_pago.find_one(
                        {
                            "_id": str(entrada["metodo_pago_id"]),
                            "taller_id": contexto.taller_id,
                            "activo": True,
                        },
                        session=sesion,
                    )
                    if metodo is None:
                        raise NoEncontrado("Método de pago no encontrado")
                    importe = self._dinero_orden(orden, str(entrada["monto"])).importe
                    if importe <= 0:
                        raise ValueError("cada monto debe ser positivo")
                    suma += importe
                    lineas.append(
                        {
                            "metodo_pago_id": str(metodo["_id"]),
                            "metodo_nombre": str(metodo["nombre"]),
                            "monto": Decimal128(importe),
                        }
                    )
                total_declarado = self._dinero_orden(
                    orden, str(datos.get("total", suma))
                ).importe
                if suma != total_declarado:
                    raise ValueError("la suma de líneas debe coincidir con el total")
                finanzas = await self._db.finanzas_ordenes.find_one_and_update(
                    {
                        "_id": orden_id,
                        "taller_id": contexto.taller_id,
                        "saldo": {"$gte": Decimal128(total_declarado)},
                    },
                    {
                        "$inc": {
                            "pagado": Decimal128(total_declarado),
                            "saldo": Decimal128(-total_declarado),
                        }
                    },
                    return_document=ReturnDocument.AFTER,
                    session=sesion,
                )
                if finanzas is None:
                    raise Conflicto("El Pago supera el saldo de la Orden")
                pago = {
                    "_id": str(uuid4()),
                    "taller_id": contexto.taller_id,
                    "orden_id": orden_id,
                    "total": Decimal128(total_declarado),
                    "lineas": lineas,
                    "estado": "confirmado",
                    "creado_en": _ahora(),
                }
                await self._db.pagos.insert_one(pago, session=sesion)
                await self._historial(
                    contexto,
                    orden_id,
                    "pago",
                    {"pago_id": pago["_id"], "total": pago["total"]},
                    session=sesion,
                )
        return _salida(pago)

    async def listar_pagos(
        self, contexto: ContextoTaller, orden_id: str
    ) -> list[dict[str, Any]]:
        await self._orden(contexto, orden_id)
        cursor = self._db.pagos.find(
            {"taller_id": contexto.taller_id, "orden_id": orden_id}
        ).sort([("creado_en", 1), ("_id", 1)])
        return [_serializar(item) async for item in cursor]

    async def anular_pago(
        self, contexto: ContextoTaller, pago_id: str, motivo: str
    ) -> dict[str, Any]:
        if not motivo.strip():
            raise ValueError("el motivo es obligatorio")
        async with self._cliente.start_session() as sesion:
            async with await sesion.start_transaction():
                pago = await self._db.pagos.find_one(
                    {
                        "_id": pago_id,
                        "taller_id": contexto.taller_id,
                        "estado": "confirmado",
                    },
                    session=sesion,
                )
                if pago is None:
                    raise NoEncontrado("Pago confirmado no encontrado")
                orden = await self._orden(
                    contexto, str(pago["orden_id"]), session=sesion
                )
                self._mutable(orden)
                total = _decimal(pago["total"])
                await self._db.finanzas_ordenes.update_one(
                    {"_id": pago["orden_id"], "taller_id": contexto.taller_id},
                    {
                        "$inc": {
                            "pagado": Decimal128(-total),
                            "saldo": Decimal128(total),
                        }
                    },
                    session=sesion,
                )
                await self._db.pagos.update_one(
                    {"_id": pago_id, "taller_id": contexto.taller_id},
                    {
                        "$set": {
                            "estado": "anulado",
                            "motivo_anulacion": motivo.strip(),
                            "anulado_en": _ahora(),
                        }
                    },
                    session=sesion,
                )
                await self._historial(
                    contexto,
                    str(pago["orden_id"]),
                    "pago_anulado",
                    {"pago_id": pago_id, "motivo": motivo.strip()},
                    session=sesion,
                )
                pago.update(
                    estado="anulado",
                    motivo_anulacion=motivo.strip(),
                    anulado_en=_ahora(),
                )
        return _salida(pago)

    async def historial(
        self,
        contexto: ContextoTaller,
        orden_id: str,
        cursor: str | None,
        limite: int,
    ) -> dict[str, Any]:
        await self._orden(contexto, orden_id)
        filtro: dict[str, Any] = {
            "taller_id": contexto.taller_id,
            "orden_id": orden_id,
        }
        if cursor:
            taller_cursor, orden_cursor, id_cursor = self._decodificar_cursor(cursor)
            if taller_cursor != contexto.taller_id or orden_cursor != orden_id:
                raise ValueError("cursor inválido para el tenant")
            filtro["_id"] = {"$gt": _id_mongo(id_cursor)}
        documentos = [
            item
            async for item in self._db.historial_ordenes.find(filtro)
            .sort("_id", 1)
            .limit(limite + 1)
        ]
        hay_mas = len(documentos) > limite
        elementos = documentos[:limite]
        siguiente = None
        if hay_mas and elementos:
            siguiente = self._codificar_cursor(
                contexto.taller_id, orden_id, str(elementos[-1]["_id"])
            )
        return {
            "elementos": [_serializar(item) for item in elementos],
            "cursor_siguiente": siguiente,
        }

    async def _orden(
        self, contexto: ContextoTaller, orden_id: str, session: Any | None = None
    ) -> dict[str, Any]:
        documento = await self._db.ordenes.find_one(
            {"_id": orden_id, "taller_id": contexto.taller_id}, session=session
        )
        if documento is None:
            raise NoEncontrado("Orden no encontrada")
        return cast(dict[str, Any], documento)

    @staticmethod
    def _mutable(orden: Mapping[str, Any]) -> None:
        if orden["estado"] == "entregado":
            raise Conflicto("La Orden entregada está congelada")

    @staticmethod
    def _dinero_orden(orden: Mapping[str, Any], valor: str) -> Dinero:
        moneda = orden["moneda"]
        return Dinero.desde_texto(
            valor, str(moneda["codigo"]), int(moneda["decimales"])
        )

    async def _guardar_totales(
        self, contexto: ContextoTaller, orden: dict[str, Any], *, session: Any
    ) -> None:
        descuento = orden.get("descuento")
        subtotal, descuento_total, total = calcular_totales(
            [
                (_decimal(x["precio_unitario"]), int(x["cantidad"]))
                for x in orden["servicios"]
            ],
            [
                (_decimal(x["precio_unitario"]), int(x["cantidad"]))
                for x in orden["repuestos"]
            ],
            descuento["tipo"] if descuento else None,
            _decimal(descuento["valor"]) if descuento else Decimal("0"),
            int(orden["moneda"]["decimales"]),
        )
        finanzas = await self._db.finanzas_ordenes.find_one(
            {"_id": orden["_id"], "taller_id": contexto.taller_id}, session=session
        )
        pagado = _decimal(finanzas["pagado"] if finanzas else 0)
        if total < pagado:
            raise Conflicto("El total no puede quedar por debajo de lo pagado")
        await self._db.ordenes.update_one(
            {"_id": orden["_id"], "taller_id": contexto.taller_id},
            {
                "$set": {
                    "servicios": orden["servicios"],
                    "repuestos": orden["repuestos"],
                    "descuento": orden.get("descuento"),
                    "subtotal": Decimal128(subtotal),
                    "descuento_total": Decimal128(descuento_total),
                    "total": Decimal128(total),
                    "actualizado_en": _ahora(),
                }
            },
            session=session,
        )
        await self._db.finanzas_ordenes.update_one(
            {"_id": orden["_id"], "taller_id": contexto.taller_id},
            {
                "$set": {
                    "total": Decimal128(total),
                    "saldo": Decimal128(total - pagado),
                }
            },
            session=session,
        )
        orden.update(
            subtotal=Decimal128(subtotal),
            descuento_total=Decimal128(descuento_total),
            total=Decimal128(total),
        )

    async def _historial(
        self,
        contexto: ContextoTaller,
        orden_id: str,
        evento: str,
        datos: Mapping[str, Any],
        *,
        session: Any | None = None,
    ) -> None:
        await self._db.historial_ordenes.insert_one(
            {
                "_id": ObjectId(),
                "taller_id": contexto.taller_id,
                "orden_id": orden_id,
                "evento": evento,
                "datos": dict(datos),
                "creado_en": _ahora(),
                "usuario_id": contexto.usuario_id,
            },
            session=session,
        )

    @staticmethod
    def _codificar_cursor(taller_id: str, orden_id: str, item_id: str) -> str:
        contenido = json.dumps([taller_id, orden_id, item_id]).encode()
        return base64.urlsafe_b64encode(contenido).decode().rstrip("=")

    @staticmethod
    def _decodificar_cursor(cursor: str) -> tuple[str, str, str]:
        try:
            relleno = "=" * (-len(cursor) % 4)
            valores = json.loads(base64.urlsafe_b64decode(cursor + relleno))
            if not isinstance(valores, list) or len(valores) != 3:
                raise ValueError
            return str(valores[0]), str(valores[1]), str(valores[2])
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            raise ValueError("cursor inválido") from error
