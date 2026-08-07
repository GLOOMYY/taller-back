"""Contratos transversales de aplicación."""

from app.shared.application.contexto import ContextoIdentidad, ContextoTaller
from app.shared.application.errores import (
    Conflicto,
    ErrorAplicacion,
    NoAutenticado,
    NoEncontrado,
    Prohibido,
)

__all__ = [
    "Conflicto",
    "ContextoIdentidad",
    "ContextoTaller",
    "ErrorAplicacion",
    "NoAutenticado",
    "NoEncontrado",
    "Prohibido",
]
