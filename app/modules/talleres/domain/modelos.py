"""Entidades del dominio de Talleres."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Taller:
    """Tenant de la plataforma."""

    id: str
    nombre: str
    pais_codigo: str = "CO"
    moneda_codigo: str = "COP"

    def __post_init__(self) -> None:
        nombre = self.nombre.strip()
        pais = self.pais_codigo.strip().upper()
        moneda = self.moneda_codigo.strip().upper()
        if not self.id or not nombre or not pais or not moneda:
            raise ValueError("id, nombre, país y moneda son obligatorios")
        object.__setattr__(self, "nombre", nombre)
        object.__setattr__(self, "pais_codigo", pais)
        object.__setattr__(self, "moneda_codigo", moneda)

    def renombrar(self, nombre: str) -> "Taller":
        """Devuelve el Taller con un nombre nuevo validado."""
        return Taller(
            id=self.id,
            nombre=nombre,
            pais_codigo=self.pais_codigo,
            moneda_codigo=self.moneda_codigo,
        )

    def actualizar_referencias(
        self, *, pais_codigo: str | None = None, moneda_codigo: str | None = None
    ) -> "Taller":
        """Cambia país y moneda sin afectar snapshots de Órdenes existentes."""
        return Taller(
            id=self.id,
            nombre=self.nombre,
            pais_codigo=pais_codigo or self.pais_codigo,
            moneda_codigo=moneda_codigo or self.moneda_codigo,
        )
