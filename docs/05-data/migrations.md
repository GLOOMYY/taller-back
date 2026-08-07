# Migraciones de datos

## Estado de fases 1 y 2

La base parte de colecciones vacías y crea índices de forma idempotente con
`create_index`; no requiere transformar datos previos. No se incorpora una
herramienta de migración sin un cambio de esquema vigente.

## Convenciones aceptadas para cambios futuros

- Todo cambio persistente tiene versión, propósito, propietario de módulo y estrategia de reversión o compensación.
- Las migraciones son repetibles o idempotentes cuando sea viable, observables y probadas sobre copias no productivas.
- Cambios incompatibles usan despliegues expandir/migrar/contraer cuando corresponda.
- Procesos masivos preservan el scope tenant y permiten reanudación.
- Nunca se edita silenciosamente el significado histórico de un documento.

Backups, ventanas, rollbacks y aprobación de cambios destructivos se definirán antes de producción.
