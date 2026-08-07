"""Esquemas HTTP del módulo Usuarios."""

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.modules.usuarios.domain.modelos import normalizar_nombre_usuario


class RegistrarUsuarioEntrada(BaseModel):
    """Datos mínimos para registrar el Usuario autenticado."""

    nombre: str
    nombre_usuario: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        """Rechaza nombres vacíos."""
        if not valor.strip():
            raise ValueError("nombre no puede estar vacío")
        return valor.strip()

    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre_usuario(cls, valor: str) -> str:
        """Normaliza el identificador público en el límite HTTP."""
        return normalizar_nombre_usuario(valor)


class ActualizarUsuarioEntrada(BaseModel):
    """Campos editables del perfil actual."""

    nombre: str | None = None
    nombre_usuario: str | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str | None) -> str | None:
        if valor is not None and not valor.strip():
            raise ValueError("nombre no puede estar vacío")
        return valor.strip() if valor is not None else None

    @field_validator("nombre_usuario")
    @classmethod
    def validar_nombre_usuario(cls, valor: str | None) -> str | None:
        return normalizar_nombre_usuario(valor) if valor is not None else None

    @model_validator(mode="after")
    def validar_cambio(self) -> "ActualizarUsuarioEntrada":
        if self.nombre is None and self.nombre_usuario is None:
            raise ValueError("se requiere al menos un campo")
        return self


class UsuarioSalida(BaseModel):
    """Representación pública de un Usuario."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    nombre_usuario: str
