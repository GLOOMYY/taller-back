"""Habilitación y proyección segura del seguimiento de Órdenes."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast

from bson import ObjectId
from bson.decimal128 import Decimal128
from bson.errors import InvalidId
from pymongo import ReturnDocument

from app.modules.seguimiento.application.dto import (
    EquipoPublico,
    EventoPublico,
    LineaPublica,
    OrdenPublica,
)
from app.modules.seguimiento.application.tokens import (
    ServicioTokensSeguimiento,
    TokenSeguimientoInvalido,
)
from app.shared.application import Conflicto, NoEncontrado
from app.shared.application.contexto import ContextoTaller


class ServicioSeguimientoPublico:
    """Gestiona versiones HMAC y construye el único DTO de lectura pública."""

    def __init__(self, base_datos: Any, tokens: ServicioTokensSeguimiento) -> None:
        self._db = base_datos
        self._tokens = tokens

    async def habilitar(self, contexto: ContextoTaller, orden_id: str) -> str:
        """Habilita un enlace permanente; llamadas repetidas conservan su versión."""
        orden = await self._db.ordenes.find_one(
            {"_id": orden_id, "taller_id": contexto.taller_id}
        )
        if orden is None:
            raise NoEncontrado("Orden no encontrada")
        if not orden.get("seguimiento_habilitado", False):
            orden = await self._db.ordenes.find_one_and_update(
                {"_id": orden_id, "taller_id": contexto.taller_id},
                {
                    "$set": {"seguimiento_habilitado": True},
                    "$inc": {"seguimiento_version": 1},
                },
                return_document=ReturnDocument.AFTER,
            )
            await self._evento(contexto, orden_id, "seguimiento_habilitado")
        return self._tokens.emitir(
            orden_id=orden_id, version=int(orden["seguimiento_version"])
        )

    async def rotar(self, contexto: ContextoTaller, orden_id: str) -> str:
        """Invalida la versión anterior y devuelve un enlace nuevo."""
        orden = await self._db.ordenes.find_one_and_update(
            {
                "_id": orden_id,
                "taller_id": contexto.taller_id,
                "seguimiento_habilitado": True,
            },
            {"$inc": {"seguimiento_version": 1}},
            return_document=ReturnDocument.AFTER,
        )
        if orden is None:
            raise Conflicto("El seguimiento debe estar habilitado para rotarlo")
        await self._evento(contexto, orden_id, "seguimiento_rotado")
        return self._tokens.emitir(
            orden_id=orden_id, version=int(orden["seguimiento_version"])
        )

    async def revocar(self, contexto: ContextoTaller, orden_id: str) -> None:
        """Invalida el enlace vigente sin guardar el token."""
        orden = await self._db.ordenes.find_one_and_update(
            {"_id": orden_id, "taller_id": contexto.taller_id},
            {
                "$set": {"seguimiento_habilitado": False},
                "$inc": {"seguimiento_version": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        if orden is None:
            raise NoEncontrado("Orden no encontrada")
        await self._evento(contexto, orden_id, "seguimiento_revocado")

    async def obtener_publica(self, token: str) -> OrdenPublica:
        """Verifica el token y devuelve solo campos aprobados para el público."""
        try:
            referencia = self._tokens.verificar(token)
        except TokenSeguimientoInvalido as error:
            raise NoEncontrado("Seguimiento no encontrado") from error
        orden = await self._db.ordenes.find_one({"_id": referencia.orden_id})
        if (
            orden is None
            or not orden.get("seguimiento_habilitado", False)
            or not self._tokens.version_vigente(
                referencia, version_actual=int(orden["seguimiento_version"])
            )
        ):
            raise NoEncontrado("Seguimiento no encontrado")
        return await self._proyectar(cast(dict[str, Any], orden))

    async def _proyectar(self, orden: dict[str, Any]) -> OrdenPublica:
        taller_id = str(orden["taller_id"])
        dispositivo = await self._db.dispositivos.find_one(
            {"_id": _id_mongo(str(orden["dispositivo_id"])), "taller_id": taller_id}
        )
        if dispositivo is None:
            raise NoEncontrado("Seguimiento no encontrado")
        modelo = await self._db.modelos_dispositivo.find_one(
            {"_id": _id_mongo(str(dispositivo["modelo_id"])), "taller_id": taller_id}
        )
        if modelo is None:
            raise NoEncontrado("Seguimiento no encontrado")
        tipo = await self._db.tipos_dispositivo.find_one(
            {"_id": _id_mongo(str(modelo["tipo_id"])), "taller_id": taller_id}
        )
        marca = await self._db.marcas_dispositivo.find_one(
            {"_id": _id_mongo(str(modelo["marca_id"])), "taller_id": taller_id}
        )
        taller = await self._db.talleres.find_one({"_id": taller_id})
        if tipo is None or marca is None or taller is None:
            raise NoEncontrado("Seguimiento no encontrado")
        eventos_documento = [
            item
            async for item in self._db.historial_ordenes.find(
                {
                    "taller_id": taller_id,
                    "orden_id": orden["_id"],
                    "evento": {
                        "$in": [
                            "creacion",
                            "campos",
                            "estado",
                            "garantia",
                            "servicio_agregado",
                            "servicio_retirado",
                            "repuesto_agregado",
                            "repuesto_retirado",
                        ]
                    },
                }
            ).sort("creado_en", 1)
        ]
        eventos = tuple(
            EventoPublico(
                fecha=item.get("creado_en", datetime.now(UTC)),
                descripcion=self._descripcion_evento(item),
            )
            for item in eventos_documento
        )
        entrega = next(
            (
                item.get("creado_en")
                for item in reversed(eventos_documento)
                if item.get("evento") == "estado"
                and item.get("datos", {}).get("nuevo") == "entregado"
            ),
            None,
        )
        moneda = orden["moneda"]
        total = orden["total"]
        return OrdenPublica(
            numero=str(orden["consecutivo"]),
            estado=str(orden["estado"]),
            taller_nombre=str(taller["nombre"]),
            equipo=EquipoPublico(
                tipo=str(tipo["nombre"]),
                marca=str(marca["nombre"]),
                modelo=str(modelo["nombre"]),
                identificador=dispositivo.get("identificador"),
            ),
            falla_reportada=str(orden["falla_reportada"]),
            diagnostico=orden.get("diagnostico"),
            trabajo_realizado=orden.get("trabajo_realizado"),
            accesorios_recibidos=orden.get("accesorios_recibidos"),
            servicios=tuple(
                LineaPublica(
                    nombre="Domicilio"
                    if item.get("domicilio")
                    else str(item["nombre"]),
                    cantidad=Decimal(str(item["cantidad"])),
                )
                for item in orden.get("servicios", [])
            ),
            repuestos=tuple(
                LineaPublica(
                    nombre=str(item["nombre"]),
                    cantidad=Decimal(str(item["cantidad"])),
                )
                for item in orden.get("repuestos", [])
            ),
            historial=eventos,
            moneda_codigo=str(moneda["codigo"]),
            moneda_decimales=int(moneda["decimales"]),
            total=(
                total.to_decimal()
                if isinstance(total, Decimal128)
                else Decimal(str(total))
            ),
            entregado_en=entrega,
        )

    async def _evento(
        self, contexto: ContextoTaller, orden_id: str, evento: str
    ) -> None:
        await self._db.historial_ordenes.insert_one(
            {
                "_id": ObjectId(),
                "taller_id": contexto.taller_id,
                "orden_id": orden_id,
                "evento": evento,
                "datos": {},
                "creado_en": datetime.now(UTC),
                "usuario_id": contexto.usuario_id,
            }
        )

    @staticmethod
    def _descripcion_evento(documento: dict[str, Any]) -> str:
        evento = str(documento.get("evento"))
        datos = documento.get("datos", {})
        if evento == "estado":
            return f"Estado actualizado a {datos.get('nuevo', '')}."
        if evento == "garantia":
            return "Orden reabierta por garantía."
        descripciones = {
            "creacion": "Orden creada.",
            "campos": "Información operativa actualizada.",
            "servicio_agregado": "Servicio agregado.",
            "servicio_retirado": "Servicio retirado.",
            "repuesto_agregado": "Repuesto agregado.",
            "repuesto_retirado": "Repuesto retirado.",
        }
        return descripciones.get(evento, "Orden actualizada.")


def _id_mongo(valor: str) -> str | ObjectId:
    try:
        return ObjectId(valor)
    except (InvalidId, TypeError):
        return valor
