# KISS, YAGNI y SOLID

## KISS

Elegir la menor estructura que preserve requisitos, seguridad y límites. “Simple” no significa omitir aislamiento o validación.

## YAGNI

No crear módulos candidatos, campos futuros de Membresía, motores genéricos de permisos, buses, microservicios o capas de abstracción sin caso confirmado.

## SOLID

- Responsabilidad única por razón de cambio.
- Extensión sin alterar reglas estables cuando haya necesidad real.
- Sustitución preservando contratos.
- Interfaces enfocadas en consumidores reales.
- Núcleo dependiente de abstracciones en fronteras externas.

SOLID no obliga a una interfaz por clase ni a patrones ceremoniales. Service Layer y Repository se usan cuando expresan una frontera o necesidad real.
