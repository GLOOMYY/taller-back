# Pruebas de arquitectura

## Reglas a verificar

- Domain no importa Infrastructure, Presentation ni frameworks.
- Application no depende de adaptadores concretos.
- Presentation no accede a MongoDB.
- No hay imports de internals entre módulos ni ciclos.
- Los módulos no acceden a colecciones ajenas.
- Reportes no se convierte en propietario de datos fuente.

## Estado

La automatización es **Aceptada** como objetivo (RNF-007); herramienta y reglas ejecutables exactas están **Pendientes**. La revisión manual sigue siendo necesaria para acoplamiento semántico.
