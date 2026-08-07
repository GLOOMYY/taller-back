"""DTO publico de Orden, independiente de persistencia y presentacion HTTP."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class EquipoPublico:
    """Descripcion no sensible del equipo recibido por el Taller."""

    tipo: str
    marca: str
    modelo: str
    identificador: str | None = None


@dataclass(frozen=True, slots=True)
class LineaPublica:
    """Servicio o Repuesto sin informacion de precio unitario."""

    nombre: str
    cantidad: Decimal


@dataclass(frozen=True, slots=True)
class EventoPublico:
    """Evento operativo apto para ser mostrado a quien posee el enlace."""

    fecha: datetime
    descripcion: str


@dataclass(frozen=True, slots=True)
class OrdenPublica:
    """Proyeccion segura usada por seguimiento JSON y comprobantes.

    Por diseno no contiene metodos ni lineas de pago, proveedores, costos de
    compra o precios unitarios. El total es el unico importe publico.
    """

    numero: str
    estado: str
    taller_nombre: str
    equipo: EquipoPublico
    falla_reportada: str
    moneda_codigo: str
    total: Decimal
    moneda_decimales: int = 2
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    accesorios_recibidos: str | None = None
    servicios: tuple[LineaPublica, ...] = ()
    repuestos: tuple[LineaPublica, ...] = ()
    historial: tuple[EventoPublico, ...] = ()
    entregado_en: datetime | None = None
