# Convenciones de pruebas

## Propuestas

- Nombre en español o convención consistente elegida por el proyecto, describiendo comportamiento.
- Datos mínimos explícitos; factories/builders solo si reducen duplicación real.
- Fixtures aisladas por prueba y sin dependencias de orden.
- Reloj/IDs controlables cuando afecten resultados.
- Evitar esperas, red externa y aserciones sobre detalles irrelevantes.
- Marcar con requisito o regla los escenarios críticos.
- Las pruebas tenant siempre usan identificadores plausibles cruzados, no datasets triviales.

Framework, organización de carpetas, markers y umbrales están **Pendientes**.
