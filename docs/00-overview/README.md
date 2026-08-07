# Panorama general

## Qué es

Aplicación de gestión para talleres de electrónica, concebida como plataforma multi-tenant: cada **Taller** es un tenant. El producto organizará su construcción por fases y módulos de dominio.

## Estado

**Confirmado:** la fase 1 constituye la base multi-tenant y la fase 2 está lista
para implementar operación, inventario mínimo, pagos y seguimiento. Las
interfaces visuales y las fases 3–4 restantes siguen en planeación. ADR-005 a
ADR-009 definen los contratos técnicos aceptados.

## Tecnología y arquitectura objetivo

- Persistencia: MongoDB.
- Forma: monolito modular.
- Estructura interna: arquitectura hexagonal y separación `Domain`, `Application`, `Infrastructure`, `Presentation`.
- Patrones: puertos y adaptadores; Service Layer y Repository cuando correspondan.
- Principios: SOLID, KISS, YAGNI y Clean Code.
- Python futuro: PEP 8, PEP 257, Google Python Style Guide y type hints.

## Navegación

Leer en este orden: [visión](vision.md), [alcance](scope.md), [glosario](glossary.md) y [principios](principles.md). Continuar en el [índice raíz](../README.md).
