# ADR-001: Arquitectura hexagonal

- **Estado:** Aceptado
- **Fecha:** 2026-08-07

## Contexto

El sistema evolucionará por módulos y necesita mantener reglas de negocio independientes de MongoDB, API y otros detalles aún no elegidos.

## Decisión

Separar cada módulo en Domain, Application, Infrastructure y Presentation. Las interacciones tecnológicas se conectan por puertos y adaptadores. Service Layer y Repository se usan cuando expresan una necesidad real.

## Consecuencias

- Domain es comprobable sin infraestructura.
- Adaptadores pueden cambiar sin reescribir reglas.
- Se requieren disciplina de dependencias y pruebas arquitectónicas.
- Puede existir costo de traducción en límites, que debe mantenerse proporcional.

## No decidido

Framework, paquetes exactos, inyección y herramientas. Esta decisión no obliga a crear interfaces o capas vacías.
