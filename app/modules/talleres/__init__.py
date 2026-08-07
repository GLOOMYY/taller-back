"""Módulo público de Talleres."""

from app.modules.talleres.application.casos_uso import ServicioTalleres
from app.modules.talleres.domain.modelos import Taller

__all__ = ["ServicioTalleres", "Taller"]
