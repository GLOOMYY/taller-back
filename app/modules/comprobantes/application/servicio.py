"""Servicio asincrono de comprobantes."""

import asyncio

from app.modules.comprobantes.application.puertos import GeneradorComprobante
from app.modules.seguimiento.application.dto import OrdenPublica


class ComprobanteNoDisponible(ValueError):
    """La Orden aun no permite descargar un comprobante final."""

    def __init__(self) -> None:
        super().__init__("El comprobante solo esta disponible para Ordenes entregadas.")


class ServicioComprobantes:
    """Aisla del event loop la generacion sincrona del PDF."""

    def __init__(self, generador: GeneradorComprobante) -> None:
        self._generador = generador

    async def generar_pdf(self, orden: OrdenPublica) -> bytes:
        """Genera un PDF final sin bloquear otras solicitudes asincronas."""
        if orden.estado != "entregado":
            raise ComprobanteNoDisponible()
        return await asyncio.to_thread(self._generador.generar, orden)
