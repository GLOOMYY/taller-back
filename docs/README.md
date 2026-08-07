# Documentación de la aplicación de talleres de electrónica

## Estado y autoridad

Esta carpeta es la fuente de verdad. Las fases 1 y 2 están autorizadas;
solo los elementos marcados **Confirmado** o **Aceptado** constituyen requisitos.
**Propuesto**, **Candidato** y **Pendiente** no autorizan implementación.

La fase 1 se rige por BR-015 a BR-021 y ADR-005/ADR-006. La fase 2 se rige
por BR-022 a BR-047, sus RF/AC y ADR-007 a ADR-009. Las fases 3 y 4 siguen
en planeación salvo los módulos de Proveedores e inventario mínimo de Repuestos,
adelantados explícitamente a fase 2.

## Orden de lectura para agentes

1. [`00-overview/README.md`](00-overview/README.md), alcance, glosario y principios.
2. [`01-business/business-rules.md`](01-business/business-rules.md) y requisitos aplicables.
3. [`03-architecture/architecture.md`](03-architecture/architecture.md), límites y reglas de dependencia.
4. El archivo del módulo en [`04-domain/`](04-domain/).
5. Estrategia de datos, seguridad y pruebas pertinentes.
6. ADR vigentes en [`12-decisions/`](12-decisions/README.md).
7. Instrucciones de ejecución en [`14-agents/AGENTS.md`](14-agents/AGENTS.md).

## Índice

| Área | Contenido |
|---|---|
| `00-overview` | visión, alcance, lenguaje y principios |
| `01-business` | contexto, actores, reglas y flujos |
| `02-requirements` | requisitos, restricciones y aceptación |
| `03-architecture` | arquitectura objetivo, límites y diagramas |
| `04-domain` | módulos confirmados por fase |
| `05-data` | decisiones de persistencia en MongoDB |
| `06-api` | convenciones y contratos aceptados por fase |
| `07-security` | autenticación, autorización y aislamiento tenant |
| `08-development` | estándares futuros de ingeniería |
| `09-testing` | estrategia y convenciones de pruebas |
| `10-deployment` | lineamientos sin fijar infraestructura |
| `11-observability` | señales operativas propuestas |
| `12-decisions` | registros de decisiones arquitectónicas |
| `13-roadmap` | fases funcionales confirmadas |
| `14-agents` | reglas de trabajo para agentes |

## Convenciones de estado

- **Aceptado/Confirmado:** decisión o requisito obligatorio.
- **Propuesto:** opción recomendada aún no aprobada como contrato.
- **Candidato:** posibilidad a evaluar, sin compromiso de construcción.
- **Pendiente:** decisión necesaria y todavía no tomada.

## Identificadores

- `BR-xxx`: regla de negocio canónica.
- `RF-<MOD>-xxx`: requisito funcional por módulo.
- `RNF-xxx`: requisito no funcional.
- `AC-xxx`: criterio de aceptación.

Cada identificador tiene una definición canónica en `01-business/business-rules.md` o `02-requirements/`; las demás apariciones son referencias.
