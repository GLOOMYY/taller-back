# Reportes

**Fase:** 4 · **Estado del módulo:** Confirmado para roadmap; contenido pendiente

## Propósito

Presentar información derivada de módulos propietarios sin convertirse en fuente de verdad (RF-REP-001, RF-REP-002).

## Responsabilidades

- Consumir datos mediante contratos aprobados.
- Mantener cualquier proyección derivada reconstruible desde fuentes canónicas, si se aprueba usar proyecciones.

## Qué NO pertenece

Modificar datos propietarios, definir reglas operativas ocultas o asumir métricas y formatos no aprobados.

## Entidades/conceptos conocidos

Reporte como lectura derivada. Reportes, métricas, filtros y proyecciones concretos están **Pendientes**.

## Reglas de negocio confirmadas

BR-007, BR-013 y BR-014.

## Casos de uso candidatos

**Candidatos:** generar, consultar, filtrar o exportar reportes. Ninguno está aceptado en detalle.

## Dependencias permitidas/prohibidas

Puede consumir contratos públicos de módulos fuente. No escribe en sus colecciones ni crea una segunda fuente canónica.

## Consideraciones multi-tenant

Toda consulta y resultado se limita al Taller autorizado. Agregaciones nunca deben mezclar tenants salvo requisito futuro explícito y controlado.

## Preguntas/decisiones pendientes

Audiencia, catálogo, métricas, periodicidad, consistencia, exportación, retención, rendimiento y estrategia de proyecciones.
