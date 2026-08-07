# Pruebas de integración

## Alcance aceptado

Verificar adaptadores MongoDB, configuración, serialización, índices, restricciones y traducción de errores contra una instancia real compatible, no un mock de comportamiento distinto.

## Casos obligatorios

- Aislamiento con dos Talleres.
- Lecturas, updates, deletes y agregaciones tenant-scoped.
- Referencias cross-tenant rechazadas.
- Persistencia y recuperación del agregado sin filtrar detalles técnicos.
- Migraciones repetibles/reanudables cuando existan.
- Índices únicos/tenant-aware y consecutivos bajo concurrencia.
- Decimal128 y cuantización de moneda.
- Rollback de stock, movimientos, historial, Pagos y cuenta financiera.
- Sobreconsumo/sobrepago concurrente y entrega/reapertura transaccional.

Se ejecutan contra el replica set de Docker Compose del proyecto. La limpieza
preserva independencia entre pruebas; estrategia de producción no se infiere.
