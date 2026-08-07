# Reglas de dependencia

## Dentro de un módulo

```text
Presentation ──> Application ──> Domain
Infrastructure ──> Application/Domain (al implementar puertos)
```

- Domain no depende de Application, Infrastructure ni Presentation.
- Application no depende de adaptadores concretos.
- Presentation no accede directamente a Infrastructure.
- Infrastructure no introduce reglas de negocio.

## Entre módulos

- Solo se usan interfaces públicas de Application o contratos explícitos aprobados.
- Se prohíben imports de internals, acceso a colecciones ajenas y ciclos.
- Una dependencia nueva requiere justificar necesidad, dirección y efecto tenant.
- Un paquete común no puede convertirse en atajo para acoplar dominios.

## Cumplimiento

Ruff, mypy, pruebas AST de arquitectura y revisión humana verifican estas reglas
en fase 1.
