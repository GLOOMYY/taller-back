"""Rutas autenticadas de Órdenes, inventario y Pagos."""

from collections.abc import Callable
from datetime import date, timedelta
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.modules.operaciones.application.puertos import CasosUsoOperaciones
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
    estado_destino: Literal[
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


class DescuentoFijo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: Literal["fijo"]
    monto: str


class DescuentoPorcentaje(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: Literal["porcentaje"]
    porcentaje: str


Descuento = Annotated[DescuentoFijo | DescuentoPorcentaje, Field(discriminator="tipo")]


class LineaPago(BaseModel):
    metodo_pago_id: str
    monto: str


class EntradaPago(BaseModel):
    total: str
    lineas: list[LineaPago] = Field(min_length=1)


class PaginaSalida(BaseModel):
    items: list[dict[str, Any]]
    siguiente_cursor: str | None


class ProveedorSalida(BaseModel):
    id: str
    nombre: str
    contacto: str | None = None
    notas: str | None = None
    activo: bool


class PaginaProveedoresSalida(BaseModel):
    items: list[ProveedorSalida]
    siguiente_cursor: str | None


class RepuestoSalida(BaseModel):
    id: str
    codigo: str | None = None
    nombre: str
    descripcion: str | None = None
    precio_venta: str
    existencia: int
    activo: bool


class PaginaRepuestosSalida(BaseModel):
    items: list[RepuestoSalida]
    siguiente_cursor: str | None


class MovimientoStockSalida(BaseModel):
    id: str
    repuesto_id: str
    tipo: str
    cantidad: int
    creado_en: str
    costo_unitario: str | None = None
    proveedor_id: str | None = None
    nota: str | None = None
    motivo: str | None = None
    orden_id: str | None = None


class PaginaMovimientosSalida(BaseModel):
    items: list[MovimientoStockSalida]
    siguiente_cursor: str | None


class MetodoPagoSalida(BaseModel):
    id: str
    nombre: str
    activo: bool


class PaginaMetodosSalida(BaseModel):
    items: list[MetodoPagoSalida]
    siguiente_cursor: str | None


class LineaPagoSalida(BaseModel):
    metodo_pago_id: str
    metodo_nombre: str
    monto: str


class PagoSalida(BaseModel):
    id: str
    orden_id: str
    total: str
    lineas: list[LineaPagoSalida]
    estado: Literal["confirmado", "anulado"]
    creado_en: str
    motivo_anulacion: str | None = None
    anulado_en: str | None = None


class PaginaPagosSalida(BaseModel):
    items: list[PagoSalida]
    siguiente_cursor: str | None


class HistorialSalida(BaseModel):
    id: str
    orden_id: str
    evento: str
    datos: dict[str, Any]
    creado_en: str
    usuario_id: str


class PaginaHistorialSalida(BaseModel):
    items: list[HistorialSalida]
    siguiente_cursor: str | None


class MonedaSnapshotSalida(BaseModel):
    codigo: str
    nombre: str
    simbolo: str
    decimales: int


class OrdenSalida(BaseModel):
    id: str
    consecutivo: int
    dispositivo_id: str
    estado: str
    falla_reportada: str
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    accesorios_recibidos: str | None = None
    notas: str | None = None
    servicios: list[dict[str, Any]] = []
    repuestos: list[dict[str, Any]] = []
    descuento: dict[str, Any] | None = None
    subtotal: str
    descuento_total: str
    total: str
    pagado: str | None = None
    saldo: str | None = None
    moneda: MonedaSnapshotSalida
    seguimiento_habilitado: bool
    creado_en: str
    actualizado_en: str


class PaginaOrdenesSalida(BaseModel):
    items: list[OrdenSalida]
    siguiente_cursor: str | None


class ConteosEstadoSalida(BaseModel):
    abierta: int
    en_proceso: int
    espera_repuesto: int
    pendiente_recogida: int
    entregado: int


class TotalMonedaSalida(BaseModel):
    moneda_codigo: str
    moneda_simbolo: str
    moneda_decimales: int
    ordenado: str
    pagado: str
    pendiente: str


class OrdenesDiaSalida(BaseModel):
    fecha: date
    conteos_por_estado: ConteosEstadoSalida


class PagoMonedaDiaSalida(BaseModel):
    moneda_codigo: str
    total: str


class PagosDiaSalida(BaseModel):
    fecha: date
    totales_por_moneda: list[PagoMonedaDiaSalida]


class ResumenOperativoSalida(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    conteos_por_estado: ConteosEstadoSalida
    activas: int
    pendientes_recogida: int
    entregadas: int
    totales_por_moneda: list[TotalMonedaSalida]
    serie_ordenes: list[OrdenesDiaSalida]
    serie_pagos: list[PagosDiaSalida]


def crear_router(
    servicio: CasosUsoOperaciones, obtener_contexto: Callable[..., Any]
) -> APIRouter:
    """Construye las rutas con contexto tenant validado por Membresías."""
    router = APIRouter(prefix="/talleres/{taller_id}")
    Contexto = Annotated[ContextoTaller, Depends(obtener_contexto)]

    @router.post(
        "/proveedores",
        response_model=ProveedorSalida,
        status_code=201,
        tags=["proveedores"],
    )
    async def crear_proveedor(
        entrada: EntradaProveedor, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.crear_proveedor(contexto, entrada.model_dump())

    @router.get(
        "/proveedores", response_model=PaginaProveedoresSalida, tags=["proveedores"]
    )
    async def listar_proveedores(
        contexto: Contexto,
        activo: bool | None = None,
        texto: str | None = None,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.listar_proveedores(
            contexto, activo, texto, cursor, limite
        )

    @router.patch(
        "/proveedores/{proveedor_id}",
        response_model=ProveedorSalida,
        tags=["proveedores"],
    )
    async def actualizar_proveedor(
        proveedor_id: str, entrada: CambioProveedor, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_proveedor(
            contexto, proveedor_id, entrada.model_dump(exclude_unset=True)
        )

    @router.get(
        "/proveedores/{proveedor_id}",
        response_model=ProveedorSalida,
        tags=["proveedores"],
    )
    async def obtener_proveedor(
        proveedor_id: str, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.obtener_proveedor(contexto, proveedor_id)

    @router.delete("/proveedores/{proveedor_id}", status_code=204, tags=["proveedores"])
    async def desactivar_proveedor(proveedor_id: str, contexto: Contexto) -> Response:
        await servicio.actualizar_proveedor(contexto, proveedor_id, {"activo": False})
        return Response(status_code=204)

    @router.post(
        "/repuestos", response_model=RepuestoSalida, status_code=201, tags=["repuestos"]
    )
    async def crear_repuesto(
        entrada: EntradaRepuesto, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.crear_repuesto(contexto, entrada.model_dump())

    @router.get("/repuestos", response_model=PaginaRepuestosSalida, tags=["repuestos"])
    async def listar_repuestos(
        contexto: Contexto,
        activo: bool | None = None,
        texto: str | None = None,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.listar_repuestos(contexto, activo, texto, cursor, limite)

    @router.get(
        "/repuestos/{repuesto_id}", response_model=RepuestoSalida, tags=["repuestos"]
    )
    async def obtener_repuesto(repuesto_id: str, contexto: Contexto) -> dict[str, Any]:
        return await servicio.obtener_repuesto(contexto, repuesto_id)

    @router.patch(
        "/repuestos/{repuesto_id}", response_model=RepuestoSalida, tags=["repuestos"]
    )
    async def actualizar_repuesto(
        repuesto_id: str, entrada: CambioRepuesto, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_repuesto(
            contexto, repuesto_id, entrada.model_dump(exclude_unset=True)
        )

    @router.delete("/repuestos/{repuesto_id}", status_code=204, tags=["repuestos"])
    async def desactivar_repuesto(repuesto_id: str, contexto: Contexto) -> Response:
        await servicio.actualizar_repuesto(contexto, repuesto_id, {"activo": False})
        return Response(status_code=204)

    @router.post(
        "/repuestos/{repuesto_id}/entradas",
        status_code=201,
        tags=["repuestos"],
        response_model=MovimientoStockSalida,
    )
    async def entrada_stock(
        repuesto_id: str, entrada: EntradaStock, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.entrada_stock(contexto, repuesto_id, entrada.model_dump())

    @router.post(
        "/repuestos/{repuesto_id}/ajustes",
        status_code=201,
        tags=["repuestos"],
        response_model=MovimientoStockSalida,
    )
    async def ajuste_stock(
        repuesto_id: str, entrada: AjusteStock, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.ajustar_stock(contexto, repuesto_id, entrada.model_dump())

    @router.get(
        "/repuestos/{repuesto_id}/movimientos",
        response_model=PaginaMovimientosSalida,
        tags=["repuestos"],
    )
    async def movimientos(
        repuesto_id: str,
        contexto: Contexto,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.listar_movimientos(contexto, repuesto_id, cursor, limite)

    @router.post(
        "/metodos-pago",
        response_model=MetodoPagoSalida,
        status_code=201,
        tags=["pagos"],
    )
    async def crear_metodo(
        entrada: EntradaMetodo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.crear_metodo_pago(contexto, entrada.nombre)

    @router.get("/metodos-pago", response_model=PaginaMetodosSalida, tags=["pagos"])
    async def listar_metodos(
        contexto: Contexto,
        activo: bool | None = None,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.listar_metodos_pago(contexto, activo, cursor, limite)

    @router.get(
        "/metodos-pago/{metodo_id}", response_model=MetodoPagoSalida, tags=["pagos"]
    )
    async def obtener_metodo(metodo_id: str, contexto: Contexto) -> dict[str, Any]:
        return await servicio.obtener_metodo_pago(contexto, metodo_id)

    @router.patch(
        "/metodos-pago/{metodo_id}", response_model=MetodoPagoSalida, tags=["pagos"]
    )
    async def actualizar_metodo(
        metodo_id: str, entrada: CambioMetodo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_metodo_pago(
            contexto, metodo_id, entrada.model_dump(exclude_unset=True)
        )

    @router.delete("/metodos-pago/{metodo_id}", status_code=204, tags=["pagos"])
    async def desactivar_metodo(metodo_id: str, contexto: Contexto) -> Response:
        await servicio.actualizar_metodo_pago(contexto, metodo_id, {"activo": False})
        return Response(status_code=204)

    @router.post(
        "/ordenes", response_model=OrdenSalida, status_code=201, tags=["ordenes"]
    )
    async def crear_orden(entrada: EntradaOrden, contexto: Contexto) -> dict[str, Any]:
        return await servicio.crear_orden(contexto, entrada.model_dump())

    @router.get("/ordenes", response_model=PaginaOrdenesSalida, tags=["ordenes"])
    async def listar_ordenes(
        contexto: Contexto,
        estado: Literal[
            "abierta",
            "en_proceso",
            "espera_repuesto",
            "pendiente_recogida",
            "entregado",
        ]
        | None = None,
        grupo: Literal["abiertas", "pendientes_recogida", "entregadas"] | None = None,
        cliente_id: str | None = None,
        dispositivo_id: str | None = None,
        texto: str | None = None,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.listar_ordenes(
            contexto,
            dispositivo_id,
            estado,
            grupo,
            cliente_id,
            texto,
            cursor,
            limite,
        )

    @router.get("/ordenes/{orden_id}", response_model=OrdenSalida, tags=["ordenes"])
    async def obtener_orden(orden_id: str, contexto: Contexto) -> dict[str, Any]:
        return await servicio.obtener_orden(contexto, orden_id)

    @router.patch("/ordenes/{orden_id}", response_model=OrdenSalida, tags=["ordenes"])
    async def actualizar_orden(
        orden_id: str, entrada: CambioOrden, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.actualizar_orden(
            contexto, orden_id, entrada.model_dump(exclude_unset=True)
        )

    @router.post(
        "/ordenes/{orden_id}/transiciones", response_model=OrdenSalida, tags=["ordenes"]
    )
    async def transicionar(
        orden_id: str, entrada: Transicion, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.transicionar(contexto, orden_id, entrada.estado_destino)

    @router.post(
        "/ordenes/{orden_id}/reapertura-garantia",
        response_model=OrdenSalida,
        tags=["ordenes"],
    )
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

    @router.put(
        "/ordenes/{orden_id}/descuento", response_model=OrdenSalida, tags=["ordenes"]
    )
    async def descuento(
        orden_id: str, entrada: Descuento, contexto: Contexto
    ) -> dict[str, Any]:
        valor = (
            entrada.monto if isinstance(entrada, DescuentoFijo) else entrada.porcentaje
        )
        return await servicio.aplicar_descuento(contexto, orden_id, entrada.tipo, valor)

    @router.delete("/ordenes/{orden_id}/descuento", status_code=204, tags=["ordenes"])
    async def retirar_descuento(orden_id: str, contexto: Contexto) -> Response:
        await servicio.retirar_descuento(contexto, orden_id)
        return Response(status_code=204)

    @router.get(
        "/ordenes/{orden_id}/historial",
        response_model=PaginaHistorialSalida,
        tags=["ordenes"],
    )
    async def historial(
        orden_id: str,
        contexto: Contexto,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.historial(contexto, orden_id, cursor, limite)

    @router.post(
        "/ordenes/{orden_id}/pagos",
        response_model=PagoSalida,
        status_code=201,
        tags=["pagos"],
    )
    async def pago(
        orden_id: str, entrada: EntradaPago, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.registrar_pago(contexto, orden_id, entrada.model_dump())

    @router.get(
        "/ordenes/{orden_id}/pagos", response_model=PaginaPagosSalida, tags=["pagos"]
    )
    async def pagos(
        orden_id: str,
        contexto: Contexto,
        cursor: str | None = None,
        limite: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> dict[str, Any]:
        return await servicio.listar_pagos(contexto, orden_id, cursor, limite)

    @router.post(
        "/pagos/{pago_id}/anulacion", response_model=PagoSalida, tags=["pagos"]
    )
    async def anular(
        pago_id: str, entrada: Motivo, contexto: Contexto
    ) -> dict[str, Any]:
        return await servicio.anular_pago(contexto, pago_id, entrada.motivo)

    @router.get(
        "/resumen-operativo",
        response_model=ResumenOperativoSalida,
        tags=["talleres"],
    )
    async def resumen_operativo(
        contexto: Contexto,
        periodo_dias: Annotated[int, Query(ge=1, le=366)] = 30,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> dict[str, Any]:
        hasta = fecha_hasta or date.today()
        desde = fecha_desde or (hasta - timedelta(days=periodo_dias - 1))
        if desde > hasta:
            raise ValueError("fecha_desde no puede ser posterior a fecha_hasta")
        return await servicio.resumen_operativo(contexto, desde, hasta)

    return router
