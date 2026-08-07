# Lista de revisión

## Alcance y dominio

- [ ] Cada cambio corresponde a un requisito/regla aceptado.
- [ ] No introduce campos, estados, roles, endpoints o módulos inventados.
- [ ] Nombres y responsabilidades coinciden con el glosario y el módulo.

## Arquitectura

- [ ] Domain permanece libre de frameworks/persistencia.
- [ ] Application usa puertos; adaptadores no filtran detalles.
- [ ] No hay ciclos, internals o colecciones ajenas.
- [ ] Service Layer/Repository/abstracciones tienen una necesidad real.

## Multi-tenant y seguridad

- [ ] Contexto de Taller se deriva y valida del lado confiable.
- [ ] Todas las operaciones y referencias aplican pertenencia tenant.
- [ ] Existen pruebas con al menos dos Talleres y acceso cruzado.
- [ ] Errores/logs no revelan datos, existencia o secretos.

## Calidad

- [ ] Cumple PEP 8, PEP 257, Google Style y type hints.
- [ ] Código simple, cohesivo, sin duplicación/abstracción especulativa.
- [ ] Errores y bordes están cubiertos.
- [ ] Pruebas apropiadas pasan y no dependen del orden/entorno.

## Entrega

- [ ] Documentación y ADR están actualizados si aplica.
- [ ] Dependencias y migraciones están justificadas.
- [ ] No hay secretos ni cambios fuera de alcance.
- [ ] Se reportan verificaciones ejecutadas y pendientes reales.
