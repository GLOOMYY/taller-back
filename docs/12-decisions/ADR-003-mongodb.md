# ADR-003: MongoDB

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

La tecnología de persistencia fue definida como MongoDB. El modelo de dominio y los patrones de consulta aún deben descubrirse.

## Decisión

Usar MongoDB y modelar documentos desde agregados, consistencia, cardinalidad, crecimiento y patrones de lectura/escritura. No traducir mecánicamente tablas y relaciones.

## Consecuencias

- Embedding, referencias, colecciones e índices deben justificarse por caso.
- Repositorios aíslan detalles MongoDB del núcleo.
- Evolución de documentos exige estrategia de migración.
- Aislamiento tenant influye en claves, filtros e índices.

## Decisiones posteriores

ADR-006 fija para fase 1 PyMongo Async, colecciones, índices, IDs opacos y un
replica set local para transacciones. Backups, hosting y topología de producción
permanecen sin decidir.
