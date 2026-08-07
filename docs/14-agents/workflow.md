# Flujo de trabajo de agentes

## 1. Orientar

Identificar módulo, fase, requisitos `RF-*`, reglas `BR-*`, criterios `AC-*`, ADR y archivos afectados. Separar claramente hechos confirmados de preguntas.

## 2. Preparar

Validar Definition of Ready. Proponer el cambio mínimo, riesgos, dependencias y pruebas. Si falta una decisión que altera comportamiento, detener esa parte y solicitar definición.

## 3. Implementar

Trabajar dentro del módulo y capas correctas. Mantener contexto tenant explícito, errores seguros y contratos pequeños. No expandir alcance.

## 4. Verificar

Ejecutar formato, lint, tipos y pruebas disponibles; revisar límites, tenancy, secretos y documentación. Inspeccionar el diff completo y cambios no relacionados.

## 5. Entregar

Informar resultado, archivos, requisitos cubiertos, pruebas ejecutadas, decisiones/pendientes y riesgos. No afirmar éxito de una verificación no ejecutada.

## Cambios documentales

Una regla nueva necesita ID y aceptación. Una decisión arquitectónica significativa necesita ADR. Los estados Propuesto/Candidato/Pendiente no se cambian a Aceptado sin autoridad explícita.
