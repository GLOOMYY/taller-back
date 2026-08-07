# Pruebas de repositorios

## Contrato aceptado

Cada adaptador Repository se prueba contra el mismo conjunto de comportamientos que exige su puerto:

- guardar y recuperar sin perder semántica;
- distinguir ausencia y conflicto según contrato;
- imponer scope tenant en toda operación;
- rechazar o no resolver referencias cruzadas;
- manejar concurrencia/atomicidad definida por ADR-008;
- traducir fallos MongoDB a errores acordados.

No diseñar métodos genéricos CRUD antes de los casos de uso. Las pruebas no deben depender del orden natural de MongoDB.
