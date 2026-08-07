# ADR-006: Persistencia MongoDB de fase 1

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Decisión

Se usa PyMongo Async con una base compartida y colecciones separadas por módulo:
`usuarios`, `talleres`, `membresias` y `clientes`. Los adaptadores convierten
`ObjectId` a strings opacos; ningún tipo MongoDB cruza hacia Domain/Application.

Las unicidades son `usuarios(issuer, sub)`, `usuarios(nombre_usuario)` y
`membresias(taller_id, usuario_id)`. Las consultas operativas e índices de
Clientes comienzan por `taller_id`. La creación de Taller y su Membresía de dueño
se ejecuta en una transacción MongoDB; el entorno local usa replica set.

## Consecuencias

Los repositorios reciben contexto tenant explícito y todos sus filtros operativos
incluyen `taller_id`. Readiness comprueba MongoDB. Las transacciones requieren
replica set local; topología, backups y operación de producción quedan fuera.
