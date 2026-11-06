# 00 — Análisis del caso: ABC Software Corp

> **Fase 1, metodología SPEC-FIRST.** Este documento fija los requisitos, las restricciones, los supuestos, los riesgos y las preguntas abiertas. No contiene lógica de negocio.
> **Convención de fuentes:** cada afirmación normativa cita su fuente. Lo que no tiene fuente en el workspace se marca `SUPUESTO` o `PENDIENTE` y aparece en la sección 9 (preguntas abiertas).

---

## 1. Contexto

| Aspecto | Descripción |
|---|---|
| Cliente | ABC Software Corp, empresa mediana que vende abarrotes y mercadería al por mayor y al por menor. |
| Sistema legado | Fichas simples de almacén con los campos `fecha`, `ingreso`, `salida`, `producto` y `nro_documento` (documento interno informal). |
| Problema | SUNAT exige libros y registros formales (RS 234-2006) y comprobantes electrónicos en UBL 2.1 (RS 097-2012 y normas de masificación; Anexo 9-A de la RS 117-2017). El legado no valida el RUC, no calcula IGV, ISC ni ICBPER, no genera XML firmado y no se comunica con un OSE ni con SUNAT. |
| Objetivo de la Fase 1 | Producir el esqueleto de especificaciones: modelo de dominio y contratos, arquitectura MVC con visión hexagonal, contratos de API y matriz de trazabilidad normativa. |

---

## 2. Inventario de entradas (resultado del PASO 0)

| ID | Entrada | Ubicación | Estado | Observación |
|---|---|---|---|---|
| ENT-01 | Esquemas UBL (OASIS) | `Git/UBL-2.1/xsd/` (principal, agregado el 28/10) y `Git/tradeshift-ubl-xsd/.../schemas/` (2.2, control cruzado) | ✅ **UBL 2.1 OS** | Paquete oficial OASIS UBL 2.1 (04/11/2013): `UBL-Invoice/CreditNote/DebitNote-2.1.xsd`, `common/` y xmldsig. `Git/UBL-Invoice-2.1.xsd` suelto es idéntico al del paquete. `git status --short` en `tradeshift-ubl-xsd` no mostró cambios. |
| ENT-02 | Catálogos del Anexo 8 (01–10, 16, 51–53) | `Git/NN.txt` | OK, en formato JSON | Fuente comunitaria **no oficial** (2020). Son 14 archivos JSON válidos. El 02 y el 04 usan claves ISO en inglés. |
| ENT-03 | Anexo 9-A, Estándar UBL 2.1 (RS 117-2017) | `Git/anexoIX-117-2017.pdf` | OK (31 páginas) | Factura en las págs. 1–10, boleta 11–18, nota de crédito 19–22, nota de débito 23–27, resumen diario 28–30 y comunicación de baja 31. Se ignora la columna RRSSPP. |
| ENT-04 | Anexos posteriores (RS 114-2019 anexo VII, RS 150-2019 anexo VIII, RS 193-2020 anexo IV) | — | ❌ **No están** | Todo lo que dependa de ellos (ICBPER y cambios posteriores a 2019) queda `PENDIENTE`. |
| ENT-05 | Manual de la API de Nubefact (JSON) | `Git/NUBEFACT DOC API JSON V1.md` | OK, completo | Sirve como referencia de mercado. Se ignora `Git/edit.htm`. La ruta y el token de ejemplo **no se copian**: en los specs se escriben `<RUTA>` y `<TOKEN>`. |
| ENT-06 | Observaciones del DEMO de Nubefact | `Git/observaciones-nubefact-demo.md` | OK | Es un insumo del estudiante, no una fuente primaria. Se cita desde `Git/`. |
| ENT-07 | Formatos 14.1, 8.1 y 12.1 | `Git/234_formato141.pdf`, `Git/FORMATO_12_1.pdf` (28/10) y `Git/*.xls*` (extraídos en `referencias/formatos/`) | ✅ **Cubierto** / ⚠ faltan tablas | 14.1: formato impreso (PDF, RS 234-2006) y estructura PLE (comunitaria). 8.1: estructura PLE y plantilla simplificada. 12.1: cabecera e información mínima (PDF). **Faltan** las tablas 5, 6 y 12 y el texto completo de la RS 234-2006. |
| ENT-08 | XSD propios de SUNAT para el resumen diario y la baja (`SummaryDocuments`, `VoidedDocuments`, prefijo `sac:`) | — | ⚠ No hay XSD, pero sí reglas XSL (ENT-10) | 30 de las 37 filas `sac:` se verifican con la validación SUNAT (XSL). Quedan 7 PENDIENTE. |
| ENT-09 | Catálogos que el Anexo 9-A cita pero que no están en `Git/` (11, 12, 13, 14, 15, 17, 19…) | — | ❌ | Se referencian por código y quedan `PENDIENTE`. |
| ENT-10 | **Validación SUNAT vigente (hojas XSL, 06/09/2022)** | `Git/XSL Actualizado al 06092022 (1)/validaciones/` → `referencias/sunat-xsl/` | ✅ (procedencia plausible, no verificable) | 3 378 reglas con 891 códigos de error. Prevalecen sobre el Anexo 9-A de 2017: emisor y adquirente en PartyIdentification/PartyLegalEntity, tipo de operación en InvoiceTypeCode/@listID, versiones 2.1/2.0, ICBPER y cuotas. No reemplazan a los XSD de SUNAT. |

