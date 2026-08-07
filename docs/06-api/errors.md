# Errores de API

## Contrato aceptado

El contrato de error debería incluir un código estable legible por máquina, mensaje seguro, correlación y detalles de validación limitados. Presentation traduce errores conocidos sin filtrar stack traces, secretos o datos sensibles.

El cuerpo contiene `codigo`, `mensaje` y `correlacion_id`; los detalles de
validación de FastAPI se limitan a campos inválidos. Se usa `401` para token
ausente o inválido, `404` para Taller/recurso no accesible, `403` cuando un
técnico perteneciente intenta administrar Membresías, `409` para unicidad o
invariantes de estado y `422` para entradas inválidas.

## Seguridad tenant

La respuesta no revela si un recurso existe en otro Taller: se devuelve `404`.

En fase 2, `409` cubre transición inválida, Orden congelada, stock insuficiente,
total inferior a lo pagado, sobrepago, anulación inválida y entrega con saldo.
Un token público inválido, alterado, revocado o rotado responde `404` sin revelar
Orden o causa. El PDF de una Orden no entregada también responde `404`.
