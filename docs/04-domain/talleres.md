# Talleres

**Fase:** 1–2 · **Estado del módulo:** Confirmado · **Contrato:** Aceptado

## Propósito

Representar cada Taller como tenant y raíz conceptual del aislamiento
(RF-TAL-001 y RF-TAL-002; BR-001).

## Modelo aceptado

`Taller` contiene un `id` interno opaco, `nombre`, `pais_codigo` y
`moneda_codigo` obligatorios. País y moneda se validan contra Referencias, no
tienen que corresponder y pueden cambiar siempre. Cada Orden conserva su
snapshot monetario, por lo que el cambio no altera historia (BR-022/023/025).

## Casos de uso aceptados

- Crear un Taller: `POST /api/v1/talleres`.
- Listar los Talleres accesibles del Usuario: `GET /api/v1/talleres`.
- Consultar un Taller autorizado: `GET /api/v1/talleres/{taller_id}`.
- Editar nombre, país o moneda: `PATCH /api/v1/talleres/{taller_id}`.

Los listados usan cursor determinista, límite predeterminado 20 y máximo 100.
El cursor público es opaco para el consumidor.

## Creación y propiedad

El Usuario creador se convierte en dueño y se crea el Método activo `Efectivo`
(BR-024). Las tres escrituras se ejecutan en una única transacción MongoDB. Application exige
un puerto `UnidadCreacionTaller`; la implementación se compone entre los
adaptadores propietarios sin que Talleres importe internals ni colecciones de
Membresías o Pagos. Un fallo en cualquiera revierte las tres (AC-017, AC-025).

## Autorización y aislamiento

Crear y listar requieren `ContextoIdentidad` verificado. Consultar y editar
requieren `ContextoTaller` derivado por Membresías en servidor; el `taller_id`
del path nunca es autorización suficiente (BR-014). Dueños y técnicos pueden
editar el Taller. Un recurso fuera del contexto accesible responde como no
encontrado para no revelar su existencia (AC-001, AC-023).

Talleres no administra Usuarios, Membresías o Clientes y no accede a sus
colecciones. Consume únicamente un directorio público de IDs de Talleres
accesibles para el listado y la unidad transaccional pública para el alta.

## Persistencia y consultas

Colección lógica `talleres`. La lectura por ID soporta consulta/edición y el
listado filtra por el conjunto de IDs autorizado, ordena por ID y aplica el
cursor. Los documentos MongoDB y sesiones no cruzan hacia Domain/Application.

## Aceptación y trazabilidad

- AC-017: creación atómica Taller–Membresía dueño.
- AC-025: país/moneda obligatorios, Método `Efectivo` atómico y snapshots
  históricos estables.
- AC-023: listado y acceso limitados a Membresías del Usuario, incluida prueba
  negativa entre dos Talleres.
- AC-001: contexto tenant validado antes de lectura o mutación.
- AC-013 y AC-014: límites de módulo y controles de calidad.

## Fuera de alcance

Eliminación, suspensión, configuración, límites comerciales, autoabandono y
transferencia de propiedad fuera de las operaciones de Membresías aceptadas.
