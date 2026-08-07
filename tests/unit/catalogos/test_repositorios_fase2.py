"""Pruebas puras de los adaptadores MongoDB de Fase 2."""

from decimal import Decimal

import pytest
from bson import Decimal128, ObjectId

from app.modules.catalogos.application.errores import CursorCatalogoInvalido
from app.modules.catalogos.domain import TipoServicio
from app.modules.catalogos.infrastructure.mongodb import RepositorioCatalogosMongo
from app.modules.dispositivos.application.errores import CursorDispositivosInvalido
from app.modules.dispositivos.infrastructure.mongodb import RepositorioDispositivosMongo


def test_cursores_quedan_ligados_al_taller_y_recurso() -> None:
    identificador = ObjectId("64b7abdecf2160b649ab6085")
    cursor_catalogo = RepositorioCatalogosMongo._codificar_cursor(  # noqa: SLF001
        "taller-a", "modelo", identificador
    )
    cursor_dispositivo = RepositorioDispositivosMongo._codificar_cursor(  # noqa: SLF001
        "taller-a", "cliente-a", identificador
    )

    assert (
        RepositorioCatalogosMongo._decodificar_cursor(  # noqa: SLF001
            cursor_catalogo, "taller-a", "modelo"
        )
        == identificador
    )
    assert (
        RepositorioDispositivosMongo._decodificar_cursor(  # noqa: SLF001
            cursor_dispositivo, "taller-a", "cliente-a"
        )
        == identificador
    )
    with pytest.raises(CursorCatalogoInvalido):
        RepositorioCatalogosMongo._decodificar_cursor(  # noqa: SLF001
            cursor_catalogo, "taller-b", "modelo"
        )
    with pytest.raises(CursorDispositivosInvalido):
        RepositorioDispositivosMongo._decodificar_cursor(  # noqa: SLF001
            cursor_dispositivo, "taller-a", "cliente-b"
        )


def test_precio_se_traduce_a_decimal128_sin_float() -> None:
    servicio = TipoServicio.nueva("taller-a", "Domicilio", None, Decimal("12345.67"))

    documento = RepositorioCatalogosMongo._documento(servicio)  # noqa: SLF001

    assert isinstance(documento["precio_predeterminado"], Decimal128)
    assert documento["precio_predeterminado"].to_decimal() == Decimal("12345.67")
