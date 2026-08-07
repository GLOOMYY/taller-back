"""Entidades y reglas propias de Membresías."""

from dataclasses import dataclass
from enum import StrEnum


class RolMembresia(StrEnum):
    """Rol de un Usuario dentro de un Taller."""

    DUENO = "dueno"
    TECNICO = "tecnico"


@dataclass(frozen=True, slots=True)
class Membresia:
    """Vínculo de dominio entre un Usuario y un Taller."""

    id: str
    taller_id: str
    usuario_id: str
    rol: RolMembresia

    def __post_init__(self) -> None:
        """Rechaza identificadores vacíos en el límite del dominio."""
        for nombre, valor in (
            ("id", self.id),
            ("taller_id", self.taller_id),
            ("usuario_id", self.usuario_id),
        ):
            if not valor or not valor.strip():
                raise ValueError(f"{nombre} no puede estar vacío")
