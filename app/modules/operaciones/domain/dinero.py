"""Valor monetario decimal sin dependencias de persistencia o HTTP."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Literal


@dataclass(frozen=True, slots=True)
class Dinero:
    """Importe cuantizado según la precisión ISO de una moneda."""

    importe: Decimal
    moneda: str
    decimales: int

    @classmethod
    def desde_texto(cls, valor: str, moneda: str, decimales: int) -> "Dinero":
        """Convierte una representación API decimal y aplica ROUND_HALF_UP."""
        try:
            importe = Decimal(valor)
        except (InvalidOperation, ValueError) as error:
            raise ValueError("importe decimal inválido") from error
        if not importe.is_finite():
            raise ValueError("importe decimal inválido")
        cuantizador = Decimal(1).scaleb(-decimales)
        return cls(
            importe.quantize(cuantizador, rounding=ROUND_HALF_UP),
            moneda.upper(),
            decimales,
        )

    def texto(self) -> str:
        """Serializa sin notación exponencial y conserva la escala ISO."""
        return f"{self.importe:.{self.decimales}f}"


TipoDescuento = Literal["fijo", "porcentaje"]


def calcular_totales(
    servicios: list[tuple[Decimal, int]],
    repuestos: list[tuple[Decimal, int]],
    descuento_tipo: TipoDescuento | None,
    descuento_valor: Decimal,
    decimales: int,
) -> tuple[Decimal, Decimal, Decimal]:
    """Calcula subtotal, descuento efectivo y total cuantizados."""
    cuantizador = Decimal(1).scaleb(-decimales)
    subtotal = sum(
        (precio * cantidad for precio, cantidad in servicios + repuestos),
        Decimal("0"),
    )
    if descuento_tipo == "porcentaje":
        if descuento_valor < 0 or descuento_valor > 100:
            raise ValueError("el porcentaje debe estar entre 0 y 100")
        descuento = subtotal * descuento_valor / Decimal("100")
    elif descuento_tipo == "fijo":
        descuento = descuento_valor
    else:
        descuento = Decimal("0")
    subtotal = subtotal.quantize(cuantizador, rounding=ROUND_HALF_UP)
    descuento = descuento.quantize(cuantizador, rounding=ROUND_HALF_UP)
    total = (subtotal - descuento).quantize(cuantizador, rounding=ROUND_HALF_UP)
    if descuento < 0 or total < 0:
        raise ValueError("el descuento no puede superar el subtotal")
    return subtotal, descuento, total