---

## 3. Requisitos funcionales

| ID | Requisito | Fuente / justificación | Entregable |
|---|---|---|---|
| RF-01 | Emitir una factura electrónica en UBL 2.1. | Anexo 9-A, lit. a), págs. 1–10 | 1, 3, 4 |
| RF-02 | Emitir una boleta de venta electrónica. | Anexo 9-A, lit. b), págs. 11–18 | 1, 3, 4 |
| RF-03 | Emitir una nota de crédito con el documento afectado y el motivo. | Anexo 9-A, lit. c), págs. 19–22 (`cac:DiscrepancyResponse`, `cac:BillingReference`); catálogo 09 | 1, 3, 4 |
| RF-04 | Emitir una nota de débito con el documento afectado y el motivo. | Anexo 9-A, lit. d), págs. 23–27; catálogo 10 | 1, 3, 4 |
| RF-05 | Generar el resumen diario de boletas y notas. | Anexo 9-A, lit. E), págs. 28–30 (identificador `RC-<Fecha>-`) | 1, 3, 4 |
| RF-06 | Generar la comunicación de baja en dos pasos: envío con ticket y consulta de estado. | Anexo 9-A, lit. F), pág. 31 (identificador `RA-<Fecha>`); flujo de 2 pasos en ENT-06 §8 | 1, 3, 4 |
| RF-07 | Administrar series y correlativos por establecimiento y tipo de comprobante, incluidas las series de contingencia. | Anexo 9-A, `cbc:ID` "Serie y número del comprobante", págs. 1 y 11; ENT-06 §6 | 1, 3 |
| RF-08 | Validar el RUC (formato y dígito verificador) y el documento de identidad del adquirente. | Catálogo 06; la regla del dígito verificador queda `PENDIENTE` de fuente oficial | 1, 3 |
| RF-09 | Calcular y validar IGV, ISC (por sistema de cálculo) e ICBPER por línea, junto con los totales por tipo de afectación. | Catálogos 05, 07 y 08 (`cbc:TierRange`, Anexo 9-A págs. 10 y 17). El ICBPER queda `PENDIENTE` (ENT-04). | 1, 4 (solo se especifica; no se implementa en la Fase 1) |
| RF-10 | Generar el XML UBL, firmarlo (`ext:UBLExtensions` / `ds:Signature`) y enviarlo al OSE o a SUNAT; recibir y guardar el CDR. | Anexo 9-A, "Firma Digital", pág. 1; RS 097-2012 | 2, 3 |
| RF-11 | Consultar un comprobante y descargar su XML, su CDR y su representación impresa. | ENT-05, operación 2; ENT-06 §7 | 3 |
| RF-12 | Consultar los catálogos SUNAT (`/catalogos/{n}`). | Anexo 8 (ENT-02) | 1, 3 |
| RF-13 | Mantener productos con código interno, código de producto SUNAT y unidad de medida (catálogo 03). | Anexo 9-A (unidad: catálogo 03); ENT-06 §4 | 1 |
| RF-14 | Registrar la forma de pago (contado o crédito) con cuotas. | ENT-06 §3. La base normativa de las cuotas es posterior a 2019 y queda `PENDIENTE` (ENT-04). | 1 |
| RF-15 | Importar las fichas del legado conservando la trazabilidad y permitir consultar el estado de la importación. | Restricción R-01 | 1, 3, 6 |
| RF-16 | Generar por período los registros 14.1 (ventas), 8.1 (compras) y 12.1 (inventario permanente en unidades físicas). | RS 234-2006 (no está en el workspace, ENT-07); el alcance se confirma en la pregunta P-4 | 1, 3 |
| RF-17 | Llevar el ciclo de estados del comprobante: borrador → emitido → aceptado / rechazado / observado → anulado. | ENT-06 §2 y §8. El estado "observado" es un `SUPUESTO` (SUP-06). | 1 |
| RF-18 | Registrar el movimiento de almacén asociado a cada comprobante, que continúa la ficha del legado. | Restricción R-01 y RF-16 (12.1) | 1, 6 |

