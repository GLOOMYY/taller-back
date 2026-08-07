# Inventario mínimo de Repuestos

**Fase:** 2 · **Estado:** Aceptado

## Repuesto

Contiene ID opaco, `taller_id`, código opcional único dentro del Taller, nombre,
descripción opcional, precio de venta, existencia entera y `activo`. Permite
crear/listar/consultar/editar/activar/desactivar; no se borra físicamente. Un
Repuesto inactivo conserva todas sus referencias históricas.

## Operaciones y movimientos

- Entrada: cantidad positiva, costo unitario monetario, Proveedor opcional y
  nota opcional.
- Ajuste: delta entero no cero y motivo obligatorio.
- Consumo: cantidad positiva al agregar una línea a Orden.
- Reversión: repone exactamente el consumo al retirar la línea antes de entrega.

Cada operación actualiza existencia y agrega un movimiento append-only con
tipo, cantidad/delta, referencias y datos snapshot necesarios. Nunca permite
existencia negativa. Stock, movimiento, línea de Orden e historial se confirman
o revierten juntos mediante una unidad transaccional pública.

Entradas, ajustes y movimientos se consultan/listan tenant-aware. Inventario
valida Proveedor y Orden mediante contratos; no lee colecciones ajenas.
Compras, lotes, bodegas, reservas, valoración, devoluciones y cuentas por pagar
quedan fuera.

Trazabilidad: BR-039 a BR-041; RF-INV-001/002; AC-032/033.
