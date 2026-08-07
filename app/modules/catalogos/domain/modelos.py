"""Entidades tenant-scoped de los catálogos de operación."""

import re
import unicodedata
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Self


def normalizar_nombre(nombre: str) -> str:
    """Normaliza para unicidad sin alterar el nombre visible."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", nombre).strip()).casefold()


def _validar_base(taller_id: str, nombre: str) -> tuple[str, str]:
    limpio = nombre.strip()
    if not taller_id.strip() or not limpio:
        raise ValueError("El Taller y el nombre son obligatorios.")
    return limpio, normalizar_nombre(limpio)


@dataclass(frozen=True, slots=True)
class CambiosCatalogo:
    """PATCH común para nombre y activación lógica."""

    nombre_definido: bool = False
    nombre: str | None = None
    activo_definido: bool = False
    activo: bool | None = None


@dataclass(frozen=True, slots=True)
class CambiosTipoServicio(CambiosCatalogo):
    """PATCH del catálogo de servicios."""

    descripcion_definida: bool = False
    descripcion: str | None = None
    precio_definido: bool = False
    precio_predeterminado: Decimal | None = None


@dataclass(frozen=True, slots=True)
class CambiosModelo(CambiosCatalogo):
    """PATCH de Modelo, incluidas sus referencias técnicas."""

    tipo_definido: bool = False
    tipo_id: str | None = None
    marca_definida: bool = False
    marca_id: str | None = None


@dataclass(frozen=True, slots=True)
class EntradaCatalogo:
    """Base común de un valor tenant-scoped activable."""

    id: str | None
    taller_id: str
    nombre: str
    nombre_normalizado: str
    activo: bool = True

    @classmethod
    def nueva_simple(cls, taller_id: str, nombre: str) -> Self:
        limpio, normalizado = _validar_base(taller_id, nombre)
        return cls(None, taller_id, limpio, normalizado, True)

    def actualizar(self, cambios: CambiosCatalogo) -> "EntradaCatalogo":
        nombre = self.nombre
        normalizado = self.nombre_normalizado
        activo = self.activo
        if cambios.nombre_definido:
            if cambios.nombre is None:
                raise ValueError("El nombre no puede ser nulo.")
            nombre, normalizado = _validar_base(self.taller_id, cambios.nombre)
        if cambios.activo_definido:
            if cambios.activo is None:
                raise ValueError("El estado activo no puede ser nulo.")
            activo = cambios.activo
        return replace(
            self, nombre=nombre, nombre_normalizado=normalizado, activo=activo
        )


@dataclass(frozen=True, slots=True)
class TipoDispositivo(EntradaCatalogo):
    """Clasificación primaria de equipos."""


@dataclass(frozen=True, slots=True)
class MarcaDispositivo(EntradaCatalogo):
    """Marca ofrecida dentro de un Taller."""


@dataclass(frozen=True, slots=True)
class ModeloDispositivo(EntradaCatalogo):
    """Modelo asociado a un tipo y una marca del mismo Taller."""

    tipo_id: str = ""
    marca_id: str = ""

    @classmethod
    def nueva(
        cls, taller_id: str, nombre: str, tipo_id: str, marca_id: str
    ) -> "ModeloDispositivo":
        limpio, normalizado = _validar_base(taller_id, nombre)
        if not tipo_id.strip() or not marca_id.strip():
            raise ValueError("El tipo y la marca son obligatorios.")
        return cls(None, taller_id, limpio, normalizado, True, tipo_id, marca_id)

    def actualizar_modelo(self, cambios: CambiosModelo) -> "ModeloDispositivo":
        base = EntradaCatalogo.actualizar(self, cambios)
        tipo_id = self.tipo_id
        marca_id = self.marca_id
        if cambios.tipo_definido:
            if cambios.tipo_id is None or not cambios.tipo_id.strip():
                raise ValueError("El tipo es obligatorio.")
            tipo_id = cambios.tipo_id
        if cambios.marca_definida:
            if cambios.marca_id is None or not cambios.marca_id.strip():
                raise ValueError("La marca es obligatoria.")
            marca_id = cambios.marca_id
        return replace(
            self,
            nombre=base.nombre,
            nombre_normalizado=base.nombre_normalizado,
            activo=base.activo,
            tipo_id=tipo_id,
            marca_id=marca_id,
        )


@dataclass(frozen=True, slots=True)
class TipoServicio(EntradaCatalogo):
    """Servicio ofrecido con precio predeterminado ajustable en la Orden."""

    descripcion: str | None = None
    precio_predeterminado: Decimal = Decimal("0")

    @classmethod
    def nueva(
        cls,
        taller_id: str,
        nombre: str,
        descripcion: str | None,
        precio_predeterminado: Decimal,
    ) -> "TipoServicio":
        limpio, normalizado = _validar_base(taller_id, nombre)
        if not precio_predeterminado.is_finite() or precio_predeterminado < 0:
            raise ValueError("El precio predeterminado debe ser no negativo.")
        return cls(
            None,
            taller_id,
            limpio,
            normalizado,
            True,
            _limpiar_opcional(descripcion),
            precio_predeterminado,
        )

    def actualizar_servicio(self, cambios: CambiosTipoServicio) -> "TipoServicio":
        base = EntradaCatalogo.actualizar(self, cambios)
        descripcion = self.descripcion
        precio = self.precio_predeterminado
        if cambios.descripcion_definida:
            descripcion = _limpiar_opcional(cambios.descripcion)
        if cambios.precio_definido:
            if cambios.precio_predeterminado is None:
                raise ValueError("El precio predeterminado no puede ser nulo.")
            precio = cambios.precio_predeterminado
            if not precio.is_finite() or precio < 0:
                raise ValueError("El precio predeterminado debe ser no negativo.")
        return replace(
            self,
            nombre=base.nombre,
            nombre_normalizado=base.nombre_normalizado,
            activo=base.activo,
            descripcion=descripcion,
            precio_predeterminado=precio,
        )


def _limpiar_opcional(valor: str | None) -> str | None:
    if valor is None:
        return None
    limpio = valor.strip()
    return limpio or None
