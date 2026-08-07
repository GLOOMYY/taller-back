# Clientes

**Fase:** 1 · **Estado del módulo:** Confirmado

## Propósito

Gestionar Clientes exclusivos de cada Taller autorizado (RF-CLI-001,
RF-CLI-002; BR-005 a BR-007 y BR-014).

## Modelo aceptado

`Cliente` es la identidad local de una persona o entidad atendida por un
Taller. No es un Usuario de plataforma ni una identidad global compartida.

| Campo | Obligatorio | Semántica |
|---|---|---|
| `id` | sí al persistir | identificador opaco representado como `str` fuera del adaptador |
| `taller_id` | sí | pertenencia tenant, derivada del `ContextoTaller` autorizado |
| `nombre` | sí | nombre no vacío del Cliente |
| `telefono` | no | texto de contacto, sin normalización adicional aprobada |
| `correo` | no | texto de contacto, sin normalización adicional aprobada |
| `notas` | no | texto opcional |

No se ha aprobado deduplicación por nombre, teléfono o correo. La misma
persona puede registrarse de manera independiente en distintos Talleres
(BR-006).

## Casos de uso aceptados

- Crear un Cliente dentro del Taller autorizado.
- Listar Clientes del Taller autorizado con cursor determinista, límite 20
  predeterminado y máximo 100.
- Consultar un Cliente por identificador dentro del Taller autorizado.
- Editar `nombre`, `telefono`, `correo` o `notas`; los opcionales pueden
  limpiarse con `null` y `nombre` no puede quedar nulo o vacío.

No existe caso de uso ni endpoint de borrado en fase 1.

## Autorización y multi-tenancy

Dueños y técnicos pueden gestionar Clientes (AC-018). La capa de
Presentation recibe un `ContextoTaller` construido tras validar identidad y
Membresía; no construye autorización desde el parámetro de ruta.

Todos los puertos del repositorio exigen `ContextoTaller`. Cada filtro MongoDB
combina `taller_id` con el identificador o cursor aplicable. Consultar o editar
un identificador existente en otro Taller produce el mismo `404` que uno
inexistente (AC-021). El cursor incluye y valida el Taller para impedir su
reutilización entre tenants (AC-022).

## Límites

Clientes no posee Usuarios, Talleres, Membresías, Dispositivos, Órdenes ni
Pagos. Puede consumir el contrato público de contexto autorizado, pero no
consulta colecciones de otros módulos. `ObjectId`, documentos MongoDB y cursores
técnicos no atraviesan el adaptador de infraestructura.

## Trazabilidad

- RF-CLI-001: crear y listar.
- RF-CLI-002: consultar y editar, sin borrado.
- BR-005/BR-006: exclusividad e independencia por Taller.
- BR-007/BR-014, AC-001 y AC-021: scope autorizado y no divulgación cross-tenant.
- AC-018: dueños y técnicos gestionan Clientes.
- AC-022: contrato de paginación.
