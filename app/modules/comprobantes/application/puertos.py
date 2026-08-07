"""Puerto del generador bloqueante de comprobantes."""

from typing import Protocol

from app.modules.seguimiento.application.dto import OrdenPublica


class GeneradorComprobante(Protocol):
    """Construye los bytes de un comprobante a partir del DTO publico."""

    def generar(self, orden: OrdenPublica) -> bytes:
        """Genera el documento mediante una biblioteca potencialmente bloqueante."""
        ...
