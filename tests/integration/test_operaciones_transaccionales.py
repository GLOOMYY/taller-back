"""Integración de stock, cuenta financiera, Pagos y entrega."""

import asyncio
import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from app.modules.operaciones import ServicioOperaciones
from app.shared.application.contexto import ContextoTaller

pytestmark = pytest.mark.integration


def test_flujo_transaccional_stock_pago_entrega_y_garantia() -> None:
    async def escenario() -> None:
        uri = os.getenv(
            "MONGODB_TEST_URI",
            "mongodb://localhost:27017/?replicaSet=rs0&directConnection=true",
        )
        cliente = AsyncMongoClient(uri, serverSelectionTimeoutMS=500)
        try:
            try:
                await cliente.admin.command("ping")
            except PyMongoError as error:
                pytest.skip(f"MongoDB no disponible para integración: {error}")
            nombre_base = f"taller_operaciones_{uuid4().hex}"
            db = cliente[nombre_base]
            servicio = ServicioOperaciones(db, cliente)
            contexto = ContextoTaller("usuario-1", "taller-1", "dueno")
            dispositivo_id = ObjectId()
            tipo_servicio_id = ObjectId()
            try:
                await servicio.crear_indices()
                await db.talleres.insert_one(
                    {
                        "_id": contexto.taller_id,
                        "nombre": "Central",
                        "moneda_codigo": "COP",
                    }
                )
                await db.referencias_monedas.insert_one(
                    {
                        "codigo": "COP",
                        "nombre": "peso colombiano",
                        "simbolo": "$",
                        "decimales": 2,
                    }
                )
                await db.dispositivos.insert_one(
                    {
                        "_id": dispositivo_id,
                        "taller_id": contexto.taller_id,
                        "cliente_id": "cliente-1",
                        "modelo_id": "modelo-1",
                    }
                )
                await db.tipos_servicio.insert_one(
                    {
                        "_id": tipo_servicio_id,
                        "taller_id": contexto.taller_id,
                        "nombre": "Reparación",
                        "precio_predeterminado": "100.00",
                        "activo": True,
                    }
                )
                repuesto = await servicio.crear_repuesto(
                    contexto, {"nombre": "Conector", "precio_venta": "50.00"}
                )
                await servicio.entrada_stock(
                    contexto,
                    repuesto["id"],
                    {"cantidad": 2, "costo_unitario": "20.00"},
                )
                metodo = await servicio.crear_metodo_pago(contexto, "Efectivo")
                orden = await servicio.crear_orden(
                    contexto,
                    {
                        "dispositivo_id": str(dispositivo_id),
                        "falla_reportada": "No enciende",
                    },
                )
                await servicio.agregar_servicio(
                    contexto,
                    orden["id"],
                    {"tipo_servicio_id": str(tipo_servicio_id), "cantidad": 1},
                )
                await servicio.agregar_repuesto_orden(
                    contexto,
                    orden["id"],
                    {"repuesto_id": repuesto["id"], "cantidad": 1},
                )
                pago = await servicio.registrar_pago(
                    contexto,
                    orden["id"],
                    {
                        "total": "150.00",
                        "lineas": [{"metodo_pago_id": metodo["id"], "monto": "150.00"}],
                    },
                )
                await servicio.transicionar(contexto, orden["id"], "en_proceso")
                await servicio.transicionar(contexto, orden["id"], "pendiente_recogida")
                entregada = await servicio.transicionar(
                    contexto, orden["id"], "entregado"
                )

                assert entregada["estado"] == "entregado"
                assert (await servicio.obtener_orden(contexto, orden["id"]))[
                    "saldo"
                ] == "0.00"
                assert (await servicio.obtener_repuesto(contexto, repuesto["id"]))[
                    "existencia"
                ] == 1
                reabierta = await servicio.reabrir_garantia(
                    contexto, orden["id"], "Falla recurrente"
                )
                assert reabierta["estado"] == "en_proceso"
                anulado = await servicio.anular_pago(
                    contexto, pago["id"], "Corrección de caja"
                )
                assert anulado["estado"] == "anulado"
                hoy = datetime.now(UTC).date()
                resumen = await servicio.resumen_operativo(contexto, hoy, hoy)
                assert resumen["conteos_por_estado"]["entregado"] == 0
                assert resumen["conteos_por_estado"]["en_proceso"] == 1
                assert resumen["totales_por_moneda"] == [
                    {
                        "moneda_codigo": "COP",
                        "moneda_simbolo": "$",
                        "moneda_decimales": 2,
                        "ordenado": "150.00",
                        "pagado": "0.00",
                        "pendiente": "150.00",
                    }
                ]
            finally:
                await cliente.drop_database(nombre_base)
        finally:
            await cliente.close()

    asyncio.run(escenario())
