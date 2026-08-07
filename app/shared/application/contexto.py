"""Contextos confiables construidos después de autenticar y autorizar."""

from dataclasses import dataclass
from typing import Literal

RolMembresia = Literal["dueno", "tecnico"]


@dataclass(frozen=True, slots=True)
class ContextoIdentidad:
    """Identidad OIDC vinculada a un Usuario interno."""

    usuario_id: str
    issuer: str
    subject: str


@dataclass(frozen=True, slots=True)
class ContextoTaller:
    """Membresía validada para una operación tenant-scoped."""

    usuario_id: str
    taller_id: str
    rol: RolMembresia
