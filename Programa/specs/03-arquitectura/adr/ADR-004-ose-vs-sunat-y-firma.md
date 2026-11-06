# ADR-004: OSE frente a SUNAT directo, y firma digital

- **Estado:** Aceptado (Fase 1). Opción elegida por el líder: OSE como canal principal.
- **Contexto:** El legado no se comunica con nadie. El Anexo 9-A exige firma digital en `ext:UBLExtensions/.../ds:Signature` (págs. 1, 19, 23, 28 y 31). Las condiciones normativas de cada canal (homologación, plazos, códigos de respuesta) **no están en el workspace** y quedan PENDIENTE.

## Opciones

| Criterio | OSE | SUNAT directo | Proveedor tipo Nubefact (JSON) |
|---|---|---|---|
| Quién valida | El OSE valida y emite el CDR | SUNAT | El proveedor genera el XML, firma y envía |
| Qué envía ABC | XML UBL firmado | XML UBL firmado | JSON propietario, con `<RUTA>` y `<TOKEN>` |
| Firma | La hace ABC | La hace ABC | La hace el proveedor |
| Disponibilidad y SLA | Contractual | La de SUNAT | Contractual |
| Acoplamiento | Bajo (estándar UBL) | Bajo (estándar UBL) | Alto (formato propietario, códigos propios, DISC-15) |

## Decisión

1. **Canal principal: OSE.** `ClienteSunatOsePort` tiene tres adaptadores: `OseAdapter` (principal), `SunatDirectoAdapter` (respaldo) y `NubefactAdapter` (referencia de mercado, opcional). El canal se elige por configuración del emisor (`emisor.canalEnvio`).
2. **El dominio siempre usa códigos SUNAT.** El `NubefactAdapter` contiene la **capa de mapeo**: catálogo 01 → `tipo_de_comprobante` (1–4), catálogo 51 → `sunat_transaction`, catálogo 07 → `tipo_de_igv`, catálogo 02 → `moneda` (1–4), y fechas `yyyy-mm-dd` → `DD-MM-AAAA`. Las tablas de equivalencia **no se copian** al contrato.
3. **Firma:**
   - Con OSE o SUNAT directo, firma ABC mediante `FirmadorXmlPort` **en el nodo Windows**, con el certificado en el almacén de Windows (CNG/DPAPI), que no es exportable.
   - Con el adaptador de proveedor, `GeneradorUblPort` y `FirmadorXmlPort` no se usan: el proveedor devuelve el XML y el CDR, que se guardan igual.
   - La clave privada **nunca** se serializa ni se escribe en logs o archivos (REG-093). Android no guarda el certificado de facturación (ADR-006).
4. **Credenciales** (OSE, SUNAT o proveedor): se guardan en el almacén seguro del SO y se configuran como `<RUTA>` y `<TOKEN>`. **Nunca** se guardan en los specs, el código ni el repositorio.

## Consecuencias

- (+) Cambiar de OSE no toca el dominio.
- (−) PENDIENTE: requisitos del certificado (REG-091), algoritmo de firma, códigos de respuesta del CDR (SUP-06) y plazos (REG-110).
