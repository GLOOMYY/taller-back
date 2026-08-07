# Dispositivos

**Fase:** 2 · **Estado:** Aceptado

## Propósito y modelo

Representar un equipo persistente del Cliente dentro del Taller. Contiene ID
opaco, `taller_id`, `cliente_id` inmutable, `modelo_id`, identificador libre
opcional y notas opcionales (BR-028).

## Casos de uso

- Crear/listar bajo `/clientes/{cliente_id}/dispositivos`.
- Consultar/editar bajo `/dispositivos/{dispositivo_id}`.
- No borrar ni reasignar a otro Cliente.

El alta valida mediante contratos públicos que Cliente, Tipo, Marca y Modelo
sean seleccionables y pertenezcan al mismo Taller. Una edición puede cambiar
Modelo, identificador o notas, pero no Cliente. No se impone unicidad al
identificador libre.

## Colaboración y tenancy

Dispositivos posee su estado y consume validadores públicos de Clientes y del
catálogo técnico. Órdenes solo guarda su ID y puede crear varias Órdenes
activas simultáneas; Dispositivos no consulta la colección de Órdenes. Todas
las consultas combinan Taller e ID y los listados usan cursor tenant-bound.

Trazabilidad: BR-008 a BR-011, BR-028, BR-029; RF-DIS-001/002; AC-026.

