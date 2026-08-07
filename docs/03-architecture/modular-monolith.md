# Monolito modular

## Decisión aceptada

Los módulos se construyen y despliegan como una sola aplicación, con límites internos explícitos. La unidad de despliegue compartida no autoriza dependencias arbitrarias.

## Reglas

- Cada módulo es propietario de su modelo y persistencia lógica.
- Ningún módulo lee o modifica directamente colecciones pertenecientes a otro.
- La colaboración usa contratos de aplicación explícitos; eventos internos son **Candidatos**, no requisito.
- Los ciclos entre módulos están prohibidos.
- Código compartido solo contiene capacidades genuinamente transversales, no un dominio residual.
- Dividir en servicios separados requeriría un ADR futuro y evidencia; no se anticipa.

## Ventaja buscada

Mantener simplicidad operativa mientras se reduce acoplamiento para que fases y módulos evolucionen con seguridad.
