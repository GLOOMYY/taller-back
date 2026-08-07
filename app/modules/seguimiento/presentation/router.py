"""Rutas de administración y lectura pública del seguimiento."""

from collections.abc import Callable
from dataclasses import asdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel

from app.modules.comprobantes.application.servicio import ServicioComprobantes
from app.modules.seguimiento.application.dto import OrdenPublica
from app.modules.seguimiento.application.servicio import ServicioSeguimientoPublico
from app.shared.application.contexto import ContextoTaller


class TokenSeguimientoSalida(BaseModel):
    token: str


class EquipoPublicoSalida(BaseModel):
    tipo: str
    marca: str
    modelo: str
    identificador: str | None = None


class LineaPublicaSalida(BaseModel):
    nombre: str
    cantidad: str


class EventoPublicoSalida(BaseModel):
    fecha: str
    descripcion: str


class OrdenPublicaSalida(BaseModel):
    numero: str
    estado: str
    taller_nombre: str
    equipo: EquipoPublicoSalida
    falla_reportada: str
    moneda_codigo: str
    total: str
    moneda_decimales: int
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    accesorios_recibidos: str | None = None
    servicios: list[LineaPublicaSalida]
    repuestos: list[LineaPublicaSalida]
    historial: list[EventoPublicoSalida]
    entregado_en: str | None = None


def crear_router_seguimiento(
    servicio: ServicioSeguimientoPublico,
    comprobantes: ServicioComprobantes,
    obtener_contexto: Callable[..., Any],
) -> tuple[APIRouter, APIRouter]:
    """Construye rutas autenticadas y públicas, claramente separadas."""
    privado = APIRouter(prefix="/talleres/{taller_id}", tags=["seguimiento"])
    publico = APIRouter(prefix="/publico/seguimiento", tags=["seguimiento-publico"])
    Contexto = Annotated[ContextoTaller, Depends(obtener_contexto)]

    @privado.post(
        "/ordenes/{orden_id}/seguimiento", response_model=TokenSeguimientoSalida
    )
    async def habilitar(orden_id: str, contexto: Contexto) -> dict[str, str]:
        return {"token": await servicio.habilitar(contexto, orden_id)}

    @privado.post(
        "/ordenes/{orden_id}/seguimiento/rotacion",
        response_model=TokenSeguimientoSalida,
    )
    async def rotar(orden_id: str, contexto: Contexto) -> dict[str, str]:
        return {"token": await servicio.rotar(contexto, orden_id)}

    @privado.delete(
        "/ordenes/{orden_id}/seguimiento",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def revocar(orden_id: str, contexto: Contexto) -> Response:
        await servicio.revocar(contexto, orden_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @publico.get("/{token}", response_model=OrdenPublicaSalida)
    async def consultar(token: str) -> dict[str, Any]:
        return _json_publico(await servicio.obtener_publica(token))

    @publico.get("/{token}/comprobante.pdf", response_class=Response)
    async def comprobante(token: str) -> Response:
        pdf = await comprobantes.generar_pdf(await servicio.obtener_publica(token))
        return Response(
            pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="comprobante.pdf"'},
        )

    return privado, publico


def _json_publico(orden: OrdenPublica) -> dict[str, Any]:
    """Serializa el DTO sin ampliar accidentalmente su contrato seguro."""
    salida = asdict(orden)
    salida["total"] = format(orden.total, f".{orden.moneda_decimales}f")
    salida["servicios"] = [
        {"nombre": item.nombre, "cantidad": format(item.cantidad, "f")}
        for item in orden.servicios
    ]
    salida["repuestos"] = [
        {"nombre": item.nombre, "cantidad": format(item.cantidad, "f")}
        for item in orden.repuestos
    ]
    salida["historial"] = [
        {"fecha": item.fecha.isoformat(), "descripcion": item.descripcion}
        for item in orden.historial
    ]
    if orden.entregado_en is not None:
        salida["entregado_en"] = orden.entregado_en.isoformat()
    return salida
