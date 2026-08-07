# Arquitectura objetivo

## Decisión aceptada

El sistema será un **monolito modular con arquitectura hexagonal**. Cada módulo preservará responsabilidades de dominio y separará:

- **Domain:** modelo y reglas de negocio puras.
- **Application:** casos de uso, orquestación y puertos.
- **Infrastructure:** adaptadores técnicos, incluida persistencia MongoDB.
- **Presentation:** entrada/salida por API u otros canales futuros.

Service Layer y Repository se emplearán **cuando correspondan**, no como capas ceremoniales obligatorias para toda operación.

## Objetivos

- Independencia del dominio frente a frameworks y persistencia.
- Límites de módulo explícitos.
- Despliegue inicialmente unitario sin perder modularidad interna.
- Seguridad tenant aplicada en todas las rutas de acceso a datos.
- Evolución simple y comprobable.

## Decisiones por fase

ADR-005 y ADR-006 fijan FastAPI asíncrono, PyMongo Async, composición explícita,
API `/api/v1` y ejecución local para fase 1. Bus de eventos y despliegue de
producción siguen **Pendientes** y fuera de alcance.

ADR-007 a ADR-009 fijan para fase 2 representación monetaria, unidades de
trabajo MongoDB, cuenta financiera, seguimiento HMAC y PDF derivado fuera del
event loop. La composición cross-module ocurre mediante puertos públicos y no
autoriza acceso a colecciones ajenas.

Véanse [ADR-001](../12-decisions/ADR-001-arquitectura-hexagonal.md), [ADR-002](../12-decisions/ADR-002-monolito-modular.md) y los [diagramas](diagrams/README.md).