**Fuera del alcance de la Fase 1** (solo se anotan): guías de remisión, retenciones, percepciones, detracciones, anticipos, operaciones de región selva y recibos de servicios públicos (RRSSPP).

---

## 4. Requisitos no funcionales

| ID | Requisito | Justificación |
|---|---|---|
| RNF-01 | **Arquitectura evolutiva:** monolito MVC modular con puertos y adaptadores, del que se puedan extraer microservicios por contexto. | Restricción R-03; ADR-001 y ADR-002 |
| RNF-02 | **Distribución nativa:** Windows (instalador MSI) y Android (APK). En la Fase 1 solo se especifica el empaquetado. | Restricción R-04; ADR-003 |
| RNF-03 | **Operación sin conexión en Android:** emisión local, cola persistente de envío al OSE o a SUNAT con reintentos, almacenamiento local cifrado, custodia del certificado digital y uso de series de contingencia. | Restricción R-04; ENT-06 §6 (columna «Offline» y series de contingencia); ADR-006. Los plazos de envío quedan `PENDIENTE` de norma. |
| RNF-04 | **Idempotencia:** reintentar una emisión o un envío no debe duplicar el comprobante ni consumir otro correlativo. Se usa una clave de idempotencia y la unicidad emisor + tipo + serie + número. | Integridad de la numeración (RF-07) |
| RNF-05 | **Trazabilidad:** cada dato del contrato traza hasta la norma, el XPath, el DTO, la operación de la API, el caso de uso y el origen en el legado. | Entregable 4 |
| RNF-06 | **Parametrización tributaria:** las tasas y los montos (IGV, ICBPER, tasas o montos del ISC, UIT) son parámetros con vigencia (desde / hasta), nunca constantes. | Las tasas cambian por norma; no se fijan de memoria. |
| RNF-07 | **Seguridad:** el certificado digital y las credenciales del OSE o de SUNAT se guardan en el almacén seguro del sistema operativo (Windows y Android Keystore) y nunca en el código, los logs ni los archivos de especificación. | Política del proyecto; ADR-004 y ADR-006 |
| RNF-08 | **Auditoría e inmutabilidad:** un comprobante emitido no se edita; solo se corrige con una nota o una baja. Se conservan el XML firmado y el CDR. | Anexo 9-A lit. c), d) y F). El plazo de conservación queda `PENDIENTE` de norma. |
| RNF-09 | **Independencia del proveedor:** el dominio usa los códigos de los catálogos SUNAT. Los códigos propios de un proveedor (por ejemplo, los enteros 1–4 de Nubefact) solo existen en el adaptador de salida. | ADR-004 |
| RNF-10 | **Localización:** documentación y mensajes en español; moneda por catálogo 02; fechas `yyyy-mm-dd` y horas `hh:mm:ss`. | Anexo 9-A, columna Formato |

