"""Pruebas del servicio de enlaces publicos firmados."""

import pytest

from app.modules.seguimiento.application.tokens import (
    ReferenciaSeguimiento,
    ServicioTokensSeguimiento,
    TokenSeguimientoInvalido,
)

SECRETO = b"secreto-de-pruebas-con-mas-de-32-bytes-seguros"


def test_token_permanente_autentica_orden_y_version() -> None:
    servicio = ServicioTokensSeguimiento(SECRETO)

    token = servicio.emitir(orden_id="orden-opaca-01", version=4)

    assert token.count(".") == 2
    assert servicio.verificar(token) == ReferenciaSeguimiento(
        orden_id="orden-opaca-01", version=4
    )
    assert servicio.emitir(orden_id="orden-opaca-01", version=4) == token


@pytest.mark.parametrize("segmento", [0, 1, 2])
def test_rechaza_alteraciones_en_cualquier_segmento(segmento: int) -> None:
    servicio = ServicioTokensSeguimiento(SECRETO)
    partes = servicio.emitir(orden_id="orden-01", version=1).split(".")
    partes[segmento] = partes[segmento][:-1] + (
        "A" if partes[segmento][-1] != "A" else "B"
    )

    with pytest.raises(TokenSeguimientoInvalido):
        servicio.verificar(".".join(partes))


def test_rechaza_firma_producida_con_otro_secreto() -> None:
    emisor = ServicioTokensSeguimiento(SECRETO)
    verificador = ServicioTokensSeguimiento(b"otro-secreto-seguro-de-al-menos-32-bytes")

    with pytest.raises(TokenSeguimientoInvalido):
        verificador.verificar(emisor.emitir(orden_id="orden-01", version=1))


@pytest.mark.parametrize(
    "token",
    ["", "st1", "st1.payload.firma.extra", "st2.e30.ZmlybWE", "st1.***.***"],
)
def test_rechaza_tokens_malformados_sin_filtrar_detalles(token: str) -> None:
    with pytest.raises(
        TokenSeguimientoInvalido, match="El token de seguimiento no es valido"
    ):
        ServicioTokensSeguimiento(SECRETO).verificar(token)


def test_version_permite_rotar_y_revocar_sin_registrar_tokens() -> None:
    servicio = ServicioTokensSeguimiento(SECRETO)
    anterior = servicio.verificar(servicio.emitir(orden_id="orden-01", version=2))
    actual = servicio.verificar(servicio.emitir(orden_id="orden-01", version=3))

    assert not servicio.version_vigente(anterior, version_actual=3)
    assert servicio.version_vigente(actual, version_actual=3)


@pytest.mark.parametrize(
    ("orden_id", "version"),
    [("", 1), (" orden-01", 1), ("orden-01", 0), ("orden-01", True)],
)
def test_no_emite_referencias_invalidas(orden_id: str, version: int) -> None:
    with pytest.raises(ValueError):
        ServicioTokensSeguimiento(SECRETO).emitir(orden_id=orden_id, version=version)


def test_exige_secreto_con_entropia_suficiente() -> None:
    with pytest.raises(ValueError, match="al menos 32 bytes"):
        ServicioTokensSeguimiento("muy-corto")
