# Validación SUNAT vigente: hojas XSL (06/09/2022)

> **Fuente:** `Git/XSL Actualizado al 06092022 (1)/validaciones/` (15 archivos `.xsl`, agregados el 28/10). Solo lectura.
> **Generado:** `reglas-xsl.csv`, con `tools/extraer_reglas_xsl.py`. Este README se escribió a mano.

## Qué son y qué no son

- Son las **hojas de validación de reglas de negocio** con las que SUNAT valida los comprobantes electrónicos: obligatoriedad, expresiones regulares, catálogos, coherencia de montos y **códigos de error** (por ejemplo, 2074 = "UBLVersionID distinto", 3206 = "tipo de operación no válido para el comprobante").
- **No son XSD.** No describen la estructura completa del documento. Por eso no sustituyen a los XSD SUNAT de `SummaryDocuments` y `VoidedDocuments`, aunque sí confirman qué rutas valida SUNAT en esos documentos.
- **No se ejecutan:** usan extensiones de **IBM DataPower** (`dp:`) e incluyen archivos de SUNAT (`local:///commons/error/validate_utils.xsl`) que no vienen en la carpeta. Solo se **leen**.

## Evaluación de procedencia

| Indicio | Observación |
|---|---|
| Espacio de nombres SUNAT | `sac` = `urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1` |
| Plataforma | Extensiones `dp:` de IBM DataPower, la que SUNAT usa en su validación |
| Trazas internas | Comentarios de cambios internos (`Pase126 Contingencia js 260718`, `PAS20191U210000012`, `PaseYYYY`) |
| Fecha | El nombre de la carpeta (06/09/2022) es coherente con la actualización de XSD y XSL de 2022 |
| Firma o hash publicado | **No hay.** La procedencia es **plausible pero no verificable** criptográficamente |

**Conclusión:** se usan como **fuente oficial con procedencia no verificada**. Donde contradicen al Anexo 9-A (2017), prevalecen por ser posteriores y por ser lo que SUNAT valida hoy. La discrepancia queda registrada en cada caso.

## Contenido

| Hoja | Documento | Reglas con código |
|---|---|---|
| ValidaExprRegFactura-2.0.1 | Factura (01) | 771 |
| ValidaExprRegBoleta-2.0.1 | Boleta (03) | 612 |
| ValidaExprRegNC-2.0.1 / ND-2.0.1 | Nota de crédito y débito | 387 / 359 |
| ValidaExprRegSummary-1.1.0 (y 1.0.1) | Resumen diario | 73 (42) |
| ValidaExprRegSummaryVoided-1.0.1 | Comunicación de baja | 28 |
| Liquidación, Guía, Percepción, Retención, Adquirente y Operador | Fuera de alcance o de soporte | resto |
| **Total** | | **3 378 reglas, 891 códigos distintos** |

## Qué cambió en los specs gracias a estas hojas

| Hallazgo | Antes (Anexo 9-A, 2017) | Vigente (XSL) | Efecto |
|---|---|---|---|
| Tipo de operación | `cbc:ProfileID` | `cbc:InvoiceTypeCode/@listID` (catálogo 51, error 3206) | MT-087. DISC-01 y DISC-06 cerradas |
| Emisor y adquirente | `cac:PartyTaxScheme` | `cac:PartyIdentification/cbc:ID` + `cac:PartyLegalEntity` | MT-073 a MT-079 y MT-088. DISC-25 |
| Ubigeo del emisor | `PostalAddress/cbc:AddressTypeCode n6` (pág. 13) | `PartyLegalEntity/cac:RegistrationAddress/cbc:ID` (error 4093) | MT-077. DISC-24 cerrada |
| Versiones UBL | Boleta, NC y ND: "2.0"/"1.0" | Todas "2.1"/"2.0"; RC "2.0"/"1.1"; RA "2.0"/"1.0" | REG-001 y REG-002. DISC-12 cerrada |
| Boleta | Tipo "02", serie "F###" | Tipo `^03$` (error 1003), serie `^([B]…|[0-9]{4})` | DISC-04 y DISC-13 cerradas |
| Comprobante afectado de la NC y la ND | `CreditNoteDocumentReference` / `DebitDocumentReference` | `cac:InvoiceDocumentReference` | MT-099 y MT-100 corregidas. DISC-08 y DISC-11 cerradas |
| ICBPER | No existía | `BaseUnitMeasure` (NIU) + `TaxCategory/cbc:PerUnitAmount` | MT-190 a MT-192 confirmadas; MT-192 **corregida** |
| Forma de pago y cuotas | No existía | `PaymentTerms` `FormaPago` / `Contado` / `Credito` / `Cuota###` | MT-193 a MT-196 y REG-028/REG-029 confirmadas |
| Resumen diario y baja | Sin XSD | Las rutas `sac:` se validan con códigos de error | 30 filas pasan de PENDIENTE a "verificado en XSL SUNAT" |

## Columnas de `reglas-xsl.csv`

`documento, archivo, linea, plantilla, contexto, nodo, regexp, catalogo, codigos_error, comentario`. La columna **contexto** es el último `template match` o `for-each select` previo a la regla. Es una aproximación: no resuelve anidamientos, así que el cruce con la matriz (columna `codigos_error_sunat`) es **heurístico** y debe revisarse a mano antes de usarlo en código.
