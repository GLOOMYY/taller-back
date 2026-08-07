"""Configuración validada desde variables de entorno."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de runtime sin valores secretos en el código."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TALLER_",
        extra="ignore",
    )

    entorno: Literal["local", "test", "production"] = "local"
    mongodb_uri: str = "mongodb://localhost:27017/?replicaSet=rs0"
    mongodb_database: str = "taller"
    oidc_issuer: AnyHttpUrl = AnyHttpUrl("https://example.auth0.com/")
    oidc_audience: str = "https://taller-api.local"
    oidc_jwks_url: AnyHttpUrl | None = None
    seguimiento_hmac_secreto: SecretStr = SecretStr(
        "solo-desarrollo-cambiar-antes-de-produccion"
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    @field_validator("mongodb_uri", "mongodb_database", "oidc_audience")
    @classmethod
    def no_vacio(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("no puede estar vacío")
        return value

    @property
    def jwks_url(self) -> str:
        if self.oidc_jwks_url is not None:
            return str(self.oidc_jwks_url)
        return f"{str(self.oidc_issuer).rstrip('/')}/.well-known/jwks.json"

    @model_validator(mode="after")
    def validar_produccion(self) -> "Settings":
        """Impide iniciar producción con placeholders o MongoDB local."""

        if self.entorno != "production":
            return self
        if "example.auth0.com" in str(self.oidc_issuer):
            raise ValueError("production requiere un issuer OIDC real")
        if "localhost" in self.mongodb_uri or "127.0.0.1" in self.mongodb_uri:
            raise ValueError("production requiere una URI MongoDB no local")
        if self.seguimiento_hmac_secreto.get_secret_value().startswith(
            "solo-desarrollo"
        ):
            raise ValueError("production requiere un secreto HMAC real")
        return self


@lru_cache
def get_settings() -> Settings:
    """Carga una única configuración validada por proceso."""

    return Settings()
