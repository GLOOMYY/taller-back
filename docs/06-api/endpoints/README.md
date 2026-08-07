# Endpoints

Contratos aceptados: [fase 1](phase-1.md) y [fase 2](phase-2.md).

## Estado

Los contratos de fases 1 y 2 están **Aceptados**. Las fases posteriores no
obtienen rutas por inferencia y requieren su propia Definition of Ready.

Antes de documentar un endpoint, debe existir un requisito confirmado y una decisión sobre:

- caso de uso y módulo propietario;
- actor/contexto de Taller y autorización;
- entrada, salida e invariantes;
- errores y semántica de idempotencia/concurrencia;
- paginación/filtros cuando aplique;
- información sensible y pruebas de aislamiento;
- compatibilidad y versión.

Los endpoints no se derivan automáticamente de entidades o colecciones.
