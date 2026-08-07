# Registros de decisiones arquitectónicas

## Estados

- **Aceptado:** vigente y obligatorio.
- **Propuesto:** en revisión.
- **Reemplazado:** conserva historia y enlaza su sucesor.
- **Rechazado:** evaluado y no adoptado.

## Índice

| ADR | Estado | Decisión |
|---|---|---|
| [ADR-001](ADR-001-arquitectura-hexagonal.md) | Aceptado | Arquitectura hexagonal |
| [ADR-002](ADR-002-monolito-modular.md) | Aceptado | Monolito modular |
| [ADR-003](ADR-003-mongodb.md) | Aceptado | MongoDB y modelado documental |
| [ADR-004](ADR-004-multitenancy-por-taller.md) | Aceptado | Multi-tenancy por Taller |
| [ADR-005](ADR-005-stack-fase-1.md) | Aceptado | Stack y contrato técnico de fase 1 |
| [ADR-006](ADR-006-persistencia-fase-1.md) | Aceptado | MongoDB, IDs, índices y atomicidad de fase 1 |
| [ADR-007](ADR-007-operacion-financiera-fase-2.md) | Aceptado | Dinero, Pagos y cuenta financiera por Orden |
| [ADR-008](ADR-008-transacciones-fase-2.md) | Aceptado | Unidades transaccionales y concurrencia de fase 2 |
| [ADR-009](ADR-009-seguimiento-publico-y-comprobantes.md) | Aceptado | Tokens HMAC, DTO público y PDF derivado |

Un ADR nuevo registra una decisión significativa, alternativas, consecuencias y alcance. No se edita una decisión histórica para ocultar cambios: se crea un ADR sucesor.
