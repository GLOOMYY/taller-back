"""Reglas puras de catálogos tenant-scoped."""

from decimal import Decimal

import pytest

from app.modules.catalogos.domain import (
    CambiosCatalogo,
    CambiosModelo,
    CambiosTipoServicio,
    ModeloDispositivo,
    TipoDispositivo,
    TipoServicio,
)


def test_nombre_normalizado_preserva_visible_y_unifica_variantes() -> None:
    primero = TipoDispositivo.nueva_simple("taller-a", "  Teléfono  Móvil ")
    segundo = TipoDispositivo.nueva_simple("taller-a", "teléfono móvil")

    assert primero.nombre == "Teléfono  Móvil"
    assert primero.nombre_normalizado == segundo.nombre_normalizado


def test_modelo_conserva_tipo_marca_al_editar() -> None:
    modelo = ModeloDispositivo.nueva("taller-a", "A55", "tipo-1", "marca-1")

    editado = modelo.actualizar(CambiosCatalogo(nombre_definido=True, nombre="A55 5G"))

    assert editado.tipo_id == "tipo-1"
    assert editado.marca_id == "marca-1"

    reclasificado = modelo.actualizar_modelo(
        CambiosModelo(tipo_definido=True, tipo_id="tipo-2")
    )
    assert reclasificado.tipo_id == "tipo-2"
    assert reclasificado.marca_id == "marca-1"


def test_tipo_servicio_valida_precio_y_desactivacion_logica() -> None:
    servicio = TipoServicio.nueva("taller-a", "Domicilio", None, Decimal("25000.00"))
    actualizado = servicio.actualizar_servicio(
        CambiosTipoServicio(
            activo_definido=True,
            activo=False,
            precio_definido=True,
            precio_predeterminado=Decimal("30000"),
        )
    )

    assert actualizado.activo is False
    assert actualizado.precio_predeterminado == Decimal("30000")
    with pytest.raises(ValueError):
        TipoServicio.nueva("taller-a", "Revisión", None, Decimal("-1"))
