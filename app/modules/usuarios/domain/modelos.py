"""Entidades y valores del dominio de Usuarios."""

import re
from dataclasses import dataclass

PATRON_NOMBRE_USUARIO = re.compile(r"^[a-z0-9._]{3,30}$", re.ASCII)


class NombreUsuarioInvalido(ValueError):
    """Indica que un identificador público no cumple las reglas aceptadas."""


def normalizar_nombre_usuario(valor: str) -> str:
    """Normaliza y valida el identificador global de un Usuario.

    Se acepta un ``@`` inicial como representación de entrada, pero no se
    persiste porque no forma parte del identificador canónico.
    """
    normalizado = valor.strip().lower()
    if normalizado.startswith("@"):
        normalizado = normalizado[1:]
    if not PATRON_NOMBRE_USUARIO.fullmatch(normalizado):
        raise NombreUsuarioInvalido(
            "nombre_usuario debe tener entre 3 y 30 caracteres y usar solo "
            "letras ASCII minúsculas, números, punto o guion bajo"
        )
    return normalizado


@dataclass(frozen=True, slots=True)
class IdentidadOidc:
    """Identidad externa verificada, estable por emisor y sujeto."""

    issuer: str
    subject: str

    def __post_init__(self) -> None:
        if not self.issuer.strip() or not self.subject.strip():
            raise ValueError("issuer y subject son obligatorios")


@dataclass(frozen=True, slots=True)
class Usuario:
    """Identidad interna de una persona en la plataforma."""

    id: str
    identidad: IdentidadOidc
    nombre: str
    nombre_usuario: str

    def __post_init__(self) -> None:
        nombre = self.nombre.strip()
        if not self.id or not nombre:
            raise ValueError("id y nombre son obligatorios")
        object.__setattr__(self, "nombre", nombre)
        object.__setattr__(
            self,
            "nombre_usuario",
            normalizar_nombre_usuario(self.nombre_usuario),
        )

    def actualizar(
        self,
        *,
        nombre: str | None = None,
        nombre_usuario: str | None = None,
    ) -> "Usuario":
        """Devuelve el Usuario con los cambios solicitados validados."""
        return Usuario(
            id=self.id,
            identidad=self.identidad,
            nombre=self.nombre if nombre is None else nombre,
            nombre_usuario=(
                self.nombre_usuario if nombre_usuario is None else nombre_usuario
            ),
        )