---

## 5. Restricciones obligatorias

| ID | Restricción | Cómo se refleja en los specs |
|---|---|---|
| R-01 | Mapear el histórico del legado a las nuevas entidades sin perder trazabilidad. | `06-migracion/mapeo-legado.md`; la columna "origen en legado" de la matriz; ADR-005 |
| R-02 | Normativa peruana: catálogos del Anexo 8, series, correlativos y validaciones de emisión. El catálogo 08 (sistema de cálculo del ISC) es un punto clave. | `catalogs/`, `reglas-de-validacion.md` y la matriz |
| R-03 | Monolito MVC limpio, desacoplable hacia arquitectura hexagonal y luego microservicios. | `03-arquitectura/` y `04-api/puertos.md` |
| R-04 | Nativo en Windows y Android, con empaquetado MSI o APK. | ADR-003 y ADR-006 |
| R-05 | Contrastar los casos de uso con un facturador en línea (Nubefact). | `01-casos-de-uso.md` |
| R-06 | Fase 1 sin lógica de negocio. | DTOs con `// TODO(spec: REG-XXX)` |

---

## 6. Supuestos

| ID | Supuesto | Estado |
|---|---|---|
| SUP-01 | ~~Se usan los XSD UBL 2.2 porque falta el 2.1.~~ **Cerrado (28/10):** la verificación se hace contra `Git/UBL-2.1/xsd`. Las 127 rutas existen en 2.1 y en 2.2 con la misma cardinalidad (M11). | ✅ Resuelto |
| SUP-02 | ABC está obligada a emitir electrónicamente y lo hace desde sus propios sistemas (SEE-Del Contribuyente, RS 097-2012). | `SUPUESTO` |
| SUP-03 | Los catálogos comunitarios (2020) se usan como semilla. Los catálogos 05, 07, 08 y 51 se contrastan con las tablas del Anexo 9-A cuando aparecen allí; el resto queda marcado como no oficial. | `SUPUESTO` |
| SUP-04 | La tasa del IGV vigente **no** se fija. El DEMO de Nubefact muestra 18 % por defecto, pero eso no es una fuente normativa. | `PENDIENTE`: verificar en la fuente oficial |
| SUP-05 | El ICBPER (Ley 30884, 2019) es posterior al Anexo 9-A. Su XPath y su tasa no se pueden verificar con las entradas actuales. | `PENDIENTE` (ENT-04) |
| SUP-06 | SUNAT puede devolver el estado "aceptado con observaciones". Se modela como el estado `OBSERVADO`. | `SUPUESTO`: confirmar el catálogo de respuestas del CDR |
| SUP-07 | En el legado, `nro_documento` es un número interno informal: no es una serie-número SUNAT. Se conserva como referencia de origen. | `SUPUESTO` |
| SUP-08 | Las fichas del legado registran cantidades, no importes, por lo que alimentan el formato 12.1 (unidades físicas) y no directamente el 14.1. | `SUPUESTO`: confirmar con una muestra real |
| SUP-09 | La boleta se informa a SUNAT por medio del resumen diario, que el Anexo 9-A incluye como lit. E). Los montos umbral y los plazos no se fijan aquí. | `PENDIENTE` de norma |

