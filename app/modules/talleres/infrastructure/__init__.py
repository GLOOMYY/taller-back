"""Adaptadores de infraestructura de Talleres."""

from app.modules.talleres.infrastructure.mongo import (
    GeneradorUuid,
    RepositorioTalleresMongo,
)

__all__ = ["GeneradorUuid", "RepositorioTalleresMongo"]
