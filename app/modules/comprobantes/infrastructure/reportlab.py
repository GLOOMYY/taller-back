"""Generador de comprobantes PDF basado en ReportLab."""

from io import BytesIO

from reportlab.lib import colors  # type: ignore[import-untyped]
from reportlab.lib.enums import TA_CENTER, TA_RIGHT  # type: ignore[import-untyped]
from reportlab.lib.pagesizes import A4  # type: ignore[import-untyped]
from reportlab.lib.styles import (  # type: ignore[import-untyped]
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm  # type: ignore[import-untyped]
from reportlab.platypus import (  # type: ignore[import-untyped]
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.modules.seguimiento.application.dto import LineaPublica, OrdenPublica

_AZUL = colors.HexColor("#17324D")
_AZUL_CLARO = colors.HexColor("#EAF1F7")
_GRIS = colors.HexColor("#5F6B76")
_BORDE = colors.HexColor("#D8E0E7")


class GeneradorComprobanteReportLab:
    """Convierte exclusivamente una proyeccion publica en un PDF final."""

    def generar(self, orden: OrdenPublica) -> bytes:
        """Construye un comprobante A4 y devuelve sus bytes."""
        salida = BytesIO()
        documento = BaseDocTemplate(
            salida,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=f"Comprobante Orden {orden.numero}",
            author=orden.taller_nombre,
        )
        marco = Frame(
            documento.leftMargin,
            documento.bottomMargin,
            documento.width,
            documento.height,
            id="contenido",
        )
        documento.addPageTemplates(
            [PageTemplate(id="comprobante", frames=[marco], onPage=self._pie_pagina)]
        )

        estilos = self._estilos()
        historia: list[object] = [
            Paragraph(self._escapar(orden.taller_nombre), estilos["marca"]),
            Paragraph("COMPROBANTE DE SERVICIO", estilos["titulo"]),
            Spacer(1, 3 * mm),
            self._resumen(orden, estilos),
            Spacer(1, 4 * mm),
            self._seccion_equipo(orden, estilos),
            Spacer(1, 3 * mm),
            self._seccion_trabajo(orden, estilos),
        ]
        if orden.servicios:
            historia.extend(
                [
                    Spacer(1, 3 * mm),
                    self._tabla_lineas("Servicios", orden.servicios, estilos),
                ]
            )
        if orden.repuestos:
            historia.extend(
                [
                    Spacer(1, 3 * mm),
                    self._tabla_lineas("Repuestos", orden.repuestos, estilos),
                ]
            )
        if orden.historial:
            historia.extend([Spacer(1, 3 * mm), self._historial(orden, estilos)])
        historia.extend(
            [
                Spacer(1, 4 * mm),
                self._total(orden, estilos),
                Spacer(1, 3 * mm),
                Paragraph(
                    "Este comprobante resume la informacion publica de la Orden. "
                    "Gracias por confiar en nuestro servicio.",
                    estilos["nota"],
                ),
            ]
        )
        documento.build(historia)
        return salida.getvalue()

    @staticmethod
    def _estilos() -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "marca": ParagraphStyle(
                "Marca",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=_AZUL,
                spaceAfter=2,
            ),
            "titulo": ParagraphStyle(
                "Titulo",
                parent=base["Title"],
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=24,
                textColor=_AZUL,
                spaceAfter=0,
            ),
            "seccion": ParagraphStyle(
                "Seccion",
                parent=base["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=_AZUL,
                spaceAfter=3 * mm,
            ),
            "cuerpo": ParagraphStyle(
                "Cuerpo",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#27313A"),
            ),
            "etiqueta": ParagraphStyle(
                "Etiqueta",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=11,
                textColor=_GRIS,
            ),
            "valor": ParagraphStyle(
                "Valor",
                parent=base["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=_AZUL,
            ),
            "total": ParagraphStyle(
                "Total",
                parent=base["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                alignment=TA_RIGHT,
                textColor=_AZUL,
            ),
            "nota": ParagraphStyle(
                "Nota",
                parent=base["BodyText"],
                fontName="Helvetica",
                fontSize=8,
                leading=11,
                alignment=TA_CENTER,
                textColor=_GRIS,
            ),
        }

    def _resumen(
        self, orden: OrdenPublica, estilos: dict[str, ParagraphStyle]
    ) -> Table:
        entrega = (
            orden.entregado_en.astimezone().strftime("%d/%m/%Y %H:%M")
            if orden.entregado_en
            else "Entrega confirmada"
        )
        datos = [
            [
                Paragraph("ORDEN", estilos["etiqueta"]),
                Paragraph("ESTADO", estilos["etiqueta"]),
                Paragraph("FECHA DE ENTREGA", estilos["etiqueta"]),
            ],
            [
                Paragraph(self._escapar(orden.numero), estilos["valor"]),
                Paragraph("Entregado", estilos["valor"]),
                Paragraph(entrega, estilos["valor"]),
            ],
        ]
        tabla = Table(datos, colWidths=[52 * mm, 52 * mm, 52 * mm])
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), _AZUL_CLARO),
                    ("BOX", (0, 0), (-1, -1), 0.6, _BORDE),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, _BORDE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        return tabla

    def _seccion_equipo(
        self, orden: OrdenPublica, estilos: dict[str, ParagraphStyle]
    ) -> KeepTogether:
        equipo = orden.equipo
        descripcion = " / ".join(
            parte for parte in (equipo.tipo, equipo.marca, equipo.modelo) if parte
        )
        filas: list[list[Paragraph]] = [
            [
                Paragraph("Equipo", estilos["etiqueta"]),
                Paragraph(self._escapar(descripcion), estilos["cuerpo"]),
            ]
        ]
        if equipo.identificador:
            filas.append(
                [
                    Paragraph("Identificador", estilos["etiqueta"]),
                    Paragraph(self._escapar(equipo.identificador), estilos["cuerpo"]),
                ]
            )
        if orden.accesorios_recibidos:
            filas.append(
                [
                    Paragraph("Accesorios", estilos["etiqueta"]),
                    Paragraph(
                        self._escapar(orden.accesorios_recibidos), estilos["cuerpo"]
                    ),
                ]
            )
        tabla = Table(filas, colWidths=[35 * mm, 121 * mm], hAlign="LEFT")
        tabla.setStyle(self._estilo_detalle())
        return KeepTogether([Paragraph("Equipo recibido", estilos["seccion"]), tabla])

    def _seccion_trabajo(
        self, orden: OrdenPublica, estilos: dict[str, ParagraphStyle]
    ) -> KeepTogether:
        filas = [
            [
                Paragraph("Falla reportada", estilos["etiqueta"]),
                Paragraph(self._escapar(orden.falla_reportada), estilos["cuerpo"]),
            ],
            [
                Paragraph("Diagnostico", estilos["etiqueta"]),
                Paragraph(self._texto_opcional(orden.diagnostico), estilos["cuerpo"]),
            ],
            [
                Paragraph("Trabajo realizado", estilos["etiqueta"]),
                Paragraph(
                    self._texto_opcional(orden.trabajo_realizado), estilos["cuerpo"]
                ),
            ],
        ]
        tabla = Table(filas, colWidths=[35 * mm, 121 * mm], hAlign="LEFT")
        tabla.setStyle(self._estilo_detalle())
        return KeepTogether(
            [Paragraph("Detalle del servicio", estilos["seccion"]), tabla]
        )

    def _tabla_lineas(
        self,
        titulo: str,
        lineas: tuple[LineaPublica, ...],
        estilos: dict[str, ParagraphStyle],
    ) -> KeepTogether:
        datos: list[list[Paragraph]] = [
            [
                Paragraph("DESCRIPCION", estilos["etiqueta"]),
                Paragraph("CANTIDAD", estilos["etiqueta"]),
            ]
        ]
        datos.extend(
            [
                Paragraph(self._escapar(linea.nombre), estilos["cuerpo"]),
                Paragraph(self._cantidad(linea), estilos["cuerpo"]),
            ]
            for linea in lineas
        )
        tabla = Table(datos, colWidths=[129 * mm, 27 * mm], hAlign="LEFT")
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), _AZUL_CLARO),
                    ("BOX", (0, 0), (-1, -1), 0.5, _BORDE),
                    ("INNERGRID", (0, 0), (-1, -1), 0.35, _BORDE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return KeepTogether([Paragraph(titulo, estilos["seccion"]), tabla])

    def _historial(
        self, orden: OrdenPublica, estilos: dict[str, ParagraphStyle]
    ) -> KeepTogether:
        datos: list[list[Paragraph]] = []
        for evento in orden.historial:
            fecha = evento.fecha.astimezone().strftime("%d/%m/%Y %H:%M")
            datos.append(
                [
                    Paragraph(fecha, estilos["etiqueta"]),
                    Paragraph(self._escapar(evento.descripcion), estilos["cuerpo"]),
                ]
            )
        tabla = Table(datos, colWidths=[35 * mm, 121 * mm], hAlign="LEFT")
        tabla.setStyle(self._estilo_detalle())
        return KeepTogether(
            [Paragraph("Historial operativo", estilos["seccion"]), tabla]
        )

    def _total(self, orden: OrdenPublica, estilos: dict[str, ParagraphStyle]) -> Table:
        decimales = max(0, min(orden.moneda_decimales, 4))
        importe = f"{orden.total:,.{decimales}f}"
        total = f"TOTAL {self._escapar(orden.moneda_codigo)} {importe}"
        tabla = Table([[Paragraph(total, estilos["total"])]], colWidths=[156 * mm])
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), _AZUL_CLARO),
                    ("BOX", (0, 0), (-1, -1), 0.8, _AZUL),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            )
        )
        return tabla

    @staticmethod
    def _estilo_detalle() -> TableStyle:
        return TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, _BORDE),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, _BORDE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F6F8FA")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )

    @staticmethod
    def _cantidad(linea: LineaPublica) -> str:
        return format(linea.cantidad.normalize(), "f")

    def _texto_opcional(self, valor: str | None) -> str:
        return self._escapar(valor) if valor else "No registrado"

    @staticmethod
    def _escapar(valor: str) -> str:
        return (
            valor.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

    @staticmethod
    def _pie_pagina(canvas: object, documento: BaseDocTemplate) -> None:
        lienzo = canvas
        lienzo.saveState()  # type: ignore[attr-defined]
        lienzo.setStrokeColor(_BORDE)  # type: ignore[attr-defined]
        lienzo.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)  # type: ignore[attr-defined]
        lienzo.setFillColor(_GRIS)  # type: ignore[attr-defined]
        lienzo.setFont("Helvetica", 7.5)  # type: ignore[attr-defined]
        lienzo.drawString(18 * mm, 9 * mm, "Comprobante de servicio")  # type: ignore[attr-defined]
        lienzo.drawRightString(  # type: ignore[attr-defined]
            A4[0] - 18 * mm, 9 * mm, f"Pagina {documento.page}"
        )
        lienzo.restoreState()  # type: ignore[attr-defined]
