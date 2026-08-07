# ADR-008: Transacciones y concurrencia de fase 2

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

Fase 2 introduce invariantes que atraviesan documentos y módulos propietarios.
MongoDB ofrece atomicidad de documento, pero stock, historial y cuenta financiera
deben quedar consistentes aun con solicitudes concurrentes o fallos parciales.

## Decisión

Mantener PyMongo Async y replica set. Application define unidades de trabajo
públicas; Infrastructure compone repositorios/sesión sin exponer PyMongo ni
permitir acceso de un módulo a colecciones ajenas.

Se usan transacciones para:

1. Taller + Membresía dueño + Método `Efectivo`.
2. Crear Orden + cuenta financiera + historial; el consecutivo se reserva con
   `$inc` atómico por Taller dentro de la operación.
3. Agregar/retirar Repuesto + stock + movimiento + línea + historial.
4. Cambiar líneas/descuento/total frente a cuenta y Pagos existentes.
5. Pago/anulación + cuenta + historial.
6. Entrega o reapertura por garantía + cuenta/estado + historial.

Cada transacción vuelve a leer y validar la invariante dentro de sesión. La
cuenta financiera se actualiza como guardia serializada para impedir write skew
en Pagos/total/entrega. Operaciones de un solo documento sin invariante cruzada
usan atomicidad nativa.

Fuera de estas invariantes, PATCH es parcial, sin bloqueo ni control optimista
general: última escritura por campo prevalece.

## Alternativas descartadas

- Compensación eventual: permitiría stock, saldo o historial temporalmente
  falsos y no satisface aceptación.
- Bloqueo distribuido externo: añade infraestructura innecesaria.
- Un documento gigante por Taller/Orden con historia y Pagos embebidos: tiene
  crecimiento no acotado y perjudica paginación/contención.

## Consecuencias

- Integración requiere MongoDB real con replica set, concurrencia y rollback.
- Los casos de uso y repositorios son async; no se bloquea el event loop.
- Los reintentos de transacción no constituyen idempotencia HTTP general.
- Trazabilidad: BR-024, BR-031, BR-037, BR-041, BR-046; AC-025, AC-027,
  AC-031, AC-033 a AC-035 y AC-041.

