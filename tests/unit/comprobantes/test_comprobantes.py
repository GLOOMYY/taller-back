"""Pruebas del servicio asincrono y el adaptador ReportLab."""

import asyncio
import threading
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO

import pytest

from app.modules.comprobantes.application.servicio import (
    ComprobanteNoDisponible,
    ServicioComprobantes,
)
from app.modules.comprobantes.infrastructure.reportlab import (
    GeneradorComprobanteReportLab,
)
from app.modules.seguimiento.application.dto import (
    EquipoPublico,
    EventoPublico,
    LineaPublica,
    OrdenPublica,
)


def orden_publica(*, estado: str = "entregado") -> OrdenPublica:
    return OrdenPublica(
        numero="OT-000042",
        estado=estado,
        taller_nombre="Taller Central",
        equipo=EquipoPublico(
            tipo="Celular",
            marca="Samsung",
            modelo="Galaxy S23",
            identificador="IMEI ...7890",
        ),
        falla_reportada="No enciende despues de una caida.",
        diagnostico="Conector de carga danado.",
        trabajo_realizado="Cambio de conector y pruebas funcionales.",
        accesorios_recibidos="Funda negra",
        servicios=(
            LineaPublica(nombre="Reparacion de conector", cantidad=Decimal("1")),
            LineaPublica(nombre="Domicilio", cantidad=Decimal("1")),
        ),
        repuestos=(LineaPublica(nombre="Conector USB-C", cantidad=Decimal("1")),),
        historial=(
            EventoPublico(
                fecha=datetime(2026, 8, 6, 9, 30, tzinfo=UTC),
                descripcion="Equipo recibido.",
            ),
            EventoPublico(
                fecha=datetime(2026, 8, 7, 15, 45, tzinfo=UTC),
                descripcion="Reparacion terminada y equipo entregado.",
            ),
        ),
        moneda_codigo="COP",
        moneda_decimales=2,
        total=Decimal("185000.00"),
        entregado_en=datetime(2026, 8, 7, 15, 45, tzinfo=UTC),
    )


class GeneradorEspia:
    def __init__(self) -> None:
        self.hilo: int | None = None
        self.orden: OrdenPublica | None = None

    def generar(self, orden: OrdenPublica) -> bytes:
        self.hilo = threading.get_ident()
        self.orden = orden
        return b"%PDF-prueba"


def test_servicio_ejecuta_generador_fuera_del_event_loop() -> None:
    async def escenario() -> None:
        hilo_event_loop = threading.get_ident()
        generador = GeneradorEspia()
        orden = orden_publica()

        resultado = await ServicioComprobantes(generador).generar_pdf(orden)

        assert resultado == b"%PDF-prueba"
        assert generador.orden is orden
        assert generador.hilo is not None
        assert generador.hilo != hilo_event_loop

    asyncio.run(escenario())


def test_comprobante_no_disponible_mientras_garantia_esta_reabierta() -> None:
    async def escenario() -> None:
        generador = GeneradorEspia()

        with pytest.raises(ComprobanteNoDisponible):
            await ServicioComprobantes(generador).generar_pdf(
                orden_publica(estado="en_proceso")
            )

        assert generador.orden is None

    asyncio.run(escenario())


def test_reportlab_genera_pdf_con_dto_publico_y_total_final() -> None:
    pypdf = pytest.importorskip("pypdf")
    pdf = GeneradorComprobanteReportLab().generar(orden_publica())

    assert pdf.startswith(b"%PDF-")
    documento = pypdf.PdfReader(BytesIO(pdf))
    texto = "\n".join(pagina.extract_text() or "" for pagina in documento.pages)
    assert len(documento.pages) == 1
    assert "OT-000042" in texto
    assert "Domicilio" in texto
    assert "TOTAL COP 185,000.00" in texto
    assert "metodo de pago" not in texto.lower()
    assert "precio unitario" not in texto.lower()
    assert "proveedor" not in texto.lower()
