"""Rutas autenticadas de Órdenes, inventario y Pagos."""

from collections.abc import Callable
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.modules.operaciones.application.servicio import ServicioOperaciones
from app.shared.application.contexto import ContextoTaller


class EntradaProveedor(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    contacto: str | None = None
    notas: str | None = None


class CambioProveedor(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    contacto: str | None = None
    notas: str | None = None
    activo: bool | None = None


class EntradaRepuesto(BaseModel):
    codigo: str | None = None
    nombre: str = Field(min_length=1, max_length=160)
    descripcion: str | None = None
    precio_venta: str


class CambioRepuesto(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    precio_venta: str | None = None
    activo: bool | None = None


class EntradaStock(BaseModel):
    cantidad: int = Field(gt=0)
    costo_unitario: str
    proveedor_id: str | None = None
    nota: str | None = None


class AjusteStock(BaseModel):
    delta: int
    motivo: str = Field(min_length=1)


class EntradaMetodo(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)


class CambioMetodo(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=80)
    activo: bool | None = None


class EntradaOrden(BaseModel):
    dispositivo_id: str
    falla_reportada: str = Field(min_length=1)
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    accesorios_recibidos: str | None = None
    notas: str | None = None


class CambioOrden(BaseModel):
    model_config = ConfigDict(extra="forbid")
    falla_reportada: str | None = Field(default=None, min_length=1)
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    accesorios_recibidos: str | None = None
    notas: str | None = None


class Transicion(BaseModel):
    estado: Literal[
        "abierta", "en_proceso", "espera_repuesto", "pendiente_recogida", "entregado"
    ]


class Motivo(BaseModel):
    motivo: str = Field(min_length=1)


class LineaServicio(BaseModel):
    tipo_servicio_id: str
    cantidad: int = Field(default=1, gt=0)
    precio_unitario: str | None = None
    domicilio: bool = False


class LineaRepuesto(BaseModel):
    repuesto_id: str
    cantidad: int = Field(default=1, gt=0)
    precio_unitario: str | None = None


class Descuento(BaseModel):
    tipo: Literal["fijo", "porcentaje"]
    valor: str


class LineaPago(BaseModel):
    metodo_pago_id: str
    monto: str


class EntradaPago(BaseModel):
    total: str
    lineas: list[LineaPago] = Field(min_length=1)


def crear_router(
    servicio: ServicioOperaciones, obtener_contexto: Callable[..., Any]
) -> APIRouter:
    """Construye las rutas con contexto tenant validado por Membresías."""
    router = APIRouter(prefix="/talleres/{taller_id}")
    Contexto = Annotated[ContextoTaller, Depends(obtener_contexto)]

    @router.post("/proveedores", status_code=201, tags=["proveedores"])
    async def crear_proveedor(
        entrada: EntradaProveedor, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.crear_proveedor(contexto, entrada.model_dump())

    @router.get("/proveedores", tags=["proveedores"])
    async def listar_proveedores(
        contexto: Contexto, activo: bool | None = None
    ) -> list[dict[str, Any]]:
        return await servicio.listar_proveedores(contexto, activo)

    @router.patch("/proveedores/{proveedor_id}", tags=["proveedores"])
    async def actualizar_proveedor(
        proveedor_id: str, entrada: CambioProveedor, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_proveedor(
            contexto, proveedor_id, entrada.model_dump(exclude_unset=True)
        )

    @router.get("/proveedores/{proveedor_id}", tags=["proveedores"])
    async def obtener_proveedor(
        proveedor_id: str, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.obtener_proveedor(contexto, proveedor_id)

    @router.post("/repuestos", status_code=201, tags=["repuestos"])
    async def crear_repuesto(
        entrada: EntradaRepuesto, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.crear_repuesto(contexto, entrada.model_dump())

    @router.get("/repuestos", tags=["repuestos"])
    async def listar_repuestos(
        contexto: Contexto, activo: bool | None = None
    ) -> list[dict[str, Any]]:
        return await servicio.listar_repuestos(contexto, activo)

    @router.get("/repuestos/{repuesto_id}", tags=["repuestos"])
    async def obtener_repuesto(repuesto_id: str, contexto: Contexto) -> dict[str, Any]:
        return await servicio.obtener_repuesto(contexto, repuesto_id)

    @router.patch("/repuestos/{repuesto_id}", tags=["repuestos"])
    async def actualizar_repuesto(
        repuesto_id: str, entrada: CambioRepuesto, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_repuesto(
            contexto, repuesto_id, entrada.model_dump(exclude_unset=True)
        )

    @router.post(
        "/repuestos/{repuesto_id}/entradas", status_code=201, tags=["repuestos"]
    )
    async def entrada_stock(
        repuesto_id: str, entrada: EntradaStock, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.entrada_stock(contexto, repuesto_id, entrada.model_dump())

    @router.post(
        "/repuestos/{repuesto_id}/ajustes", status_code=201, tags=["repuestos"]
    )
    async def ajuste_stock(
        repuesto_id: str, entrada: AjusteStock, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.ajustar_stock(contexto, repuesto_id, entrada.model_dump())

    @router.get("/repuestos/{repuesto_id}/movimientos", tags=["repuestos"])
    async def movimientos(repuesto_id: str, contexto: Contexto) -> list[dict[str, Any]]:
        return await servicio.listar_movimientos(contexto, repuesto_id)

    @router.post("/metodos-pago", status_code=201, tags=["pagos"])
    async def crear_metodo(
        entrada: EntradaMetodo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.crear_metodo_pago(contexto, entrada.nombre)

    @router.get("/metodos-pago", tags=["pagos"])
    async def listar_metodos(
        contexto: Contexto, activo: bool | None = None
    ) -> list[dict[str, Any]]:
        return await servicio.listar_metodos_pago(contexto, activo)

    @router.patch("/metodos-pago/{metodo_id}", tags=["pagos"])
    async def actualizar_metodo(
        metodo_id: str, entrada: CambioMetodo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_metodo_pago(
            contexto, metodo_id, entrada.model_dump(exclude_unset=True)
        )

    @router.post("/ordenes", status_code=201, tags=["ordenes"])
    async def crear_orden(entrada: EntradaOrden, contexto: Contexto) -> dict[str, Any]:
        return await servicio.crear_orden(contexto, entrada.model_dump())

    @router.get("/ordenes", tags=["ordenes"])
    async def listar_ordenes(
        contexto: Contexto, dispositivo_id: str | None = None
    ) -> list[dict[str, Any]]:
        return await servicio.listar_ordenes(contexto, dispositivo_id)

    @router.get("/ordenes/{orden_id}", tags=["ordenes"])
    async def obtener_orden(orden_id: str, contexto: Contexto) -> dict[str, Any]:
        return await servicio.obtener_orden(contexto, orden_id)

    @router.patch("/ordenes/{orden_id}", tags=["ordenes"])
    async def actualizar_orden(
        orden_id: str, entrada: CambioOrden, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_orden(
            contexto, orden_id, entrada.model_dump(exclude_unset=True)
        )

    @router.post("/ordenes/{orden_id}/transiciones", tags=["ordenes"])
    async def transicionar(
        orden_id: str, entrada: Transicion, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.transicionar(contexto, orden_id, entrada.estado)

    @router.post("/ordenes/{orden_id}/reapertura-garantia", tags=["ordenes"])
    async def garantia(
        orden_id: str, entrada: Motivo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.reabrir_garantia(contexto, orden_id, entrada.motivo)

    @router.post("/ordenes/{orden_id}/servicios", status_code=201, tags=["ordenes"])
    async def agregar_servicio(
        orden_id: str, entrada: LineaServicio, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.agregar_servicio(contexto, orden_id, entrada.model_dump())

    @router.delete(
        "/ordenes/{orden_id}/servicios/{linea_id}", status_code=204, tags=["ordenes"]
    )
    async def retirar_servicio(
        orden_id: str, linea_id: str, contexto: Contexto
    ) -> Response:
        await servicio.retirar_servicio(contexto, orden_id, linea_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/ordenes/{orden_id}/repuestos", status_code=201, tags=["ordenes"])
    async def agregar_repuesto(
        orden_id: str, entrada: LineaRepuesto, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.agregar_repuesto_orden(
            contexto, orden_id, entrada.model_dump()
        )

    @router.delete(
        "/ordenes/{orden_id}/repuestos/{linea_id}", status_code=204, tags=["ordenes"]
    )
    async def retirar_repuesto(
        orden_id: str, linea_id: str, contexto: Contexto
    ) -> Response:
        await servicio.retirar_repuesto_orden(contexto, orden_id, linea_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.put("/ordenes/{orden_id}/descuento", tags=["ordenes"])
    async def descuento(
        orden_id: str, entrada: Descuento, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.aplicar_descuento(
            contexto, orden_id, entrada.tipo, entrada.valor
        )

    @router.get("/ordenes/{orden_id}/historial", tags=["ordenes"])
    async def historial(
        orden_id: str,
        contexto: Contexto,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.historial(contexto, orden_id, cursor, limite)

    @router.post("/ordenes/{orden_id}/pagos", status_code=201, tags=["pagos"])
    async def pago(
        orden_id: str, entrada: EntradaPago, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.registrar_pago(contexto, orden_id, entrada.model_dump())

    @router.get("/ordenes/{orden_id}/pagos", tags=["pagos"])
    async def pagos(orden_id: str, contexto: Contexto) -> list[dict[str, Any]]:
        return await servicio.listar_pagos(contexto, orden_id)

    @router.post("/pagos/{pago_id}/anulacion", tags=["pagos"])
    async def anular(
        pago_id: str, entrada: Motivo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.anular_pago(contexto, pago_id, entrada.motivo)

    return router
