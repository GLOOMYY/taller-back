"""Pruebas puras de traducción del adaptador MongoDB."""

import pytest
from bson import ObjectId

from app.modules.clientes.application.errores import CursorClientesInvalido
from app.modules.clientes.infrastructure.mongodb import RepositorioClientesMongo


def test_cursor_es_determinista_y_esta_vinculado_al_taller() -> None:
    """AC-022: un cursor no puede reutilizarse en otro Taller."""
    identificador = ObjectId("64b7abdecf2160b649ab6085")
    cursor = RepositorioClientesMongo._codificar_cursor(  # noqa: SLF001
        "taller-a", identificador
    )

    assert (
        RepositorioClientesMongo._decodificar_cursor(  # noqa: SLF001
            cursor, "taller-a"
        )
        == identificador
    )
    with pytest.raises(CursorClientesInvalido):
        RepositorioClientesMongo._decodificar_cursor(  # noqa: SLF001
            cursor, "taller-b"
        )


@pytest.mark.parametrize("cursor", ["no-es-base64!", "e30", ""])
def test_cursor_malformado_es_rechazado(cursor: str) -> None:
    """AC-022: cursores arbitrarios no llegan a una consulta MongoDB."""
    with pytest.raises(CursorClientesInvalido):
        RepositorioClientesMongo._decodificar_cursor(  # noqa: SLF001
            cursor, "taller-a"
        )
