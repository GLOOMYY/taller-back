# Actores

## Confirmados

### Usuario

Persona con identidad en la plataforma. Puede estar vinculada a múltiples
Talleres mediante Membresías con rol `dueno` o `tecnico` (BR-017). Ambos roles
ejecutan todas las capacidades operativas de fase 2; solo `dueno` administra
Membresías.

### Taller

Actor organizacional y tenant. Es propietario lógico de Clientes y datos operativos.

### Cliente

Persona o entidad atendida por un Taller. En fase 1 requiere nombre y admite
teléfono, correo y notas opcionales. No es una identidad global compartida.

## Candidatos, no confirmados como actores del sistema

Administrador, recepcionista y cajero siguen como
**Candidatos**. `dueno` y `tecnico` son roles de Membresía aceptados, no módulos.
Proveedor es un registro del Taller, no un actor autenticado.

## Sistemas externos

No hay sistemas externos ni integraciones confirmadas.