---

## 7. Riesgos

| ID | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| RSK-01 | Diferencias entre UBL 2.2 y 2.1 provocan XPath falsamente verificados. | — | — | **Cerrado:** se verifica en 2.1 y se compara con 2.2 (M11: 0 diferencias). |
| RSK-02 | Los catálogos no oficiales están desactualizados (son de 2020). | Alta | Alto | Marcarlos como no oficiales en `INDEX.md`, versionarlos y descargarlos de nuevo del Anexo 8 oficial. |
| RSK-03 | Falta la normativa posterior a 2019: ICBPER, forma de pago con cuotas y cambios de validaciones. | Alta | Alto | Marcar PENDIENTE y registrar la discrepancia; solicitar los anexos. |
| RSK-04 | El certificado digital queda expuesto en un dispositivo Android perdido o robado. | Media | Alto | Usar Android Keystore, firma en el servidor o en el OSE como alternativa (ADR-004 y ADR-006) y revocación. |
| RSK-05 | Se duplican correlativos por emisión sin conexión en varios dispositivos. | Media | Alto | Asignar bloques de series de contingencia por dispositivo, imponer la unicidad emisor + tipo + serie + número y usar idempotencia (ADR-006). |
| RSK-06 | Los datos del legado están sucios: productos sin código, documentos repetidos, fechas inválidas, ingreso y salida en la misma ficha. | Alta | Medio | Importación por etapas con cuarentena y reporte de errores (ADR-005). |
| RSK-07 | Se acopla el dominio a los códigos de Nubefact u otro proveedor. | Media | Medio | Mapeo solo en el adaptador (RNF-09). |
| RSK-08 | Hay discrepancias internas en el Anexo 9-A, por ejemplo `cbc:ProfileID` "Catálogo 51" con `@schemeURI` terminado en `catalogo17` (págs. 1 y 11), o `cbc:TierRange` en la nota de crédito con cardinalidad y catálogo distintos (pág. 22). | Alta | Medio | Registrarlas en la hoja de discrepancias y no elegir en silencio. |
| RSK-09 | No hay XSD de SUNAT para el resumen diario y la baja. | Alta | Medio | Marcar sus XPath como PENDIENTE de verificación. |

---

## 8. Discrepancias

La lista completa (DISC-01 a DISC-17), con su fuente y la decisión tomada, está en [`05-trazabilidad/discrepancias.csv`](05-trazabilidad/discrepancias.csv) y en la [matriz §3](05-trazabilidad/matriz-trazabilidad.md). Las más relevantes para la defensa:

