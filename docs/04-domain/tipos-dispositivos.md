# Catálogo técnico de dispositivos

**Fase:** 2 · **Estado:** Aceptado

## Modelo tenant-scoped

El catálogo se compone de Tipo de dispositivo, Marca de dispositivo y Modelo
de dispositivo. Cada elemento contiene ID opaco, `taller_id`, nombre,
`nombre_normalizado` y `activo`. Modelo referencia `tipo_id` y `marca_id`.

Los nombres normalizados son únicos por Taller y clase de catálogo. Modelo es
único por `(taller_id, tipo_id, marca_id, nombre_normalizado)`. Tipo y Marca
referenciados deben pertenecer al mismo Taller. La normalización sigue la misma
función determinista en dominio e índices.

## Casos de uso e invariantes

Cada catálogo permite crear, listar, consultar, editar y activar/desactivar;
DELETE significa desactivar. No hay borrado físico. Un elemento inactivo permanece visible por consulta y
en snapshots/referencias históricas, pero no puede seleccionarse para crear o
cambiar una relación. No se fija un catálogo inicial.

El módulo expone contratos de selección y snapshots; no lee Dispositivos ni
Órdenes. Todas las operaciones e índices operativos comienzan por `taller_id`.

Trazabilidad: BR-026/027; RF-TDI-001/002; AC-008.
