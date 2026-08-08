"""Esquemas de entrada y salida para sesiones JWT locales."""

from pydantic import BaseModel, Field, field_validator

from app.modules.usuarios.domain.modelos import normalizar_nombre_usuario


class RegistroEntrada(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    nombre_usuario: str
    password: str = Field(min_length=8, max_length=200)

    @field_validator("nombre", "password")
    @classmethod
    def no_vacio(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El campo no puede estar vacío")
        return value.strip()

    @field_validator("nombre_usuario")
    @classmethod
    def normalizar_usuario(cls, value: str) -> str:
        return normalizar_nombre_usuario(value)


class LoginEntrada(BaseModel):
    nombre_usuario: str
    password: str = Field(min_length=1, max_length=200)

    @field_validator("nombre_usuario")
    @classmethod
    def normalizar_usuario(cls, value: str) -> str:
        return normalizar_nombre_usuario(value)


class SesionSalida(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: str
    nombre: str
    nombre_usuario: str
