"""Esquemas HTTP del módulo Talleres."""

from pydantic import BaseModel, ConfigDict, field_validator


class TallerEntrada(BaseModel):
    """Datos obligatorios para crear un Taller."""

    nombre: str
    pais_codigo: str
    moneda_codigo: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("nombre no puede estar vacío")
        return valor.strip()


class TallerCambio(BaseModel):
    """Cambio parcial; país y moneda pueden modificarse siempre."""

    nombre: str | None = None
    pais_codigo: str | None = None
    moneda_codigo: str | None = None


class TallerSalida(BaseModel):
    """Representación pública de un Taller."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    nombre: str
    pais_codigo: str
    moneda_codigo: str
    rol_actual: str | None = None


class PaginaTalleresSalida(BaseModel):
    """Página de Talleres con cursor opaco de continuación."""

    items: list[TallerSalida]
    siguiente_cursor: str | None