| ID | Discrepancia | Estado |
|---|---|---|
| DISC-01 | `cbc:ProfileID`: el dato dice "Catálogo 51", pero el `@schemeURI` termina en `catalogo17` (págs. 1 y 11) | **Cerrada**: la validación vigente no usa ProfileID (MT-087) |
| DISC-02 | `TierRange` de la NC (pág. 22). Con la extracción `-layout` parecía `1/an4/Cat. 05`; con la extracción `raw` es `0..1/an2/Cat. 08` | **Cerrada**: era un artefacto de la extracción |
| DISC-03 | El Anexo 9-A es UBL 2.1, pero el XSD disponible era 2.2 | **Cerrada**: el XSD 2.1 está en `Git/UBL-2.1/xsd` |
| DISC-04 | La boleta figura como `InvoiceTypeCode "02"` en el anexo (pág. 11), pero en el catálogo 01 es `03` | **Cerrada**: la validación SUNAT exige `^03$` (error 1003) |
| DISC-05 | En la factura, las longitudes de `TaxScheme/cbc:ID` y `TaxTypeCode` están invertidas respecto de la NC, la ND y el RC | Abierta |
| DISC-06 | `ProfileID an2` frente a los códigos de 4 dígitos del catálogo 51 | **Cerrada**: SUNAT valida el catálogo 51 en `InvoiceTypeCode/@listID` |
| DISC-07 y DISC-08 | XPath del anexo que no existen en el XSD (`cac:CreditLine`, `cac:DebitLine`, `cac:DebitDocumentReference`) | **Cerradas**: la validación SUNAT usa `CreditNoteLine`, `DebitNoteLine` e `InvoiceDocumentReference` |
| DISC-12 | `UBLVersionID`/`CustomizationID`: "2.1"/"2.0" en la factura frente a "2.0"/"1.0" en la boleta, la NC y la ND | **Cerrada**: SUNAT exige "2.1"/"2.0" en los cuatro |
| DISC-13 | El anexo da la serie de la boleta como `F###`, mientras que el DEMO y el manual de Nubefact usan `B` | **Cerrada**: SUNAT valida `B###` o `NNNN` |
| DISC-14 | ICBPER (7152) y el código 13 del catálogo 09 no tienen respaldo en el anexo de 2017 | Parcial: la estructura del ICBPER y de las cuotas está confirmada por la validación SUNAT; falta la tasa y el texto de los anexos (ENT-04) |
| DISC-25 | El anexo de 2017 pone emisor y adquirente en `PartyTaxScheme`; la validación vigente usa `PartyIdentification`/`PartyLegalEntity` | **Cerrada**: el contrato sigue la estructura vigente (MT-073 a MT-079, MT-088) |

---

## 9. Preguntas abiertas

**Respondidas por el líder del equipo (CHECKPOINT del PASO 1):**

| ID | Pregunta | Respuesta |
|---|---|---|
| P-1 | Lenguaje o stack | **Kotlin + Compose Multiplatform** (ADR-003) |
| P-2 | Alcance de comprobantes | **Confirmado:** factura, boleta, NC, ND, comunicación de baja y resumen diario |
| P-3 | Integración | **OSE como canal principal**, con SUNAT directo como segundo adaptador (ADR-004) |
| P-4 | Formatos 8.1 y 12.1 | **Incluidos** junto con el 14.1. Su estructura queda PENDIENTE (ENT-07) |
| P-6 | Anexos de 2019–2020 | **No disponibles**: se marcan PENDIENTE. Se trabaja solo con la información de `Git/` |
| P-7 | XSD de UBL 2.1 | **Agregado** el 28/10 (`Git/UBL-2.1/`). Siguen faltando los XSD de SUNAT para el resumen diario y la baja (P-7b) |

**Siguen abiertas:**

| ID | Pregunta | Bloquea |
|---|---|---|
| P-5 | ¿Cuáles son la fecha de entrega, el formato, la extensión y la rúbrica? (Se asumió un repositorio en Markdown) | Paso 9 (exportación) |
| P-6b | Los formatos 14.1, 8.1 y 12.1 ya están cubiertos. **Faltan** las tablas 5 (existencia), 6 (unidad de medida) y 12 (tipo de operación), y contrastar la estructura PLE comunitaria con la oficial | REG-142, REG-148 y BR-01/BR-06/BR-09 |
| P-7b | Se necesitan los XSD de SUNAT para `SummaryDocuments` y `VoidedDocuments` | 37 filas PENDIENTE de la matriz |
| P-11 | Se necesitan los catálogos 11, 12, 13 (ubigeo) y 19 y el Anexo 8 oficial vigente | REG-026, REG-038, REG-123 y RSK-02 |
| P-12 | Se necesita la norma de contingencia y sus plazos | REG-110, REG-111 y REG-170 |
| P-8 | ¿Cuál es la fuente oficial del algoritmo del dígito verificador del RUC? | REG del RUC (PASO 4) |
| P-9 | ¿Cuáles son las tasas vigentes del IGV y del ICBPER y su fuente oficial? | SUP-04 y SUP-05 |
| P-10 | ¿Hay una muestra real o anonimizada de las fichas del legado? | SUP-07 y SUP-08 |
