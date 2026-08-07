# Tipos de servicio

**Fase:** 2 · **Estado:** Aceptado

Catálogo tenant-scoped de servicios ofrecidos. Cada Tipo contiene ID opaco,
nombre, `nombre_normalizado`, descripción opcional, precio predeterminado y
`activo`. El nombre normalizado es único dentro del Taller.

Permite crear, listar, consultar, editar y activar/desactivar; DELETE desactiva
lógicamente, nunca borra.
Los inactivos conservan historia, pero no pueden originar nuevas líneas. El
precio predeterminado es monetario y se cuantiza según la moneda vigente del
Taller; la línea de Orden puede ajustar el precio y conserva su propio snapshot.

El módulo expone selección/snapshot mediante contrato público y no consulta
Órdenes. Operaciones e índices son tenant-aware.

Trazabilidad: BR-030, BR-035; RF-TSE-001; AC-009/030.
