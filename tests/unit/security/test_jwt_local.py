from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.security.jwt_local import ServicioJwtLocal
from app.shared.application import NoAutenticado


@pytest.mark.asyncio
async def test_emite_y_verifica_jwt_local() -> None:
    servicio = ServicioJwtLocal(
        "s" * 40, emisor="taller-api-local", minutos_expiracion=60
    )
    identidad = await servicio.verificar(servicio.emitir("usuario-1"))
    assert identidad.issuer == "taller-api-local"
    assert identidad.subject == "usuario-1"


@pytest.mark.asyncio
async def test_rechaza_token_expirado() -> None:
    servicio = ServicioJwtLocal(
        "s" * 40, emisor="taller-api-local", minutos_expiracion=60
    )
    token = jwt.encode(
        {
            "sub": "usuario-1",
            "iss": "taller-api-local",
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(hours=1),
        },
        "s" * 40,
        algorithm="HS256",
    )
    with pytest.raises(NoAutenticado):
        await servicio.verificar(token)
