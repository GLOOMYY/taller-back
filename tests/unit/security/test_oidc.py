"""Pruebas deterministas del adaptador OIDC, sin JWKS de red."""

from dataclasses import dataclass

import pytest

from app.security.oidc import IdentidadOidc, VerificadorOidcPyJwt
from app.security.servicio import ServicioIdentidad, UsuarioIdentidadReferencia
from app.shared.application import NoAutenticado


class JwtInvalido(Exception):
    """Equivalente de PyJWTError para el doble."""


@dataclass
class ClaveFirma:
    key: str = "clave-publica-de-prueba"


class ClienteJwksFalso:
    def get_signing_key_from_jwt(self, token: str) -> ClaveFirma:
        assert token
        return ClaveFirma()


class JwtFalso:
    PyJWTError = JwtInvalido

    def __init__(self, claims: dict[str, object] | None = None) -> None:
        self.claims = claims
        self.argumentos: dict[str, object] = {}

    def decode(self, token: str, key: str, **kwargs: object) -> dict[str, object]:
        self.argumentos = {"token": token, "key": key, **kwargs}
        if self.claims is None:
            raise JwtInvalido()
        return self.claims


def crear_verificador(jwt_falso: JwtFalso) -> VerificadorOidcPyJwt:
    return VerificadorOidcPyJwt(
        issuer="https://identidad.example/",
        audience="taller-api",
        jwks_url="https://identidad.example/.well-known/jwks.json",
        cliente_jwks=ClienteJwksFalso(),
        modulo_jwt=jwt_falso,
    )


@pytest.mark.asyncio
async def test_verifica_firma_issuer_audience_y_claims_obligatorios() -> None:
    jwt_falso = JwtFalso(
        {
            "iss": "https://identidad.example/",
            "sub": "oidc-subject",
            "aud": "taller-api",
            "exp": 2_000_000_000,
            "iat": 1_900_000_000,
        }
    )
    verificador = crear_verificador(jwt_falso)

    identidad = await verificador.verificar("token-firmado")

    assert identidad == IdentidadOidc(
        issuer="https://identidad.example/", subject="oidc-subject"
    )
    assert jwt_falso.argumentos["algorithms"] == ["RS256"]
    assert jwt_falso.argumentos["audience"] == "taller-api"
    assert jwt_falso.argumentos["issuer"] == "https://identidad.example/"
    assert jwt_falso.argumentos["options"] == {
        "require": ["exp", "iat", "iss", "sub", "aud"]
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("caso", ["expirado", "issuer", "audience", "firma"])
async def test_rechaza_token_que_pyjwt_considera_invalido(caso: str) -> None:
    del caso
    verificador = crear_verificador(JwtFalso(None))

    with pytest.raises(NoAutenticado):
        await verificador.verificar("token-invalido")


@pytest.mark.asyncio
async def test_rechaza_subject_vacio_aunque_decoder_lo_entregue() -> None:
    verificador = crear_verificador(
        JwtFalso({"iss": "https://identidad.example/", "sub": ""})
    )

    with pytest.raises(NoAutenticado):
        await verificador.verificar("token")


@pytest.mark.asyncio
async def test_issuer_con_slash_debe_coincidir_exactamente() -> None:
    verificador = crear_verificador(
        JwtFalso({"iss": "https://identidad.example", "sub": "subject"})
    )

    with pytest.raises(NoAutenticado):
        await verificador.verificar("token")


class VerificadorFalso:
    async def verificar(self, token: str) -> IdentidadOidc:
        assert token == "token"
        return IdentidadOidc("https://identidad.example", "subject")


@dataclass(frozen=True)
class UsuarioPrueba:
    id: str


class UsuariosFalso:
    def __init__(self, usuario: UsuarioIdentidadReferencia | None) -> None:
        self.usuario = usuario

    async def obtener_por_identidad(
        self, issuer: str, subject: str
    ) -> UsuarioIdentidadReferencia | None:
        assert (issuer, subject) == ("https://identidad.example", "subject")
        return self.usuario


@pytest.mark.asyncio
async def test_mapea_issuer_y_subject_a_usuario_interno() -> None:
    servicio = ServicioIdentidad(
        VerificadorFalso(), UsuariosFalso(UsuarioPrueba("usuario-1"))
    )

    contexto = await servicio.autenticar("token")

    assert contexto.usuario_id == "usuario-1"
    assert contexto.issuer == "https://identidad.example"
    assert contexto.subject == "subject"


@pytest.mark.asyncio
async def test_identidad_sin_usuario_interno_es_no_autenticada() -> None:
    servicio = ServicioIdentidad(VerificadorFalso(), UsuariosFalso(None))

    with pytest.raises(NoAutenticado):
        await servicio.autenticar("token")
