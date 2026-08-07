# Versionado

## Estado de fases 1 y 2

La versión mayor se expresa en la ruta `/api/v1`. Los cambios incompatibles
requieren una versión mayor nueva; las adiciones compatibles conservan `v1`.

## Propuesta

Versionar cambios incompatibles del contrato público y preferir evolución compatible para adiciones. Antes de publicar, definir ubicación de versión, política de deprecación, ventana de soporte y comunicación.

Versionar la API no sustituye versionar datos, eventos o migraciones. No crear una versión inicial puramente ceremonial antes de decidir el protocolo.
