# Convenciones de datos

## Aceptadas para fases 1 y 2

- Los nombres de dominio permanecen en español.
- Documentos, `ObjectId`, sesiones y excepciones PyMongo no atraviesan los
  puertos hacia Domain/Application.
- Los IDs son `str` opacos fuera de Infrastructure. El adaptador MongoDB los
  convierte desde/hacia `ObjectId`.
- Cada dato operativo incluye `taller_id`; todo acceso usa el contexto
  autorizado además del identificador del recurso.
- Campos opcionales ausentes representan falta de valor. En un PATCH, campo
  omitido significa conservar y `null` explícito significa eliminar el valor.
- El orden de listados paginados es determinista. Clientes usa `_id` ascendente,
  cursor opaco, límite 20 predeterminado y máximo 100.
- Los adaptadores aceptan solo filtros construidos internamente; no reciben
  operadores MongoDB desde la API.
- Los importes entran/salen de API como strings decimales, son `Decimal` en el
  núcleo y `Decimal128` en MongoDB. Se cuantizan con los decimales de la moneda
  snapshot usando `ROUND_HALF_UP`; no se usan `float`.
- Nombres sujetos a unicidad conservan valor legible y
  `nombre_normalizado`; índices y dominio aplican la misma normalización.
- Estado inactivo es desactivación lógica: nunca elimina referencias
  históricas y se excluye de nuevas selecciones.
- Eventos de historial y movimientos son append-only. Un cursor incluye Taller
  y posición y se valida antes de consultar.
- Los PATCH son parciales: omitido conserva, `null` elimina solo si el campo es
  opcional. No existe control optimista general; última escritura por campo
  prevalece fuera de invariantes transaccionales.

Fase 2 no requiere migración porque la base está vacía. Zona horaria, retención,
cifrado por campo y estrategia futura de migración de producción quedan
pendientes.
