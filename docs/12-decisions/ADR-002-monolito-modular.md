# ADR-002: Monolito modular

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

El roadmap contiene módulos relacionados, pero el proyecto está en planeación y no hay evidencia que justifique complejidad distribuida.

## Decisión

Construir una sola unidad de despliegue con módulos internos propietarios de su dominio y persistencia lógica. La colaboración ocurre por contratos explícitos y sin ciclos ni acceso a colecciones ajenas.

## Consecuencias

- Operación y desarrollo iniciales más simples.
- Transacciones y despliegue pueden ser locales a la aplicación cuando el diseño lo permita.
- La modularidad debe protegerse activamente pese al mismo proceso.
- Separar un módulo en servicio requerirá evidencia y otro ADR.

## Alternativa no adoptada

Microservicios desde el inicio: descartados por YAGNI y costo sin requisitos que los exijan.
