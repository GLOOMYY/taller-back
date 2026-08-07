"""Pruebas de configuración validada."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_configuracion_rechaza_uri_mongodb_vacia() -> None:
    with pytest.raises(ValidationError):
        Settings(mongodb_uri="")


def test_jwks_se_deriva_del_issuer() -> None:
    settings = Settings(oidc_issuer="https://tenant.auth0.com/")

    assert settings.jwks_url == ("https://tenant.auth0.com/.well-known/jwks.json")


def test_produccion_rechaza_placeholders_locales() -> None:
    with pytest.raises(ValidationError):
        Settings(entorno="production", _env_file=None)
