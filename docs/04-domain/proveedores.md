# Proveedores

**Fase:** 2 · **Estado:** Aceptado

Proveedor es un registro exclusivo del Taller con ID opaco, nombre, contacto y
notas opcionales y `activo`. Permite crear, listar, consultar, editar y
activar/desactivar. No se borra físicamente.

Inventario puede validar y guardar la referencia opcional de un Proveedor en
una entrada mediante contrato público. Proveedores no posee entradas, no lee
Inventario y no representa Compras, cuentas por pagar o términos comerciales.
Toda operación y referencia está limitada al Taller autorizado.

Trazabilidad: BR-038; RF-PRO-001; AC-011/032.

