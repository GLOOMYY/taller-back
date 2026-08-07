"""Pruebas de importes y descuentos de fase 2."""

from decimal import Decimal

import pytest

from app.modules.operaciones.domain.dinero import Dinero, calcular_totales


def test_dinero_cuantiza_iso_con_half_up() -> None:
    dinero = Dinero.desde_texto("10.125", "cop", 2)

    assert dinero.importe == Decimal("10.13")
    assert dinero.texto() == "10.13"
    assert dinero.moneda == "COP"


def test_descuento_porcentaje_se_aplica_al_subtotal_completo() -> None:
    subtotal, descuento, total = calcular_totales(
        [(Decimal("100.00"), 2)],
        [(Decimal("50.00"), 1)],
        "porcentaje",
        Decimal("10"),
        2,
    )

    assert (subtotal, descuento, total) == (
        Decimal("250.00"),
        Decimal("25.00"),
        Decimal("225.00"),
    )


def test_descuento_no_puede_dejar_total_negativo() -> None:
    with pytest.raises(ValueError):
        calcular_totales([], [], "fijo", Decimal("1"), 2)
