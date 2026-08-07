# Endpoints aceptados — fase 1

Base: `/api/v1`. Todos requieren Bearer JWT salvo health; las rutas con
`taller_id` construyen el contexto desde la identidad y la Membresía en servidor.

| Método | Ruta | Capacidad |
|---|---|---|
| POST, GET, PATCH | `/usuarios/me` | registrar, consultar o editar perfil propio |
| POST, GET | `/talleres` | crear o listar Talleres accesibles |
| GET, PATCH | `/talleres/{taller_id}` | consultar o editar Taller accesible |
| GET, POST | `/talleres/{taller_id}/miembros` | listar o añadir por `nombre_usuario` |
| PATCH, DELETE | `/talleres/{taller_id}/miembros/{usuario_id}` | cambiar rol o retirar miembro |
| GET, POST | `/talleres/{taller_id}/clientes` | listar o crear Clientes |
| GET, PATCH | `/talleres/{taller_id}/clientes/{cliente_id}` | consultar o editar Cliente |
| GET | `/health/live` | liveness sin dependencias |
| GET | `/health/ready` | readiness con MongoDB |

No existen endpoints de borrado para Taller o Cliente en fase 1.

Desde fase 2, `POST /talleres` exige además `pais_codigo` y `moneda_codigo`, y
`PATCH /talleres/{taller_id}` permite cambiarlos. La creación incluye
atómicamente el Método `Efectivo`; véase [phase-2.md](phase-2.md).
