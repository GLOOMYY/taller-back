# Multi-tenancy en datos

## Estrategia aceptada

Taller es el tenant (BR-001) y la fase 1 usa base y colecciones compartidas. Los
datos operativos, incluidos Clientes, almacenan una clave `taller_id` inequívoca.

El `taller_id` efectivo procede de un `ContextoTaller` construido del lado
confiable tras validar identidad y Membresía (BR-014). Presentation no entrega
un identificador de ruta como si fuera contexto autorizado.

## Defensa en profundidad

- Todos los métodos operativos de puertos y repositorios reciben
  `ContextoTaller`; no existen variantes globales sin scope.
- Crear verifica que la entidad y el contexto tengan el mismo Taller.
- Listar filtra por `taller_id` antes de ordenar/paginar.
- Consultar y editar combinan `_id` y `taller_id` en el mismo filtro.
- El cursor codifica el Taller y se rechaza si se reutiliza bajo otro contexto.
- Un documento existente en otro Taller se comporta como ausente.
- Los índices empiezan por la clave tenant cuando soportan colecciones
  operativas listables.
- Referencias ISO son la única lectura global de fase 2 y no contienen datos de
  Taller. Todo catálogo técnico, Proveedor, Repuesto, Orden, movimiento,
  Método, Pago, cuenta e historial es tenant-scoped.
- Un cursor de historial/movimientos/Pagos incluye `taller_id`; un token público
  no sustituye contexto tenant, sino que autoriza exclusivamente el DTO firmado.

## Prueba mínima

Cada repositorio operativo se prueba con dos Talleres y sus identificadores
cruzados. La prueba verifica que listar no mezcla registros, consultar no revela
existencia, editar no altera el documento ajeno y un cursor no cambia de Taller.
