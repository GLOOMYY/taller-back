# Pruebas unitarias

## Convenciones propuestas

- Probar comportamiento observable y reglas BR/RF, no implementación privada.
- Mantenerlas rápidas, deterministas y sin red, base de datos o reloj real.
- Usar dobles solo en puertos externos; no simular cada clase interna.
- Estructura Arrange–Act–Assert o equivalente clara.
- Un nombre describe condición y resultado esperado.
- Cubrir éxito, límites, errores y negaciones relevantes.

Las reglas tenant en casos de uso requieren pruebas unitarias aunque también se cubran en integración.
