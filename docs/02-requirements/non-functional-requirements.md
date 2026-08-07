# Requisitos no funcionales

| ID | Estado | Requisito |
|---|---|---|
| RNF-001 | Aceptado | Toda operación con datos de Taller debe preservar aislamiento multi-tenant. |
| RNF-002 | Aceptado | La autorización no confiará únicamente en el identificador de Taller suministrado por el cliente. |
| RNF-003 | Aceptado | La solución seguirá un monolito modular con arquitectura hexagonal y separación Domain/Application/Infrastructure/Presentation. |
| RNF-004 | Aceptado | MongoDB se modelará por documentos, agregados y patrones de consulta, no como traducción mecánica de un modelo relacional. |
| RNF-005 | Aceptado | El código Python futuro cumplirá reglas del proyecto, Google Python Style Guide, PEP 8, PEP 257 y type hints, con la precedencia documentada. |
| RNF-006 | Aceptado | La implementación seguirá KISS, YAGNI, SOLID y Clean Code sin abstracciones especulativas. |
| RNF-007 | Aceptado | Los límites de módulo y reglas de dependencia deben ser verificables mediante revisión y pruebas arquitectónicas. |
| RNF-008 | Aceptado | Los secretos no se almacenarán en código, repositorio, imágenes ni logs. |
| RNF-009 | Propuesto | Las operaciones relevantes producirán señales observables sin exponer secretos ni datos sensibles. |
| RNF-010 | Aceptado | Todas las entradas HTTP, casos de uso y adaptadores de persistencia de fase 2 serán asíncronos; cualquier biblioteca bloqueante se aislará fuera del event loop. |
| RNF-011 | Aceptado | Las invariantes de stock y finanzas se preservarán bajo concurrencia mediante transacciones MongoDB reales. |
| RNF-012 | Aceptado | Los tokens públicos se firmarán con HMAC configurado como secreto, no se persistirán ni registrarán y podrán invalidarse por versión. |

## Atributos pendientes

Objetivos cuantitativos de disponibilidad, rendimiento, capacidad, recuperación,
retención, accesibilidad y compatibilidad siguen **Pendientes**. Fase 2 no añade
SLO ni umbrales.
