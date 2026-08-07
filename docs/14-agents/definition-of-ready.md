# Definition of Ready

Una tarea está lista para implementación solo si:

- Tiene módulo/fase y resultado observable.
- Enlaza requisitos `RF-*`, reglas `BR-*` y criterios `AC-*` aplicables.
- Distingue alcance incluido y excluido.
- Las reglas necesarias están Confirmadas/Aceptadas; no depende de candidatos como si fueran requisitos.
- Entradas, salidas e invariantes mínimas están definidas al nivel requerido.
- Se conoce el contexto de Taller, identidad/autorización y escenarios cross-tenant aplicables.
- Dependencias de módulos y contratos necesarios están identificados sin ciclos.
- Persistencia requerida tiene agregados/patrones de consulta suficientes para decidir diseño.
- Criterios de prueba son observables.
- No hay pregunta pendiente que cambie materialmente el comportamiento o contrato.

Si falla un punto material, la tarea permanece **Bloqueada para implementación**; se puede continuar con descubrimiento o documentación explícitamente autorizados.

## Evaluación de fase 2

**Gate aprobado:** la fase 2 definida en `13-roadmap/phase-2.md` cumple estos
puntos mediante BR-022 a BR-047, RF/AC de fase 2, módulos en `04-domain`,
colecciones/índices/transacciones en `05-data`, contrato `06-api/endpoints/phase-2.md`
y ADR-007 a ADR-009. Sus exclusiones están enumeradas y no queda pregunta
pendiente que cambie comportamiento o contrato. Esto no autoriza alcance de
fase 3 ni producción.
