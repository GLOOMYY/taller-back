# Fase 2 — Operación, inventario, pagos y seguimiento

**Estado:** Aceptada y lista para implementación.

## Resultado observable

Un Taller configura país/moneda, catálogos y proveedores; registra equipos y
Órdenes con estado/historial, consume Repuestos, recibe Pagos divididos y entrega
solo con saldo cero. El cliente puede seguir la Orden con token revocable y
descargar comprobante PDF cuando esté entregada.

## Incluido

- Referencias ISO globales y ampliación de creación/edición de Taller.
- Tipo → Marca → Modelo, Dispositivos y Tipos de servicio tenant-scoped.
- Órdenes, consecutivos, estados, garantía, líneas snapshot, descuento e
  historial append-only.
- Proveedores, Repuestos, entradas, ajustes, consumos y movimientos.
- Métodos, Pagos sucesivos/divididos, anulaciones y cuenta financiera.
- Seguimiento JSON firmado y comprobante PDF desde el DTO público.

## Excluido

Compras, cuentas por pagar, lotes, devoluciones, impuestos, facturación fiscal,
reembolsos, conversión, frontend público y módulos independientes de garantía o
entrega.

## Trazabilidad y gate

BR-022 a BR-047; RF-REF/TAL/TDI/DIS/TSE/ODS/PRO/INV/PAG/SEG/CMP de fase 2;
AC-024 a AC-041; RNF-010 a RNF-012; ADR-007 a ADR-009. Entradas, invariantes,
persistencia, autorización, contratos cross-module y pruebas observables están
definidos; no queda pendiente que cambie el contrato de esta fase.

