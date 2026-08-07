# Paginación

## Contrato aceptado

Los listados de fase 1 usan cursor opaco y orden determinista por identificador.
El límite predeterminado es 20 y el máximo 100.

Un contrato futuro debe definir orden estable, límite por defecto/máximo, continuidad, filtros asociados y representación de siguiente página. Los tokens de cursor no deben permitir cambiar Taller ni evadir autorización.

La respuesta contiene `items` y `siguiente_cursor`; un cursor inválido produce
entrada inválida y nunca permite cambiar el Taller autorizado.

Fase 2 aplica el mismo límite 20/100 y orden determinista por ID a catálogos y
recursos. Historial y movimientos ordenan por su ID append-only. Todo cursor
operativo codifica Taller y, cuando aplica, Orden/Repuesto padre; su reutilización
en otro contexto produce entrada inválida sin revelar datos.
