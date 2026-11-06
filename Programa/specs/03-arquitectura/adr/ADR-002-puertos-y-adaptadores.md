# ADR-002: Puertos y adaptadores

- **Estado:** Aceptado (Fase 1)
- **Contexto:** El mismo núcleo debe funcionar en Windows y Android, hablar con un OSE o con SUNAT directo (o con un proveedor como Nubefact), leer el legado y exportar los registros. Las piezas que cambian (proveedor, firma, base de datos, UI) no deben tocar las reglas tributarias.
- **Decisión:**
  - **Puertos de entrada = casos de uso** (`EmitirComprobanteUseCase`, …). Son el **contrato real** de la aplicación. La UI nativa los invoca en el mismo proceso, y HTTP (Ktor) es *otro* adaptador que los expone ([puertos.md](../../04-api/puertos.md) ↔ [openapi.yaml](../../04-api/openapi.yaml)).
  - **Puertos de salida:** los repositorios, `GeneradorUblPort` (clases del XSD, ADR-007), `ValidadorXsdPort` (antes de firmar, REG-094), `FirmadorXmlPort`, `ClienteSunatOsePort`, `ValidadorRucPort`, `ImportadorLegadoPort`, `GeneradorRegistrosPort`, `CatalogoRepositoryPort`, `ParametrosTributariosPort`, `ColaEnvioPort`, `IdempotenciaPort`, `EventosDominioPort` y `RelojPort`.
  - Los puertos usan **solo DTOs del dominio con códigos SUNAT**. El mapeo a los códigos de un proveedor (por ejemplo, Nubefact: `tipo_de_comprobante` 1–4, `sunat_transaction`, `tipo_de_igv`) vive **dentro de su adaptador** (REG-150, DISC-15).
  - El resultado de un caso de uso es `Resultado<T>` = éxito o `Problema` (RFC 9457, `problema.schema.yaml`). El adaptador HTTP traduce el resultado a códigos de estado; la UI, a mensajes.
- **Consecuencias:**
  - (+) Se puede probar el núcleo sin red ni base de datos (con adaptadores falsos).
  - (+) Cambiar de OSE es escribir un adaptador nuevo.
  - (+) Cada puerto de salida es candidato natural a API remota en la fase de microservicios.
  - (−) Hay más interfaces y más código de mapeo.
- **Relación con MVC:** el *Controller* de MVC **es** un adaptador de entrada. El *Model* es application más domain.
