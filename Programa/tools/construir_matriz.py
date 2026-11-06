"""PASO 7: construye la matriz de trazabilidad normativa (CSV + MD + discrepancias).

Las filas se transcriben del Anexo 9-A (Git/anexoIX-117-2017.pdf) con su página.
Las columnas 'cardinalidad_ubl', 'tipo_xsd' y 'verificado_xsd' se calculan contra el
XSD con tools/ubl_xsd.py (no se escriben a mano). tools/verificar_matriz.py vuelve
a comprobar todo de forma independiente.

Uso:  python tools/construir_matriz.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import yaml  # pip install -r tools/requirements.txt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ubl_xsd import XSD_DIR_22, EsquemaUBL  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
OUT = RAIZ / "Programa" / "specs" / "05-trazabilidad"

COLUMNAS = [
    "id", "norma_anexo_pagina", "dato_sunat", "catalogo", "xpath_ubl", "tipo_longitud",
    "cardinalidad_ubl", "obligatoriedad", "regla", "campo_dto_schema", "operacion_openapi",
    "caso_uso", "origen_legado", "campo_nubefact", "verificado_xsd", "codigos_error_sunat", "observaciones",
]

LIT = {"a": "a) Factura", "b": "b) Boleta", "c": "c) Nota de crédito", "d": "d) Nota de débito",
       "E": "E) Resumen diario", "F": "F) Comunicación de baja"}

INV = "/Invoice"
SUP = "cac:AccountingSupplierParty/cac:Party"
CUS = "cac:AccountingCustomerParty/cac:Party"
FIRMA = "ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/ds:Signature"
TS = "cac:TaxTotal/cac:TaxSubtotal"
TC = f"{TS}/cac:TaxCategory"

C = "comprobante.schema.yaml"
N = "nota.schema.yaml"
L = "linea-detalle.schema.yaml"
T = "totales.schema.yaml"
A = "adquirente.schema.yaml"
E = "emisor.schema.yaml"
TR = "tributo.schema.yaml"
RA = "comunicacion-baja.schema.yaml"
RC = "resumen-diario.schema.yaml"
FP = "forma-pago.schema.yaml"

OP_EMIT = "emitirComprobante; consultarComprobante; descargarXml"
OP_NC = "emitirNotaCredito; consultarComprobante"
OP_ND = "emitirNotaDebito; consultarComprobante"
OP_RA = "crearComunicacionBaja; consultarEstadoBaja"
OP_RC = "crearResumenDiario; consultarEstadoResumen"

FILAS: list[dict] = []


def r(id_, lit, pag, dato, cat, xpath, tipo, oblig, regla, dto, op, cu, legado="—", nube="—", obs=""):
    FILAS.append({
        "id": id_, "norma_anexo_pagina": f"RS 117-2017, Anexo 9-A, lit. {LIT[lit]}, pág. {pag}",
        "dato_sunat": dato, "catalogo": cat, "xpath_ubl": xpath, "tipo_longitud": tipo,
        "obligatoriedad": oblig, "regla": regla, "campo_dto_schema": dto, "operacion_openapi": op,
        "caso_uso": cu, "origen_legado": legado, "campo_nubefact": nube, "observaciones": obs,
    })


# ---------------- a) FACTURA ----------------
r("MT-001", "a", 1, "Firma digital", "—", f"{INV}/{FIRMA}", "an..3000 (XMLDSig)", "OBLIGATORIO (anexo: 1)",
  "REG-090; REG-091", f"{C}#/properties/firma (firma-digital.schema.yaml)", OP_EMIT, "CU-01", "—", "— (la firma la hace el proveedor)",
  "ExtensionContent es xsd:any: el XSD no obliga la firma (mapa-xsd §2).")
r("MT-002", "a", 1, "Versión del UBL", "—", f"{INV}/cbc:UBLVersionID", 'an..10, valor "2.1"', "OBLIGATORIO (anexo: 0..1, valor fijo)",
  "REG-001", "interno (parámetro del generador UBL)", OP_EMIT, "CU-01", obs="DISC-12: boleta, NC y ND dicen \"2.0\".")
r("MT-003", "a", 1, "Versión de la estructura del documento", "—", f"{INV}/cbc:CustomizationID", 'an..10, valor "2.0"',
  "OBLIGATORIO (anexo: 0..1, valor fijo)", "REG-002", "interno (parámetro del generador UBL)", OP_EMIT, "CU-01", obs="DISC-12: boleta, NC y ND dicen \"1.0\".")
r("MT-004", "a", 1, "Código de tipo de operación", "51", f"{INV}/cbc:ProfileID", "an2 (anexo) / códigos n4 (catálogo)",
  "CONDICIONAL (anexo: 0..1)", "REG-021; REG-023", f"{C}#/properties/tipoOperacion", OP_EMIT, "CU-01", "—", "sunat_transaction (entero propio)",
  "DISC-06 (longitud). Catálogo 51, no 17.")
r("MT-005", "a", 1, "URI del catálogo del tipo de operación", "51", f"{INV}/cbc:ProfileID/@schemeURI",
  '"urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo17"', "CONDICIONAL (anexo: 0..1)", "REG-021", "interno (constante del generador UBL)",
  OP_EMIT, "CU-01", obs="DISC-01: dice catalogo17 y el dato dice Catálogo 51.")
r("MT-006", "a", 1, "Serie y número del comprobante", "—", f"{INV}/cbc:ID", "F###-NNNNNNNN", "OBLIGATORIO (anexo: 1)",
  "REG-030; REG-034; REG-035", f"{C}#/properties/serie + /correlativo", OP_EMIT, "CU-01; CU-07", "nro_documento (solo como referencia de origen)",
  "serie + numero", "El legado no tiene serie SUNAT (mapeo-legado.md).")
r("MT-007", "a", 1, "Fecha de emisión", "—", f"{INV}/cbc:IssueDate", "yyyy-mm-dd", "OBLIGATORIO (anexo: 1)", "REG-080",
  f"{C}#/properties/fechaEmision", OP_EMIT, "CU-01", "fecha", "fecha_de_emision (DD-MM-AAAA)", "Nubefact usa otro formato de fecha: lo convierte el adaptador.")
r("MT-008", "a", 1, "Hora de emisión", "—", f"{INV}/cbc:IssueTime", "hh-mm-ss.0z (anexo)", "OPCIONAL (anexo: 0..1)", "REG-082",
  f"{C}#/properties/horaEmision", OP_EMIT, "CU-01", obs="DISC-16: formato con guiones; xsd:time usa ':'.")
r("MT-009", "a", 1, "Fecha de vencimiento", "—", f"{INV}/cbc:DueDate", "yyyy-mm-dd", "OPCIONAL (anexo: 0..1)", "REG-081",
  f"{C}#/properties/fechaVencimiento", OP_EMIT, "CU-01", "—", "fecha_de_vencimiento")
r("MT-010", "a", 1, "Código de tipo de documento", "01", f"{INV}/cbc:InvoiceTypeCode", "an2", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-004; REG-010", f"{C}#/properties/tipoComprobante", OP_EMIT, "CU-01", "—", "tipo_de_comprobante (1-4, propio)",
  "Atributos @listAgencyName=PE:SUNAT, @listURI=...catalogo01.")
r("MT-011", "a", 1, "Leyenda", "52", f"{INV}/cbc:Note", "an..100", "CONDICIONAL (anexo: 0..n)", "REG-008",
  f"{C}#/properties/leyendas/items/properties/texto", OP_EMIT, "CU-01", "—", "— (lo genera el proveedor)")
r("MT-012", "a", 1, "Código de leyenda", "52", f"{INV}/cbc:Note/@languageLocaleID", "n4", "CONDICIONAL (anexo: 0..1)", "REG-025",
  f"{C}#/properties/leyendas/items/properties/codigo", OP_EMIT, "CU-01")
r("MT-013", "a", 1, "Código de tipo de moneda", "02", f"{INV}/cbc:DocumentCurrencyCode", "an3 (ISO 4217)", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-011; REG-069", f"{C}#/properties/moneda", OP_EMIT, "CU-01", "—", "moneda (1-4, propio)")
r("MT-014", "a", 1, "Cantidad de ítems", "—", f"{INV}/cbc:LineCountNumeric", "n3", "OPCIONAL (anexo: 0..1)", "REG-009",
  "interno (derivado de lineas.length)", OP_EMIT, "CU-01")
r("MT-015", "a", 2, "Número de la orden de compra", "—", f"{INV}/cac:OrderReference/cbc:ID", "an..20", "OPCIONAL (anexo: 0..1)", "REG-100",
  f"{C}#/properties/ordenCompra", OP_EMIT, "CU-01", "—", "orden_compra_servicio")
r("MT-016", "a", 2, "Número de guía de remisión relacionada", "—", f"{INV}/cac:DespatchDocumentReference/cbc:ID",
  "NNNN-NNNNNNNN / R###-NNNNNNNN", "OPCIONAL (anexo: 0..n)", "REG-100", f"{C}#/properties/guias/items/properties/serieNumero",
  OP_EMIT, "CU-01", "—", "guias[].guia_serie_numero")
r("MT-017", "a", 2, "Código de tipo de guía de remisión", "01", f"{INV}/cac:DespatchDocumentReference/cbc:DocumentTypeCode", "an2",
  "OPCIONAL (anexo: 0..1)", "REG-010", f"{C}#/properties/guias/items/properties/tipo", OP_EMIT, "CU-01", "—", "guias[].guia_tipo (propio)")
r("MT-018", "a", 2, "Número de documento relacionado", "—", f"{INV}/cac:AdditionalDocumentReference/cbc:ID", "an..30",
  "OPCIONAL (anexo: 0..n)", "REG-100", f"{C}#/properties/documentosRelacionados/items/properties/numero", OP_EMIT, "CU-01",
  "nro_documento (documento interno)")
r("MT-019", "a", 2, "Código de tipo de documento relacionado", "12", f"{INV}/cac:AdditionalDocumentReference/cbc:DocumentTypeCode",
  "an2", "OPCIONAL (anexo: 0..1)", "REG-026", f"{C}#/properties/documentosRelacionados/items/properties/tipo", OP_EMIT, "CU-01",
  obs="Catálogo 12 no está en el workspace: PENDIENTE.")
r("MT-020", "a", 3, "Información adicional de la firma", "—", f"{INV}/cac:Signature", "agregado", "OBLIGATORIO en contrato (anexo: 0..n)",
  "REG-092", "firma-digital.schema.yaml#/properties/firmanteRuc", OP_EMIT, "CU-01")
r("MT-021", "a", 3, "Nombre comercial del emisor", "—", f"{INV}/{SUP}/cac:PartyName/cbc:Name", "an..100", "OPCIONAL (anexo: 0..n)", "REG-100",
  f"{E}#/properties/nombreComercial", OP_EMIT, "CU-01")
r("MT-022", "a", 3, "Nombre o razón social del emisor", "—", f"{INV}/{SUP}/cac:PartyTaxScheme/cbc:RegistrationName", "an..100",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-100", f"{E}#/properties/razonSocial", OP_EMIT, "CU-01")
r("MT-023", "a", 3, "Número de RUC del emisor", "—", f"{INV}/{SUP}/cac:PartyTaxScheme/cbc:CompanyID", "n11", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-040; REG-041", f"{E}#/properties/ruc", OP_EMIT, "CU-01; CU-09", "—", "— (lo fija la cuenta y el token del proveedor)",
  "Anexo 2017: PartyTaxScheme (no PartyIdentification).")
r("MT-024", "a", 3, "Tipo de documento de identidad del emisor", "06", f"{INV}/{SUP}/cac:PartyTaxScheme/cbc:CompanyID/@schemeID", 'an1, valor "6"',
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-015; REG-042", "interno (constante \"6\")", OP_EMIT, "CU-01")
r("MT-025", "a", 3, "Código del domicilio fiscal o local anexo del emisor", "—",
  f"{INV}/{SUP}/cac:PartyTaxScheme/cac:RegistrationAddress/cbc:AddressTypeCode", "n4", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-036",
  f"{C}#/properties/establecimientoCodigo", OP_EMIT, "CU-01; CU-07", "—", "— (Locales y Series en el proveedor)",
  "Código SUNAT del establecimiento (ENT-06 §6).")
r("MT-026", "a", 3, "Nombre o razón social del adquirente", "—", f"{INV}/{CUS}/cac:PartyTaxScheme/cbc:RegistrationName", "an..100",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-100", f"{A}#/properties/razonSocial", OP_EMIT, "CU-01", "—", "cliente_denominacion")
r("MT-027", "a", 3, "Número de documento del adquirente", "—", f"{INV}/{CUS}/cac:PartyTaxScheme/cbc:CompanyID", "n11 (RUC)",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-040; REG-041; REG-044", f"{A}#/properties/numeroDocumento", OP_EMIT, "CU-01; CU-09", "—",
  "cliente_numero_de_documento")
r("MT-028", "a", 3, "Tipo de documento de identidad del adquirente", "06", f"{INV}/{CUS}/cac:PartyTaxScheme/cbc:CompanyID/@schemeID", "an1",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-015; REG-042; REG-043", f"{A}#/properties/tipoDocumento", OP_EMIT, "CU-01", "—",
  "cliente_tipo_de_documento", "El anexo rotula este atributo como 'del Emisor' (errata). Nubefact admite '-' (VARIOS), que no está en el catálogo 06 (DISC-15).")
r("MT-029", "a", 6, "Indicador de cargo o descuento global", "53", f"{INV}/cac:AllowanceCharge/cbc:ChargeIndicator", "true/false",
  "CONDICIONAL (anexo: 1 dentro de 0..n)", "REG-024", f"{C}#/properties/cargosDescuentos/items/properties/esCargo", OP_EMIT, "CU-01")
r("MT-030", "a", 6, "Código de motivo de cargo o descuento global", "53", f"{INV}/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode", "an..2",
  "CONDICIONAL (anexo: 0..1)", "REG-024", f"{C}#/properties/cargosDescuentos/items/properties/codigo", OP_EMIT, "CU-01")
r("MT-031", "a", 6, "Factor de cargo o descuento global", "—", f"{INV}/cac:AllowanceCharge/cbc:MultiplierFactorNumeric", "n(3,5)",
  "CONDICIONAL (anexo: 0..1)", "REG-067", f"{C}#/properties/cargosDescuentos/items/properties/factor", OP_EMIT, "CU-01")
r("MT-032", "a", 6, "Monto de cargo o descuento global", "02", f"{INV}/cac:AllowanceCharge/cbc:Amount", "n(12,2)", "CONDICIONAL (anexo: 1)",
  "REG-063; REG-064; REG-067", f"{C}#/properties/cargosDescuentos/items/properties/monto", OP_EMIT, "CU-01", "—", "descuento_global")
r("MT-033", "a", 6, "Base del cargo o descuento global", "02", f"{INV}/cac:AllowanceCharge/cbc:BaseAmount", "n(12,2)", "CONDICIONAL (anexo: 1)",
  "REG-067", f"{C}#/properties/cargosDescuentos/items/properties/base", OP_EMIT, "CU-01")
r("MT-034", "a", 7, "Monto total de impuestos", "02", f"{INV}/cac:TaxTotal/cbc:TaxAmount", "n(12,2)", "OBLIGATORIO en contrato (anexo: 1 dentro de 0..n)",
  "REG-057", f"{T}#/properties/totalTributos", OP_EMIT, "CU-01")
r("MT-035", "a", 7, "Monto de las operaciones gravadas, exoneradas o inafectas", "02", f"{INV}/{TS}/cbc:TaxableAmount", "n(12,2)",
  "CONDICIONAL (anexo: 0..1)", "REG-057; REG-061", f"{TR}#/properties/base", OP_EMIT, "CU-01", "—",
  "total_gravada / total_exonerada / total_inafecta / total_gratuita")
r("MT-036", "a", 7, "Monto total del impuesto", "02", f"{INV}/{TS}/cbc:TaxAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)", "REG-057",
  f"{TR}#/properties/monto", OP_EMIT, "CU-01", "—", "total_igv / total_isc / total_impuestos_bolsas")
r("MT-037", "a", 7, "Categoría de impuestos", "05", f"{INV}/{TC}/cbc:ID", "UN/ECE 5305", "OPCIONAL (anexo: 0..1)", "REG-014",
  "interno (derivado del tributo)", OP_EMIT, "CU-01")
r("MT-038", "a", 7, "Código de tributo", "05", f"{INV}/{TC}/cac:TaxScheme/cbc:ID", "an..3 (anexo) / códigos n4 (catálogo)",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-014", f"{TR}#/properties/codigoTributo", OP_EMIT, "CU-01", obs="DISC-05.")
r("MT-039", "a", 7, "Nombre de tributo", "05", f"{INV}/{TC}/cac:TaxScheme/cbc:Name", "an..6", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-014", "interno (derivado del catálogo 05)", OP_EMIT, "CU-01")
r("MT-040", "a", 7, "Código internacional de tributo", "05", f"{INV}/{TC}/cac:TaxScheme/cbc:TaxTypeCode", "an4 (anexo) / an3 (catálogo)",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-014", "interno (derivado del catálogo 05)", OP_EMIT, "CU-01", obs="DISC-05.")
r("MT-041", "a", 7, "Total valor de venta", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:LineExtensionAmount", "n(12,2)", "CONDICIONAL (anexo: 0..1)",
  "REG-061", f"{T}#/properties/valorVenta", OP_EMIT, "CU-01")
r("MT-042", "a", 7, "Total precio de venta (incluye impuestos)", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:TaxInclusiveAmount", "n(12,2)",
  "CONDICIONAL (anexo: 0..1)", "REG-062", f"{T}#/properties/precioVenta", OP_EMIT, "CU-01")
r("MT-043", "a", 7, "Monto total de descuentos globales", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:AllowanceTotalAmount", "n(12,2)",
  "CONDICIONAL (anexo: 0..1)", "REG-063", f"{T}#/properties/descuentosGlobales", OP_EMIT, "CU-01", "—", "total_descuento")
r("MT-044", "a", 7, "Monto total de otros cargos", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:ChargeTotalAmount", "n(12,2)",
  "CONDICIONAL (anexo: 0..1)", "REG-064", f"{T}#/properties/otrosCargos", OP_EMIT, "CU-01", "—", "total_otros_cargos")
r("MT-045", "a", 7, "Monto total de anticipos", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:PrepaidAmount", "n(15,2)", "CONDICIONAL (anexo: 0..1)",
  "REG-065", f"{T}#/properties/anticipos", OP_EMIT, "CU-01", "—", "total_anticipo", "Detalle de anticipos fuera de alcance (MT-193).")
r("MT-046", "a", 7, "Importe total de la venta", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:PayableAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)",
  "REG-066; REG-068", f"{T}#/properties/importeTotal", OP_EMIT, "CU-01", "—", "total")
r("MT-047", "a", 7, "Moneda de los montos", "02", f"{INV}/cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID", "an3", "OBLIGATORIO (anexo: 1)",
  "REG-011; REG-069", f"{C}#/properties/moneda", OP_EMIT, "CU-01", obs="Aplica a todo @currencyID del documento.")
r("MT-048", "a", 8, "Número de orden del ítem", "—", f"{INV}/cac:InvoiceLine/cbc:ID", "n..3", "OBLIGATORIO (anexo: 1)", "REG-005; REG-006",
  f"{L}#/properties/numeroOrden", OP_EMIT, "CU-01")
r("MT-049", "a", 8, "Cantidad de unidades del ítem", "—", f"{INV}/cac:InvoiceLine/cbc:InvoicedQuantity", "n(12,10)", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-067", f"{L}#/properties/cantidad", OP_EMIT, "CU-01", "salida (cantidad)", "items[].cantidad")
r("MT-050", "a", 8, "Código de unidad de medida del ítem", "03", f"{INV}/cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode", "an..3",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-012", f"{L}#/properties/unidadMedida", OP_EMIT, "CU-01",
  "— (el legado no tiene unidad: brecha)", "items[].unidad_de_medida")
r("MT-051", "a", 8, "Valor de venta del ítem", "02", f"{INV}/cac:InvoiceLine/cbc:LineExtensionAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)",
  "REG-060", f"{L}#/properties/valorVenta", OP_EMIT, "CU-01", "—", "items[].subtotal")
r("MT-052", "a", 8, "Precio de venta unitario o valor referencial unitario", "02",
  f"{INV}/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceAmount", "n(12,10)", "OBLIGATORIO (anexo: 1 dentro de 0..n)",
  "REG-055; REG-067", f"{L}#/properties/precioUnitario/properties/monto", OP_EMIT, "CU-01", "—", "items[].precio_unitario")
r("MT-053", "a", 8, "Código de tipo de precio", "16", f"{INV}/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode",
  "an2", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-020; REG-055", f"{L}#/properties/precioUnitario/properties/tipoPrecio", OP_EMIT, "CU-01")
r("MT-054", "a", 9, "Indicador de cargo o descuento del ítem", "53", f"{INV}/cac:InvoiceLine/cac:AllowanceCharge/cbc:ChargeIndicator", "true/false",
  "CONDICIONAL (anexo: 1 dentro de 0..n)", "REG-024", f"{L}#/properties/cargosDescuentos/items/properties/esCargo", OP_EMIT, "CU-01")
r("MT-055", "a", 9, "Código de cargo o descuento del ítem", "53", f"{INV}/cac:InvoiceLine/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode", "an2",
  "CONDICIONAL (anexo: 0..1)", "REG-024", f"{L}#/properties/cargosDescuentos/items/properties/codigo", OP_EMIT, "CU-01")
r("MT-056", "a", 9, "Factor de cargo o descuento del ítem", "—", f"{INV}/cac:InvoiceLine/cac:AllowanceCharge/cbc:MultiplierFactorNumeric", "n(3,5)",
  "CONDICIONAL (anexo: 0..1)", "REG-067", f"{L}#/properties/cargosDescuentos/items/properties/factor", OP_EMIT, "CU-01")
r("MT-057", "a", 9, "Monto de cargo o descuento del ítem", "02", f"{INV}/cac:InvoiceLine/cac:AllowanceCharge/cbc:Amount", "n(12,2)",
  "CONDICIONAL (anexo: 1)", "REG-060", f"{L}#/properties/cargosDescuentos/items/properties/monto", OP_EMIT, "CU-01", "—", "items[].descuento")
r("MT-058", "a", 9, "Base de cargo o descuento del ítem", "02", f"{INV}/cac:InvoiceLine/cac:AllowanceCharge/cbc:BaseAmount", "n(12,2)",
  "CONDICIONAL (anexo: 1)", "REG-067", f"{L}#/properties/cargosDescuentos/items/properties/base", OP_EMIT, "CU-01")
r("MT-059", "a", 9, "Monto de tributo del ítem", "02", f"{INV}/cac:InvoiceLine/cac:TaxTotal/cbc:TaxAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)",
  "REG-050", f"{L}#/properties/totalTributos", OP_EMIT, "CU-01")
r("MT-060", "a", 9, "Monto de la operación (base del tributo)", "02", f"{INV}/cac:InvoiceLine/{TS}/cbc:TaxableAmount", "n(12,2)",
  "CONDICIONAL (anexo: 0..1)", "REG-050; REG-052", f"{L}#/properties/tributos/items/properties/base (tributo.schema.yaml)", OP_EMIT, "CU-01")
r("MT-061", "a", 9, "Monto de tributo del ítem (subtotal)", "02", f"{INV}/cac:InvoiceLine/{TS}/cbc:TaxAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)",
  "REG-050; REG-052; REG-054", f"{L}#/properties/tributos/items/properties/monto (tributo.schema.yaml)", OP_EMIT, "CU-01", "—", "items[].igv / items[].isc")
r("MT-062", "a", 10, "Categoría de impuestos del ítem", "05", f"{INV}/cac:InvoiceLine/{TC}/cbc:ID", "UN/ECE 5305", "OPCIONAL (anexo: 0..1)", "REG-014",
  "interno (derivado del tributo)", OP_EMIT, "CU-01")
r("MT-063", "a", 10, "Porcentaje del impuesto", "—", f"{INV}/cac:InvoiceLine/{TC}/cbc:Percent", "n(3,5)", "CONDICIONAL (anexo: 0..1)", "REG-051",
  f"{TR}#/properties/tasa", OP_EMIT, "CU-01", "—", "porcentaje_de_igv", "La tasa vigente es un parámetro PENDIENTE (SUP-04).")
r("MT-064", "a", 10, "Código de tipo de afectación del IGV", "07", f"{INV}/cac:InvoiceLine/{TC}/cbc:TaxExemptionReasonCode", "an2",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-016; REG-022", f"{L}#/properties/afectacionIgv", OP_EMIT, "CU-01", "—", "items[].tipo_de_igv (1-…, propio)")
r("MT-065", "a", 10, "Código de tipo de sistema de ISC", "08", f"{INV}/cac:InvoiceLine/{TC}/cbc:TierRange", "an2", "CONDICIONAL (anexo: 0..1)",
  "REG-017; REG-052", f"{L}#/properties/isc/properties/sistemaCalculo", OP_EMIT, "CU-01", "—", "items[].tipo_de_isc (1, 2 o 3)",
  "Punto clave del caso. Condición 'si hay ISC': SUPUESTO.")
r("MT-066", "a", 10, "Código de tributo del ítem", "05", f"{INV}/cac:InvoiceLine/{TC}/cac:TaxScheme/cbc:ID", "an..3 (anexo)", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-014; REG-022", f"{TR}#/properties/codigoTributo", OP_EMIT, "CU-01", obs="DISC-05.")
r("MT-067", "a", 10, "Nombre de tributo del ítem", "05", f"{INV}/cac:InvoiceLine/{TC}/cac:TaxScheme/cbc:Name", "an..6", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-014", "interno (derivado del catálogo 05)", OP_EMIT, "CU-01")
r("MT-068", "a", 10, "Código internacional de tributo del ítem", "05", f"{INV}/cac:InvoiceLine/{TC}/cac:TaxScheme/cbc:TaxTypeCode", "an4 (anexo)",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-014", "interno (derivado del catálogo 05)", OP_EMIT, "CU-01", obs="DISC-05.")
r("MT-069", "a", 10, "Descripción del bien o servicio", "—", f"{INV}/cac:InvoiceLine/cac:Item/cbc:Description", "an..250", "OBLIGATORIO en contrato (anexo: 0..n)",
  "REG-100", f"{L}#/properties/descripcion", OP_EMIT, "CU-01", "producto (texto libre)", "items[].descripcion")
r("MT-070", "a", 10, "Código de producto del ítem", "—", f"{INV}/cac:InvoiceLine/cac:Item/cac:SellersItemIdentification/cbc:ID", "an..30",
  "OPCIONAL (anexo: 1 dentro de 0..1)", "REG-100; REG-132", f"{L}#/properties/codigoProducto", OP_EMIT, "CU-01; CU-13",
  "producto (sin código: brecha)", "items[].codigo")
r("MT-071", "a", 10, "Código de producto SUNAT", "—", f"{INV}/cac:InvoiceLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode",
  "n8 (UNSPSC)", "OPCIONAL (anexo: 1 dentro de 0..1)", "REG-027", f"{L}#/properties/codigoProductoSunat", OP_EMIT, "CU-01; CU-13", "— (brecha)",
  "items[].codigo_producto_sunat")
r("MT-072", "a", 10, "Valor unitario del ítem", "02", f"{INV}/cac:InvoiceLine/cac:Price/cbc:PriceAmount", "n(12,10)", "OBLIGATORIO (anexo: 1 dentro de 0..1)",
  "REG-060; REG-067", f"{L}#/properties/valorUnitario", OP_EMIT, "CU-01", "—", "items[].valor_unitario")

# ---------------- b) BOLETA (solo diferencias con la factura) ----------------
r("MT-080", "b", 11, "Versión del UBL (boleta)", "—", f"{INV}/cbc:UBLVersionID", 'an..10, valor "2.0"', "OBLIGATORIO (anexo: 0..1, valor fijo)", "REG-001",
  "interno (parámetro del generador UBL)", OP_EMIT, "CU-01", obs="DISC-12.")
r("MT-081", "b", 11, "Versión de la estructura (boleta)", "—", f"{INV}/cbc:CustomizationID", 'an..10, valor "1.0"', "OBLIGATORIO (anexo: 0..1, valor fijo)",
  "REG-002", "interno (parámetro del generador UBL)", OP_EMIT, "CU-01", obs="DISC-12.")
r("MT-082", "b", 11, "Código de tipo de documento (boleta)", "01", f"{INV}/cbc:InvoiceTypeCode", 'valor "02" (anexo)', "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-010", f"{C}#/properties/tipoComprobante", OP_EMIT, "CU-01", "—", "tipo_de_comprobante = 2 (propio)", "DISC-04: el catálogo 01 dice 03.")
r("MT-083", "b", 11, "Serie y número (boleta)", "—", f"{INV}/cbc:ID", "F###-NNNNNNNN (anexo)", "OBLIGATORIO (anexo: 1)", "REG-031",
  f"{C}#/properties/serie + /correlativo", OP_EMIT, "CU-01; CU-07", "—", "serie (empieza con B)", "DISC-13: el anexo dice F### para la boleta.")
r("MT-084", "b", 13, "Número de documento del adquirente (boleta)", "06", f"{INV}/{CUS}/cac:PartyTaxScheme/cbc:CompanyID", "n11 (anexo)",
  "CONDICIONAL (anexo: 0..1)", "REG-043; REG-045", f"{A}#/properties/numeroDocumento", OP_EMIT, "CU-01", "—", "cliente_numero_de_documento",
  "Rotulado 'RUC del adquirente'; en la boleta puede ser DNI o 'VARIOS' (ENT-06): PENDIENTE.")
r("MT-086", "b", 13, "Ubigeo del domicilio del emisor (el anexo lo rotula 'Código del domicilio fiscal o de local anexo del emisor')", "13",
  f"{INV}/{SUP}/cac:PostalAddress/cbc:AddressTypeCode", "n6 (anexo), Catálogo 13 (ubigeo)", "CONDICIONAL (anexo: 0..1)", "REG-038",
  f"{E}#/properties/domicilioFiscal/properties/ubigeo", OP_EMIT, "CU-01", "— (el legado no tiene direcciones)", "— (Nubefact lo toma de 'Locales y Series': UBIGEO INEI, ENT-06 §6)",
  "DISC-24: el mismo nodo cbc:AddressTypeCode es n4 (código de establecimiento, MT-025) en RegistrationAddress, pero aquí es n6/Catálogo 13 (formato de ubigeo) en PostalAddress. La factura (págs. 1-10) no trae esta fila. Catálogo 13 PENDIENTE (P-11).")
r("MT-085", "b", 17, "Código de tipo de sistema de ISC (boleta)", "08", f"{INV}/cac:InvoiceLine/{TC}/cbc:TierRange", "an2", "CONDICIONAL (anexo: 0..1)",
  "REG-017", f"{L}#/properties/isc/properties/sistemaCalculo", OP_EMIT, "CU-01")

# ---------------- c) NOTA DE CRÉDITO ----------------
CN = "/CreditNote"
r("MT-090", "c", 19, "Firma digital (NC)", "—", f"{CN}/{FIRMA}", "XMLDSig", "OBLIGATORIO (anexo: 1)", "REG-090", f"{N}#/properties/firma", OP_NC, "CU-03")
r("MT-091", "c", 19, "Versión del UBL (NC)", "—", f"{CN}/cbc:UBLVersionID", 'valor "2.0"', "OBLIGATORIO (anexo: 0..1, valor fijo)", "REG-001",
  "interno (parámetro del generador UBL)", OP_NC, "CU-03", obs="DISC-12.")
r("MT-092", "c", 19, "Versión de la estructura (NC)", "—", f"{CN}/cbc:CustomizationID", 'valor "1.0"', "OBLIGATORIO (anexo: 0..1, valor fijo)", "REG-002",
  "interno (parámetro del generador UBL)", OP_NC, "CU-03", obs="DISC-12.")
r("MT-093", "c", 19, "Serie y número de la NC", "—", f"{CN}/cbc:ID", "F###-NNNNNNNN", "OBLIGATORIO (anexo: 1)", "REG-030; REG-032",
  f"{N}#/properties/serie + /correlativo", OP_NC, "CU-03; CU-07", "—", "serie + numero")
r("MT-094", "c", 19, "Fecha de emisión (NC)", "—", f"{CN}/cbc:IssueDate", "yyyy-mm-dd", "OBLIGATORIO (anexo: 1)", "REG-080",
  f"{N}#/properties/fechaEmision", OP_NC, "CU-03", "—", "fecha_de_emision")
r("MT-095", "c", 19, "Moneda (NC)", "02", f"{CN}/cbc:DocumentCurrencyCode", "an3", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-011; REG-069",
  f"{N}#/properties/moneda", OP_NC, "CU-03", "—", "moneda")
r("MT-096", "c", 19, "Serie y número del comprobante afectado", "—", f"{CN}/cac:DiscrepancyResponse/cbc:ReferenceID", "NNNN-NNNNNNNN / F###-NNNNNNNN",
  "OBLIGATORIO (anexo: 1 dentro de 0..n)", "REG-070; REG-071", f"{N}#/properties/documentoAfectado", OP_NC, "CU-03", "—",
  "documento_que_se_modifica_serie + _numero")
r("MT-097", "c", 19, "Código de tipo de nota de crédito", "09", f"{CN}/cac:DiscrepancyResponse/cbc:ResponseCode", "n2",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-018", f"{N}#/properties/motivo/properties/codigo", OP_NC, "CU-03", "—",
  "tipo_de_nota_de_credito (entero propio)")
r("MT-098", "c", 19, "Motivo o sustento", "—", f"{CN}/cac:DiscrepancyResponse/cbc:Description", "an..250", "OBLIGATORIO en contrato (anexo: 0..n)", "REG-074",
  f"{N}#/properties/motivo/properties/descripcion", OP_NC, "CU-03", "—", "observaciones")
r("MT-099", "c", 19, "Serie y número del comprobante que modifica", "—", f"{CN}/cac:BillingReference/cac:CreditNoteDocumentReference/cbc:ID",
  "NNNN-NNNNNNNN / F###-NNNNNNNN", "OBLIGATORIO (anexo: 1 dentro de 0..n)", "REG-070; REG-072", f"{N}#/properties/documentoAfectado",
  OP_NC, "CU-03", "—", "documento_que_se_modifica_serie + _numero", "DISC-11: semánticamente es InvoiceDocumentReference.")
r("MT-100", "c", 19, "Tipo de comprobante que modifica", "01", f"{CN}/cac:BillingReference/cac:CreditNoteDocumentReference/cbc:DocumentTypeCode",
  "n2", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-010; REG-070", f"{N}#/properties/documentoAfectado/properties/tipo", OP_NC, "CU-03", "—",
  "documento_que_se_modifica_tipo (1-2, propio)")
r("MT-101", "c", 20, "RUC del emisor (NC)", "—", f"{CN}/{SUP}/cac:PartyTaxScheme/cbc:CompanyID", "n11", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-040; REG-041",
  f"{E}#/properties/ruc", OP_NC, "CU-03")
r("MT-102", "c", 20, "Número de documento del adquirente (NC)", "06", f"{CN}/{CUS}/cac:PartyTaxScheme/cbc:CompanyID", "n11",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-073", f"{A}#/properties/numeroDocumento", OP_NC, "CU-03", obs="Debe coincidir con el documento afectado (REG-073).")
r("MT-103", "c", 20, "Código de tributo (NC)", "05", f"{CN}/{TC}/cac:TaxScheme/cbc:ID", "an4", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-014",
  f"{TR}#/properties/codigoTributo", OP_NC, "CU-03", obs="DISC-05: an4 en la NC frente a an..3 en la factura.")
r("MT-104", "c", 21, "Importe total (NC)", "02", f"{CN}/cac:LegalMonetaryTotal/cbc:PayableAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)", "REG-066; REG-073",
  f"{T}#/properties/importeTotal", OP_NC, "CU-03", "—", "total")
r("MT-105", "c", 21, "Número de orden del ítem (NC)", "—", f"{CN}/cac:CreditNoteLine/cbc:ID", "n..3", "OBLIGATORIO (anexo: 1)", "REG-005",
  f"{L}#/properties/numeroOrden", OP_NC, "CU-03")
r("MT-106", "c", 21, "Cantidad de unidades del ítem (NC)", "—", f"{CN}/cac:CreditNoteLine/cbc:CreditedQuantity", "n(12,10)",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-067", f"{L}#/properties/cantidad", OP_NC, "CU-03", "ingreso (devolución)", "items[].cantidad")
r("MT-107", "c", 22, "Afectación del IGV (NC)", "07", f"{CN}/cac:CreditNoteLine/{TC}/cbc:TaxExemptionReasonCode", "an2", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-016", f"{L}#/properties/afectacionIgv", OP_NC, "CU-03")
r("MT-108", "c", 22, "Sistema de ISC (NC)", "08", f"{CN}/cac:CreditNoteLine/{TC}/cbc:TierRange", "an2", "CONDICIONAL (anexo: 0..1)", "REG-017",
  f"{L}#/properties/isc/properties/sistemaCalculo", OP_NC, "CU-03", obs="DISC-02 cerrada: con -layout parecía an4/Cat. 05 (artefacto de extracción).")
r("MT-109", "c", 22, "Código de producto SUNAT (NC)", "—", f"{CN}/cac:CreditNoteLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode",
  "n8", "OPCIONAL (anexo: 1 dentro de 0..1)", "REG-027", f"{L}#/properties/codigoProductoSunat", OP_NC, "CU-03",
  obs="DISC-07: el anexo escribe cac:CreditLine (no existe en el XSD).")
r("MT-110", "c", 22, "Valor unitario del ítem (NC)", "02", f"{CN}/cac:CreditNoteLine/cac:Price/cbc:PriceAmount", "n(12,10)", "OBLIGATORIO (anexo: 1)",
  "REG-067", f"{L}#/properties/valorUnitario", OP_NC, "CU-03")

# ---------------- d) NOTA DE DÉBITO ----------------
DN = "/DebitNote"
r("MT-120", "d", 23, "Versión del UBL (ND)", "—", f"{DN}/cbc:UBLVersionID", 'valor "2.0"', "OBLIGATORIO (anexo: 0..1, valor fijo)", "REG-001",
  "interno (parámetro del generador UBL)", OP_ND, "CU-04", obs="DISC-12.")
r("MT-121", "d", 23, "Versión de la estructura (ND)", "—", f"{DN}/cbc:CustomizationID", 'valor "1.0"', "OBLIGATORIO (anexo: 0..1, valor fijo)", "REG-002",
  "interno (parámetro del generador UBL)", OP_ND, "CU-04", obs="DISC-12.")
r("MT-122", "d", 23, "Tipo de operación (ND)", "—", f"{DN}/cbc:ProfileID", "sin formato ni catálogo en el anexo", "OPCIONAL (anexo: 0..1)", "REG-021",
  f"{N}#/properties/tipoOperacion", OP_ND, "CU-04", obs="DISC-17: la ND lo lista sin catálogo; la NC no lo lista.")
r("MT-123", "d", 23, "Serie y número de la ND", "—", f"{DN}/cbc:ID", "F###-NNNNNNNN", "OBLIGATORIO (anexo: 1)", "REG-030; REG-032",
  f"{N}#/properties/serie + /correlativo", OP_ND, "CU-04; CU-07", "—", "serie + numero")
r("MT-124", "d", 23, "Serie y número del comprobante afectado (ND)", "—", f"{DN}/cac:DiscrepancyResponse/cbc:ReferenceID", "NNNN-NNNNNNNN / F###-NNNNNNNN",
  "OBLIGATORIO (anexo: 1 dentro de 0..n)", "REG-070", f"{N}#/properties/documentoAfectado", OP_ND, "CU-04", "—", "documento_que_se_modifica_serie + _numero")
r("MT-125", "d", 23, "Código de tipo de nota de débito", "10", f"{DN}/cac:DiscrepancyResponse/cbc:ResponseCode", "n2", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-019", f"{N}#/properties/motivo/properties/codigo", OP_ND, "CU-04", "—", "tipo_de_nota_de_debito (entero propio)",
  "La numeración de Nubefact no coincide con el catálogo 10 (DISC-15).")
r("MT-126", "d", 23, "Motivo o sustento (ND)", "—", f"{DN}/cac:DiscrepancyResponse/cbc:Description", "an..250", "OBLIGATORIO en contrato (anexo: 0..n)", "REG-074",
  f"{N}#/properties/motivo/properties/descripcion", OP_ND, "CU-04")
r("MT-127", "d", 23, "Serie y número del comprobante que modifica (ND)", "—", f"{DN}/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID",
  "NNNN-NNNNNNNN / F###-NNNNNNNN", "OBLIGATORIO (anexo: 1 dentro de 0..n)", "REG-070; REG-072", f"{N}#/properties/documentoAfectado", OP_ND, "CU-04", "—",
  "documento_que_se_modifica_serie + _numero", "DISC-08: el anexo escribe cac:DebitDocumentReference (no existe en el XSD); se usa InvoiceDocumentReference (PENDIENTE).")
r("MT-128", "d", 23, "Tipo de comprobante que modifica (ND)", "01", f"{DN}/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode", "n2",
  "OBLIGATORIO en contrato (anexo: 0..1)", "REG-010; REG-070", f"{N}#/properties/documentoAfectado/properties/tipo", OP_ND, "CU-04", "—", "documento_que_se_modifica_tipo")
r("MT-129", "d", 24, "RUC del emisor (ND)", "—", f"{DN}/{SUP}/cac:PartyTaxScheme/cbc:CompanyID", "n11", "OBLIGATORIO en contrato (anexo: 0..1)", "REG-040; REG-041",
  f"{E}#/properties/ruc", OP_ND, "CU-04")
r("MT-130", "d", 26, "Importe total (ND)", "02", f"{DN}/cac:RequestedMonetaryTotal/cbc:PayableAmount", "n(12,2)", "OBLIGATORIO (anexo: 1)", "REG-066",
  f"{T}#/properties/importeTotal", OP_ND, "CU-04", "—", "total", "La ND usa RequestedMonetaryTotal (no LegalMonetaryTotal).")
r("MT-131", "d", 26, "Cantidad de unidades del ítem (ND)", "—", f"{DN}/cac:DebitNoteLine/cbc:DebitedQuantity", "n(12,10)", "OBLIGATORIO en contrato (anexo: 0..1)",
  "REG-067", f"{L}#/properties/cantidad", OP_ND, "CU-04")
r("MT-132", "d", 26, "Sistema de ISC (ND)", "08", f"{DN}/cac:DebitNoteLine/{TC}/cbc:TierRange", "an2", "CONDICIONAL (anexo: 0..1)", "REG-017",
  f"{L}#/properties/isc/properties/sistemaCalculo", OP_ND, "CU-04")
r("MT-133", "d", 27, "Código de producto SUNAT (ND)", "—", f"{DN}/cac:DebitNoteLine/cac:Item/cac:CommodityClassification/cbc:ItemClassificationCode", "n8",
  "OPCIONAL (anexo: 1 dentro de 0..1)", "REG-027", f"{L}#/properties/codigoProductoSunat", OP_ND, "CU-04",
  obs="DISC-07: el anexo escribe cac:DebitLine en AdditionalItemProperty (pág. 27).")

# ---------------- E) RESUMEN DIARIO (sin XSD) ----------------
SD = "/SummaryDocuments"
SL = f"{SD}/sac:SummaryDocumentsLine"
for id_, pag, dato, cat, xp, tipo, oblig, regla, dto in [
    ("MT-140", 28, "Versión del UBL (RC)", "—", f"{SD}/cbc:UBLVersionID", "an..10", "M", "REG-001", "interno"),
    ("MT-141", 28, "Versión de la estructura (RC)", "—", f"{SD}/cbc:CustomizationID", "an..10", "M", "REG-002", "interno"),
    ("MT-142", 28, "Identificador del resumen", "—", f"{SD}/cbc:ID", "an..17, RC-<Fecha>-#####", "M", "REG-120", f"{RC}#/properties/identificador"),
    ("MT-143", 28, "Fecha de generación del resumen", "—", f"{SD}/cbc:IssueDate", "YYYY-MM-DD", "M", "REG-122", f"{RC}#/properties/fechaGeneracion"),
    ("MT-144", 28, "Fecha de emisión de los documentos", "—", f"{SD}/cbc:ReferenceDate", "YYYY-MM-DD", "M", "REG-122", f"{RC}#/properties/fechaReferencia"),
    ("MT-145", 28, "Firma digital (RC)", "—", f"{SD}/{FIRMA}", "an..3000", "M", "REG-090", f"{RC}#/properties/firma"),
    ("MT-146", 28, "Número de RUC del emisor (RC)", "—", f"{SD}/cac:AccountingSupplierParty/cbc:CustomerAssignedAccountID", "n11", "M", "REG-040", f"{E}#/properties/ruc"),
    ("MT-147", 28, "Tipo de documento del emisor (RC)", "06", f"{SD}/cac:AccountingSupplierParty/cbc:AdditionalAccountID", "n1", "M", "REG-015", "interno (constante \"6\")"),
    ("MT-148", 28, "Razón social del emisor (RC)", "—", f"{SD}/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", "an..100", "M", "REG-100", f"{E}#/properties/razonSocial"),
    ("MT-149", 28, "Número de fila", "—", f"{SL}/cbc:LineID", "n..5", "M", "REG-121", f"{RC}#/properties/items/items/properties/linea"),
    ("MT-150", 28, "Serie y número del documento", "—", f"{SL}/cbc:ID", "an..13", "M", "REG-120", f"{RC}#/properties/items/items/properties/serieNumero"),
    ("MT-151", 28, "Tipo de documento", "01", f"{SL}/cbc:DocumentTypeCode", "an2", "M", "REG-010", f"{RC}#/properties/items/items/properties/tipoComprobante"),
    ("MT-152", 28, "Número de documento del adquirente", "—", f"{SL}/cac:AccountingCustomerParty/cbc:CustomerAssignedAccountID", "an20", "M", "REG-043", f"{RC}#/properties/items/items/properties/adquirente"),
    ("MT-153", 28, "Tipo de documento del adquirente", "06", f"{SL}/cac:AccountingCustomerParty/cbc:AdditionalAccountID", "n1", "M", "REG-015", f"{RC}#/properties/items/items/properties/adquirente"),
    ("MT-154", 28, "Boleta que modifica (serie-número)", "—", f"{SL}/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID", "an..13", "C", "REG-070", f"{RC}#/properties/items/items/properties/documentoModificado"),
    ("MT-155", 28, "Tipo de documento que modifica", "01", f"{SL}/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode", "an2", "C", "REG-010", f"{RC}#/properties/items/items/properties/documentoModificado"),
    ("MT-156", 29, "Estado del ítem", "19", f"{SL}/cac:Status/cbc:ConditionCode", "n1", "M", "REG-123", f"{RC}#/properties/items/items/properties/estadoItem"),
    ("MT-157", 29, "Importe total del ítem", "02", f"{SL}/sac:TotalAmount", "n(12,2)", "M", "REG-066", f"{RC}#/properties/items/items/properties/importeTotal"),
    ("MT-158", 29, "Totales por tipo de valor de venta (gravadas, exoneradas, inafectas, gratuitas)", "11", f"{SL}/sac:BillingPayment/cbc:PaidAmount", "n(12,2)", "M/C", "REG-124", f"{RC}#/properties/items/items/properties/totalesPorTipo"),
    ("MT-159", 29, "Código de tipo de valor de venta", "11", f"{SL}/sac:BillingPayment/cbc:InstructionID", "an2", "M", "REG-124", f"{RC}#/properties/items/items/properties/totalesPorTipo"),
    ("MT-160", 29, "Otros cargos del ítem", "—", f"{SL}/cac:AllowanceCharge/cbc:Amount", "n(12,2)", "M", "REG-064", f"{RC}#/properties/items/items/properties/otrosCargos"),
    ("MT-161", 29, "Total ISC, IGV y otros tributos del ítem", "05", f"{SL}/cac:TaxTotal/cbc:TaxAmount", "n(12,2)", "M/C", "REG-057", f"{RC}#/properties/items/items/properties/tributos"),
]:
    r(id_, "E", pag, dato, cat, xp, tipo, f"{'OBLIGATORIO' if oblig == 'M' else 'CONDICIONAL'} (anexo: {oblig})", regla, dto, OP_RC, "CU-06",
      obs="Sin XSD SUNAT en el workspace (ENT-08)." + (" DISC-09: el anexo cita el Catálogo 11 como 'afectación de IGV'." if cat == "11" else "")
      + (" Catálogo 19 PENDIENTE." if cat == "19" else ""))

# ---------------- F) COMUNICACIÓN DE BAJA (sin XSD) ----------------
VD = "/VoidedDocuments"
VL = f"{VD}/sac:VoidedDocumentsLine"
for id_, dato, cat, xp, tipo, regla, dto in [
    ("MT-170", "Versión del UBL (RA)", "—", f"{VD}/cbc:UBLVersionID", "an..10", "REG-001", "interno"),
    ("MT-171", "Versión de la estructura (RA)", "—", f"{VD}/cbc:CustomizationID", "an..10", "REG-002", "interno"),
    ("MT-172", "Identificador de la comunicación", "—", f"{VD}/cbc:ID", "an..17, RA-<Fecha>-#####", "REG-121", f"{RA}#/properties/identificador"),
    ("MT-173", "Fecha de generación de la comunicación", "—", f"{VD}/cbc:IssueDate", "YYYY-MM-DD", "REG-122", f"{RA}#/properties/fechaGeneracion"),
    ("MT-174", "Fecha de generación del documento dado de baja", "—", f"{VD}/cbc:ReferenceDate", "YYYY-MM-DD", "REG-122", f"{RA}#/properties/fechaReferencia"),
    ("MT-175", "Firma digital (RA)", "—", f"{VD}/{FIRMA}", "an..3000", "REG-090", f"{RA}#/properties/firma"),
    ("MT-176", "Número de RUC del emisor (RA)", "—", f"{VD}/cac:AccountingSupplierParty/cbc:CustomerAssignedAccountID", "n11", "REG-040", f"{E}#/properties/ruc"),
    ("MT-177", "Tipo de documento del emisor (RA)", "06", f"{VD}/cac:AccountingSupplierParty/cbc:AdditionalAccountID", "n1", "REG-015", "interno (constante \"6\")"),
    ("MT-178", "Razón social del emisor (RA)", "—", f"{VD}/cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName", "an..100", "REG-100", f"{E}#/properties/razonSocial"),
    ("MT-179", "Número de ítem", "—", f"{VL}/cbc:LineID", "n..5", "REG-124", f"{RA}#/properties/items/items/properties/linea"),
    ("MT-180", "Tipo de documento dado de baja", "01", f"{VL}/cbc:DocumentTypeCode", "an2", "REG-010", f"{RA}#/properties/items/items/properties/tipoComprobante"),
    ("MT-181", "Serie del documento dado de baja", "—", f"{VL}/sac:DocumentSerialID", "an4", "REG-124", f"{RA}#/properties/items/items/properties/serie"),
    ("MT-182", "Correlativo del documento dado de baja", "—", f"{VL}/sac:DocumentNumberID", "n..8", "REG-124", f"{RA}#/properties/items/items/properties/correlativo"),
    ("MT-183", "Motivo de baja", "—", f"{VL}/sac:VoidReasonDescription", "an..100", "REG-124", f"{RA}#/properties/items/items/properties/motivo"),
]:
    r(id_, "F", 31, dato, cat, xp, tipo, "OBLIGATORIO (anexo: M)", regla, dto, OP_RA, "CU-05", "—",
      "motivo" if "Motivo" in dato else ("serie" if "Serie" in dato else ("numero" if "Correlativo" in dato else "—")),
      "Sin XSD SUNAT en el workspace (ENT-08).")

# ---------------- PENDIENTE: datos posteriores al Anexo 9-A (ENT-04) ----------------
PEND = "PENDIENTE (RS 114-2019 / 150-2019 / 193-2020 no disponibles)"
for id_, dato, cat, xp, regla, dto, nube in [
    ("MT-190", "ICBPER: monto del impuesto por línea", "05", f"{INV}/cac:InvoiceLine/{TS}/cbc:TaxAmount", "REG-054", f"{L}#/properties/icbper/properties/monto", "items[].impuesto_bolsas"),
    ("MT-191", "ICBPER: cantidad de bolsas", "—", f"{INV}/cac:InvoiceLine/{TS}/cbc:BaseUnitMeasure", "REG-054", f"{L}#/properties/icbper/properties/cantidadBolsas", "—"),
    ("MT-192", "ICBPER: monto unitario por bolsa", "—", f"{INV}/cac:InvoiceLine/{TS}/cbc:PerUnitAmount", "REG-054", f"{L}#/properties/icbper/properties/montoUnitario", "—"),
    ("MT-193", "Forma de pago (contado o crédito)", "—", f"{INV}/cac:PaymentTerms/cbc:PaymentMeansID", "REG-028", f"{FP}#/properties/tipo", "medio_de_pago / venta_al_credito"),
    ("MT-194", "Monto neto pendiente de pago", "02", f"{INV}/cac:PaymentTerms/cbc:Amount", "REG-028", f"{FP}#/properties/montoPendiente", "—"),
    ("MT-195", "Identificador de cuota", "—", f"{INV}/cac:PaymentTerms/cbc:ID", "REG-029", f"{FP}#/properties/cuotas/items/properties/numero", "venta_al_credito[].cuota"),
    ("MT-196", "Fecha de vencimiento de la cuota", "—", f"{INV}/cac:PaymentTerms/cbc:PaymentDueDate", "REG-029", f"{FP}#/properties/cuotas/items/properties/fechaVencimiento", "venta_al_credito[].fecha_de_pago"),
]:
    r(id_, "a", "—", dato, cat, xp, "PENDIENTE", "CONDICIONAL (PENDIENTE de norma)", regla, dto, OP_EMIT, "CU-01", "—", nube,
      "XPath confirmado por la validación SUNAT vigente (XSL 2022). Falta el texto de los anexos 2019-2020 (DISC-14).")
    FILAS[-1]["norma_anexo_pagina"] = PEND


# ---------------- Validación SUNAT vigente (XSL 06/09/2022) ----------------
XSL = "Validación SUNAT: Git/XSL Actualizado al 06092022 (1)/validaciones"
XSL_POR_ID = {"MT-087": "ValidaExprRegFactura-2.0.1.xsl"}
r("MT-087", "a", "—", "Código de tipo de operación (ubicación vigente)", "51", f"{INV}/cbc:InvoiceTypeCode/@listID", "n4 (catálogo 51)",
  "OBLIGATORIO (XSL: catálogo 51, error 3206)", "REG-021; REG-023", f"{C}#/properties/tipoOperacion", OP_EMIT, "CU-01", "—", "sunat_transaction (entero propio)",
  "La validación SUNAT vigente lee el tipo de operación de InvoiceTypeCode/@listID (ValidaExprRegFactura-2.0.1.xsl, líneas 107 y 911) y NO valida cbc:ProfileID. Resuelve DISC-01 y DISC-06.")
FILAS[-1]["norma_anexo_pagina"] = f"{XSL}/ValidaExprRegFactura-2.0.1.xsl (líneas 107, 911); ValidaExprRegBoleta-2.0.1.xsl (línea 92)"

# Correcciones a filas transcritas del Anexo 9-A (2017) según la validación vigente. El valor del anexo queda en 'observaciones'.
CORRECCIONES_XSL = {
    "MT-004": {"obligatoriedad": "REEMPLAZADO (XSL 2022 no valida ProfileID; ver MT-087)"},
    "MT-005": {"obligatoriedad": "REEMPLAZADO (ver MT-087)"},
    "MT-080": {"tipo_longitud": 'valor "2.1" (XSL; el anexo decía "2.0")'},
    "MT-081": {"tipo_longitud": 'valor "2.0" (XSL; el anexo decía "1.0")'},
    "MT-091": {"tipo_longitud": 'valor "2.1" (XSL; el anexo decía "2.0")'},
    "MT-092": {"tipo_longitud": 'valor "2.0" (XSL; el anexo decía "1.0")'},
    "MT-120": {"tipo_longitud": 'valor "2.1" (XSL; el anexo decía "2.0")'},
    "MT-121": {"tipo_longitud": 'valor "2.0" (XSL; el anexo decía "1.0")'},
    "MT-140": {"tipo_longitud": 'an..10, valor "2.0" (XSL ValidaExprRegSummary-1.1.0)'},
    "MT-141": {"tipo_longitud": 'an..10, valor "1.1" (XSL ValidaExprRegSummary-1.1.0)'},
    "MT-170": {"tipo_longitud": 'an..10, valor "2.0" (XSL ValidaExprRegSummaryVoided-1.0.1)'},
    "MT-171": {"tipo_longitud": 'an..10, valor "1.0" (XSL ValidaExprRegSummaryVoided-1.0.1)'},
    "MT-099": {"xpath_ubl": f"{CN}/cac:BillingReference/cac:InvoiceDocumentReference/cbc:ID",
               "_obs": "XSL ValidaExprRegNC-2.0.1 (líneas 20, 118) usa InvoiceDocumentReference; el anexo (pág. 19) decía CreditNoteDocumentReference. DISC-11 cerrada."},
    "MT-100": {"xpath_ubl": f"{CN}/cac:BillingReference/cac:InvoiceDocumentReference/cbc:DocumentTypeCode",
               "_obs": "Ídem MT-099 (DISC-11 cerrada)."},
    "MT-127": {"_obs": "Confirmado por XSL ValidaExprRegND-2.0.1 (líneas 19, 78): InvoiceDocumentReference. DISC-08 cerrada."},
    "MT-192": {"xpath_ubl": f"{INV}/cac:InvoiceLine/{TC}/cbc:PerUnitAmount",
               "_obs": "Corregido según XSL (Factura línea 3734: cac:TaxCategory/cbc:PerUnitAmount); el candidato anterior era TaxSubtotal/cbc:PerUnitAmount."},
}
XSL_FILAS_POST2019 = {
    "MT-190": "Factura líneas 3725-3800 (ICBPER, errores 3237, 2892, 4318, 4320)",
    "MT-191": "Factura línea 3733 (cbc:BaseUnitMeasure, error 2892)",
    "MT-192": "Factura línea 3734 (cac:TaxCategory/cbc:PerUnitAmount, errores 2892, 3238)",
    "MT-193": "Factura líneas 41, 524, 1011-1020 (PaymentTerms ID='FormaPago', PaymentMeansID Contado/Credito)",
    "MT-194": "Factura líneas 1063-1071 (monto neto pendiente = Amount de 'Credito')",
    "MT-195": "Factura líneas 1064-1067 (PaymentMeansID 'Cuota###')",
    "MT-196": "Factura (PaymentDueDate de las cuotas)",
}
for id_, ref in XSL_FILAS_POST2019.items():
    CORRECCIONES_XSL.setdefault(id_, {})
    CORRECCIONES_XSL[id_]["norma_anexo_pagina"] = f"{XSL}/ValidaExprRegFactura-2.0.1.xsl: {ref}. Anexos 2019-2020: PENDIENTE"
    CORRECCIONES_XSL[id_]["obligatoriedad"] = "CONDICIONAL (validado por SUNAT, XSL 2022)"
    CORRECCIONES_XSL[id_]["tipo_longitud"] = "ver XSL"

PART_E = f"{INV}/cac:AccountingSupplierParty/cac:Party"
PART_A = f"{INV}/cac:AccountingCustomerParty/cac:Party"
for id_, dato, cat, xp, tipo, regla, dto, legado, nube, reemplaza in [
    ("MT-073", "Número de RUC del emisor (estructura vigente)", "—", f"{PART_E}/cac:PartyIdentification/cbc:ID", "n11", "REG-040; REG-041", f"{E}#/properties/ruc", "—", "— (cuenta del proveedor)", "MT-023"),
    ("MT-074", "Tipo de documento del emisor (estructura vigente)", "06", f"{PART_E}/cac:PartyIdentification/cbc:ID/@schemeID", 'an1, valor "6"', "REG-015; REG-042", "interno (constante \"6\")", "—", "—", "MT-024"),
    ("MT-075", "Razón social del emisor (estructura vigente)", "—", f"{PART_E}/cac:PartyLegalEntity/cbc:RegistrationName", "an..100", "REG-100", f"{E}#/properties/razonSocial", "—", "—", "MT-022"),
    ("MT-076", "Código del establecimiento anexo (estructura vigente)", "—", f"{PART_E}/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:AddressTypeCode", "n4", "REG-036", f"{C}#/properties/establecimientoCodigo", "parámetro `establecimiento` del lote", "— (Locales y Series)", "MT-025"),
    ("MT-077", "Ubigeo del domicilio del emisor (estructura vigente)", "13", f"{PART_E}/cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID", "n6 (Catálogo 13)", "REG-038", f"{E}#/properties/domicilioFiscal/properties/ubigeo", "—", "— (UBIGEO INEI del local)", "MT-086"),
    ("MT-078", "Número de documento del adquirente (estructura vigente)", "—", f"{PART_A}/cac:PartyIdentification/cbc:ID", "an..15", "REG-040; REG-043; REG-044", f"{A}#/properties/numeroDocumento", "—", "cliente_numero_de_documento", "MT-027"),
    ("MT-079", "Tipo de documento del adquirente (estructura vigente)", "06", f"{PART_A}/cac:PartyIdentification/cbc:ID/@schemeID", "an1", "REG-015; REG-042; REG-043", f"{A}#/properties/tipoDocumento", "—", "cliente_tipo_de_documento", "MT-028"),
    ("MT-088", "Razón social del adquirente (estructura vigente)", "—", f"{PART_A}/cac:PartyLegalEntity/cbc:RegistrationName", "an..100", "REG-100", f"{A}#/properties/razonSocial", "—", "cliente_denominacion", "MT-026"),
]:
    r(id_, "a", "—", dato, cat, xp, tipo, "OBLIGATORIO (validado por SUNAT, XSL 2022)", regla, dto, OP_EMIT, "CU-01", legado, nube,
      f"Reemplaza a {reemplaza} (Anexo 9-A 2017: PartyTaxScheme / PostalAddress). La validación SUNAT vigente usa PartyIdentification y PartyLegalEntity (DISC-25). Aplica igual en /CreditNote y /DebitNote.")
    FILAS[-1]["norma_anexo_pagina"] = f"{XSL}/ValidaExprRegFactura-2.0.1.xsl y ValidaExprRegBoleta-2.0.1.xsl (templates cac:AccountingSupplierParty / cac:AccountingCustomerParty)"
    CORRECCIONES_XSL.setdefault(reemplaza, {})["obligatoriedad"] = f"REEMPLAZADO (estructura 2017; vigente: {id_})"
for viejo, nuevo in [("MT-084", "MT-078"), ("MT-101", "MT-073"), ("MT-102", "MT-078"), ("MT-129", "MT-073")]:
    CORRECCIONES_XSL.setdefault(viejo, {})["obligatoriedad"] = f"REEMPLAZADO (estructura 2017; vigente: {nuevo}, misma ruta bajo la raíz de la nota)"
XSL_POR_ID.update({k: "ValidaExprRegFactura-2.0.1.xsl" for k in ("MT-073", "MT-074", "MT-075", "MT-076", "MT-077", "MT-078", "MT-079", "MT-088")})

for f in FILAS:
    for campo, valor in CORRECCIONES_XSL.get(f["id"], {}).items():
        if campo == "_obs":
            f["observaciones"] = (f["observaciones"] + " " + valor).strip()
        else:
            f[campo] = valor

# ---------------- Fuera de alcance de la Fase 1 (agrupado) ----------------
for id_, pag, dato, xp in [
    ("MT-197", 2, "Servicios públicos (RRSSPP): ciclo de facturación y suministro", f"{INV}/cac:InvoicePeriod"),
    ("MT-198", "4-5", "Factura-guía: datos de traslado y transporte", f"{INV}/cac:Delivery/cac:Shipment"),
    ("MT-199", 6, "Detracción: cuenta del Banco de la Nación, bien sujeto, porcentaje y monto", f"{INV}/cac:PaymentMeans/cac:PayeeFinancialAccount"),
    ("MT-200", 6, "Anticipos: detalle por comprobante de anticipo", f"{INV}/cac:PrepaidPayment"),
    ("MT-201", "8-9", "Hospedaje, paquete turístico y transporte de pasajeros", f"{INV}/cac:InvoiceLine/cac:Delivery"),
    ("MT-202", 10, "Propiedades adicionales del ítem (Catálogo 55)", f"{INV}/cac:InvoiceLine/cac:Item/cac:AdditionalItemProperty"),
]:
    r(id_, "a", pag, dato, "—", xp, "agregado", "FUERA DE ALCANCE (Fase 1)", "—", "—", "—", "—",
      obs="Se anota para completar la cobertura del anexo; no se modela en la Fase 1.")
r("MT-203", "E", 28, "Percepción en el resumen diario", "—", f"{SL}/sac:SUNATPerceptionSummaryDocumentReference", "agregado", "FUERA DE ALCANCE (Fase 1)",
  "—", "—", "—", "—", obs="Sin XSD SUNAT en el workspace.")

DISCREPANCIAS = [
    ("DISC-01", "Anexo 9-A, págs. 1 y 11", "cbc:ProfileID: el dato dice 'Catálogo 51'", "Anexo 9-A, mismas págs.: @schemeURI termina en 'catalogo17'", "CERRADA", "CERRADA: la validación SUNAT vigente lee el tipo de operación de InvoiceTypeCode/@listID con el catálogo 51 (error 3206) y no valida ProfileID (MT-087)."),
    ("DISC-02", "Anexo 9-A, pág. 22 (extracción con -layout)", "TierRange de la NC: 1 / an4 / Catálogo 05", "Anexo 9-A, pág. 22 (extracción raw): 0..1 / an2 / Catálogo 08", "CERRADA", "Artefacto de la extracción del PDF; no es una discrepancia."),
    ("DISC-03", "Anexo 9-A (título): estándar UBL 2.1", "—", "Git/tradeshift-ubl-xsd: XSD UBL 2.2", "CERRADA", "Desde el 28/10, Git/UBL-2.1/xsd (OASIS UBL 2.1 OS, 2013) es el XSD principal. Las 127 rutas verificadas existen en 2.1 y en 2.2 con la misma cardinalidad (M11)."),
    ("DISC-04", "Anexo 9-A, pág. 11: boleta InvoiceTypeCode = \"02\"", "—", "Git/01.txt: boleta = '03'; '02' no existe", "CERRADA", "CERRADA: ValidaExprRegBoleta-2.0.1.xsl exige InvoiceTypeCode '^03$' (error 1003). El '02' del anexo es una errata."),
    ("DISC-05", "Anexo 9-A, págs. 7 y 10 (factura): TaxScheme/cbc:ID an..3, TaxTypeCode an4", "—", "Anexo 9-A, págs. 20, 25 y 29 (NC, ND, RC): ID an4, TaxTypeCode an3; Git/05.txt: códigos de 4 dígitos e internacionales de 3 letras", "ABIERTA", "Contrato: ID = 4 dígitos (catálogo 05), TaxTypeCode = 3 letras."),
    ("DISC-06", "Anexo 9-A, págs. 1 y 11: ProfileID an2", "—", "Git/51.txt: códigos de 4 dígitos (0101…)", "CERRADA", "CERRADA: el tipo de operación usa los 4 dígitos del catálogo 51 en InvoiceTypeCode/@listID (MT-087)."),
    ("DISC-07", "Anexo 9-A, pág. 22: /CreditNote/cac:CreditLine/…; pág. 27: /DebitNote/cac:DebitLine/…", "—", "XSD 2.1 (y 2.2): solo existen cac:CreditNoteLine y cac:DebitNoteLine", "ABIERTA", "Errata del anexo; la matriz usa CreditNoteLine y DebitNoteLine."),
    ("DISC-08", "Anexo 9-A, pág. 23: cac:BillingReference/cac:DebitDocumentReference", "—", "XSD 2.1 (y 2.2): BillingReferenceType no tiene DebitDocumentReference", "CERRADA", "CERRADA: ValidaExprRegND-2.0.1.xsl usa cac:BillingReference/cac:InvoiceDocumentReference (MT-127)."),
    ("DISC-09", "Anexo 9-A, pág. 29 (RC): InstructionID 'Tipo de Afectación de IGV - Catálogo No 11'", "—", "Anexo 9-A, pág. 10: la afectación del IGV usa el Catálogo 07", "ABIERTA", "El catálogo 11 no está en el workspace: PENDIENTE."),
    ("DISC-10", "Anexo 9-A, págs. 4 y 5: 'cac:cac:PartyLegalEntity' y 'cacPartyLegalEntity'", "—", "Sintaxis XPath", "ABIERTA", "Errata tipográfica; fuera de alcance (transporte)."),
    ("DISC-11", "Anexo 9-A, pág. 19: NC usa cac:CreditNoteDocumentReference para el comprobante que modifica", "—", "XSD 2.1 (y 2.2): también existe cac:InvoiceDocumentReference, semánticamente más adecuado", "CERRADA", "CERRADA: ValidaExprRegNC-2.0.1.xsl usa cac:BillingReference/cac:InvoiceDocumentReference (MT-099/MT-100 corregidas)."),
    ("DISC-12", "Anexo 9-A, pág. 1 (factura): UBLVersionID \"2.1\", CustomizationID \"2.0\"", "—", "Anexo 9-A, págs. 11, 19 y 23 (boleta, NC, ND): \"2.0\" y \"1.0\"", "CERRADA", "CERRADA: las XSL exigen UBLVersionID '2.1' y CustomizationID '2.0' en factura, boleta, NC y ND; '2.0'/'1.1' en el resumen diario y '2.0'/'1.0' en la baja."),
    ("DISC-13", "Anexo 9-A, pág. 11: serie de la boleta 'F###'", "—", "Git/observaciones-nubefact-demo.md §6 y manual Nubefact ('serie'): la boleta empieza con 'B'", "CERRADA", "CERRADA: ValidaExprRegBoleta-2.0.1.xsl valida la serie con '^([B][A-Z0-9]{3}|[0-9]{4})-[0-9]{1,8}$'; la factura usa F, y las notas F, B o S."),
    ("DISC-14", "Git/05.txt (7152 ICBPER) y Git/09.txt (código 13: cuotas)", "—", "Anexo 9-A (2017): no los contempla", "ABIERTA (parcial)", "La estructura del ICBPER (BaseUnitMeasure, TaxCategory/PerUnitAmount) y de las cuotas (PaymentTerms FormaPago/Credito/Cuota###) está confirmada por la validación SUNAT vigente (MT-190 a MT-196). Falta el texto normativo de los anexos 2019-2020 y la tasa vigente del ICBPER."),
    ("DISC-15", "Manual Nubefact: cliente_tipo_de_documento '-' (VARIOS); tipo_de_nota_de_debito 4 = IVAP", "—", "Git/06.txt no tiene '-'; Git/10.txt: IVAP = '12'", "ABIERTA", "Los códigos propios del proveedor se mapean solo en el adaptador (RNF-09)."),
    ("DISC-16", "Anexo 9-A, págs. 1, 11 y 19: IssueTime 'hh-mm-ss.0z'", "—", "Anexo 9-A, pág. 9: 'hh:mm:ss.0z'; XSD udt:TimeType (xsd:time) usa ':'", "ABIERTA", "Contrato: hh:mm:ss (REG-082)."),
    ("DISC-17", "Anexo 9-A, pág. 23: la ND lista ProfileID sin formato ni catálogo", "—", "Anexo 9-A, pág. 19: la NC no lista ProfileID", "ABIERTA", "Contrato: tipoOperacion opcional en las notas."),
    ("DISC-18", "Git/464918148-11-FORMATO-DE-KARDEX-SEGUN-SUNAT-xls.xls (nombre: 'kardex')", "Contenido: FORMATO 13.1 (inventario permanente valorizado)", "Alcance pedido: Formato 12.1 (unidades físicas)", "CERRADA", "Se resolvió al agregar Git/FORMATO_12_1.pdf (28/10), que es la fuente del 12.1. El 13.1 queda solo como referencia."),
    ("DISC-19", "Git/592044723-FORMATO-8-1.xlsx: 19 columnas (una base imponible, sin ISC ni ICBPER, con 'DIVISIONARIA')", "—", "Estructura PLE 8.1 (.xlsm): 42 campos", "ABIERTA", "El contrato sigue la estructura PLE (registro-compras-8-1.schema.yaml)."),
    ("DISC-20", "Git/234_formato141.pdf (RS 234-2006) = Git/registro ventas formato 14.1.xls: 22 columnas, sin ICBPER ni IVAP", "—", "Estructura PLE 14.1 (.xlsm): 35 campos, con ICBPER (23) e IVAP (21, 22)", "ABIERTA", "Son versiones distintas: el formato impreso de la RS 234-2006 y la estructura electrónica PLE posterior. El contrato sigue el PLE, que es un superconjunto. Confirmar la vigencia con SUNAT."),
    ("DISC-24", "Anexo 9-A, pág. 13 (boleta): /Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cbc:AddressTypeCode, n6, Catálogo 13 (ubigeo)", "—", "Anexo 9-A, págs. 3, 13, 20 y 24: el mismo cbc:AddressTypeCode en PartyTaxScheme/RegistrationAddress es n4 (código de establecimiento, MT-025)", "CERRADA", "CERRADA: el ubigeo vigente va en cac:PartyLegalEntity/cac:RegistrationAddress/cbc:ID (error 4093, MT-077). El AddressTypeCode n6 de la pág. 13 es una errata del anexo."),
    ("DISC-25", "Anexo 9-A (2017), págs. 3, 13, 20 y 24: emisor y adquirente en cac:PartyTaxScheme (CompanyID, RegistrationName, RegistrationAddress)", "—", "Validación SUNAT vigente (XSL 2022): cac:PartyIdentification/cbc:ID y cac:PartyLegalEntity (RegistrationName, RegistrationAddress/AddressTypeCode y cbc:ID)", "CERRADA", "El contrato sigue la estructura vigente (MT-073 a MT-079, MT-088). Las filas del anexo quedan como REEMPLAZADO para conservar la trazabilidad."),
    ("DISC-23", "Git/FORMATO_12_1.pdf, cabecera e: 'Código de la existencia (según Tabla 5)'", "—", "Git/…KARDEX…xls (13.1): 'CÓDIGO DE LA EXISTENCIA' y, aparte, 'TIPO (TABLA 5)'", "ABIERTA", "El contrato separa el código interno de la existencia; la Tabla 5 (tipo) queda PENDIENTE hasta tenerla."),
    ("DISC-21", "Tablas PLE 2 (6 códigos) y 4 (4 monedas)", "—", "Catálogos 06 (10 códigos; B a E no están en la Tabla 2) y 02 (179 monedas ISO)", "ABIERTA", "En los registros se valida contra las tablas PLE (REG-147); en UBL, contra los catálogos."),
    ("DISC-22", "Tabla PLE 10: 61 códigos; '02' = Recibo por Honorarios", "—", "Catálogo 01: 40 códigos (71 y 72 no están en la Tabla 10); Anexo 9-A, pág. 11: boleta = '02'", "ABIERTA", "Para 01, 03, 07 y 08 coinciden. Refuerza que el '02' de la boleta en el anexo es una errata (DISC-04)."),
]

# Ítems del Formato 12.1 transcritos de Git/FORMATO_12_1.pdf (cab = cabecera, det = información mínima).
# Origen en el legado de cada ítem del 12.1 (ver specs/06-migracion/mapeo-legado.md).
LEGADO_121 = {
    "cab-a": "— (constante)",
    "cab-b": "derivado de `fecha` (AAAAMM)",
    "cab-c": "— (dato del emisor)",
    "cab-d": "parámetro `establecimiento` del lote (BR-05)",
    "cab-e": "`producto` (código al inicio, o provisional `LEG-<hash>`, REG-132)",
    "cab-f": "`producto` (descripción)",
    "cab-g": "— (brecha BR-02: del producto homologado)",
    "det-a": "`fecha` (REG-130)",
    "det-b": "`nro_documento` → '00' Otros (SUPUESTO)",
    "det-c": "`nro_documento` (prefijo, p. ej. NI/VS/AJ)",
    "det-d": "`nro_documento` (número)",
    "det-e": "— (brecha BR-06: Tabla 12 PENDIENTE; sugerido por el prefijo)",
    "det-f": "`ingreso` (REG-131, REG-135); saldo inicial: BR-09",
    "det-g": "`salida` (REG-131, REG-135)",
    "det-h": "calculado (saldo acumulado)",
    "det-i": "calculado (REG-148)",
}

ITEMS_121 = {
    "cab-a": "Denominación del libro o registro.",
    "cab-b": "Período y/o ejercicio al que corresponde la información registrada.",
    "cab-c": "Número de RUC del deudor tributario, Apellidos y Nombres, Denominación y/o Razón Social de este.",
    "cab-d": "Información del Establecimiento donde se ubican las existencias.",
    "cab-e": "Código de la existencia (según Tabla 5).",
    "cab-f": "Descripción de la existencia.",
    "cab-g": "Código de la unidad de medida (según tabla 6).",
    "det-a": "Fecha de emisión del documento de traslado, comprobante de pago, documento interno o similar.",
    "det-b": "Tipo de documento de traslado, comprobante de pago, documento interno o similar (según Tabla 10).",
    "det-c": "Número de serie del documento de traslado, comprobante de pago, documento interno o similar.",
    "det-d": "Número del documento de traslado, comprobante de pago, documento interno o similar.",
    "det-e": "Tipo de operación (según Tabla 12).",
    "det-f": "Entradas en unidades, adicionalmente considerar en esta columna la información del saldo inicial.",
    "det-g": "Salidas en unidades.",
    "det-h": "Saldo final en unidades.",
    "det-i": "Totales.",
}

FORMATOS = RAIZ / "Programa" / "referencias" / "formatos" / "estructura-ple.json"
SCHEMAS = RAIZ / "Programa" / "specs" / "02-dominio-y-contratos" / "schemas"
REGISTROS_PLE = {"14.1": "registro-ventas-14-1.schema.yaml", "8.1": "registro-compras-8-1.schema.yaml"}


def escribir_matriz_registros() -> None:
    """Campo PLE (estructura comunitaria) <-> propiedad del schema <-> fila MT del Anexo 9-A."""
    import json
    if not FORMATOS.exists():
        print("AVISO: falta referencias/formatos/estructura-ple.json (ejecute tools/extraer_formatos_excel.py)")
        return
    libros = json.loads(FORMATOS.read_text(encoding="utf-8"))["libros"]
    lineas = [
        "# Matriz de trazabilidad de registros PLE (14.1 y 8.1)",
        "",
        "> **GENERADO** por `tools/construir_matriz.py` y verificado por `tools/verificar_matriz.py` (M10).",
        "> **Fuente:** estructura PLE transcrita en `Git/Macro excel Registro de compras y ventas excel 2019 MOD.xlsm` (plantilla **comunitaria**; ver `referencias/formatos/README.md`).",
        "> La columna **MT** enlaza con la [matriz del Anexo 9-A](matriz-trazabilidad.md). 'interno' significa que el dato no sale del comprobante UBL emitido (por ejemplo, el CUO contable o las compras recibidas).",
        "",
    ]
    for libro, archivo in REGISTROS_PLE.items():
        sch = yaml.safe_load((SCHEMAS / archivo).read_text(encoding="utf-8"))
        props = sch["properties"]["filas"]["items"]["properties"] | {k: v for k, v in sch["properties"].items() if k != "filas"}
        por_campo = {v.get("x-campo-ple"): (k, v.get("x-trazabilidad", "")) for k, v in props.items() if v.get("x-campo-ple")}
        lineas += [f"## Formato {libro} → `{archivo}`", "",
                   "| Campo PLE | Descripción (PLE) | Long. | Oblig. | Propiedad del schema | MT |", "|---|---|---|---|---|---|"]
        for c in libros[libro]["campos"]:
            prop, mt = por_campo.get(c["campo"], ("— (campos de libre uso; no se modelan)" if "al" in c["campo"] else "**FALTA**", ""))
            desc = _celda(c["descripcion"][:110] + ("…" if len(c["descripcion"]) > 110 else ""))
            lineas.append(f"| {c['campo']} | {desc} | {_celda(c['longitud'][:20])} | {c['obligatorio']} | `{prop}` | {mt} |")
        lineas.append("")
    sch = yaml.safe_load((SCHEMAS / "registro-inventario-12-1.schema.yaml").read_text(encoding="utf-8"))
    por_item: dict[str, list[str]] = {}

    def recorrer(nodo, ruta):
        if isinstance(nodo, dict):
            for k, v in nodo.get("properties", {}).items():
                if isinstance(v, dict) and "x-item-121" in v:
                    por_item.setdefault(v["x-item-121"], []).append(f"{ruta}{k} ({v.get('x-trazabilidad', '')})")
                recorrer(v, f"{ruta}{k}.")
                recorrer(v.get("items", {}), f"{ruta}{k}[].")
    recorrer(sch, "")
    lineas += ["## Formato 12.1 → `registro-inventario-12-1.schema.yaml`", "",
               "> Fuente: `Git/FORMATO_12_1.pdf` (los ítems no son campos PLE numerados). Las tablas 5, 6 y 12 están PENDIENTE.", "",
               "| Ítem | Texto del formato | Propiedad(es) del schema (MT o interno) | Origen en el legado |", "|---|---|---|---|"]
    for item, texto in ITEMS_121.items():
        props = "; ".join(f"`{p}`" for p in por_item.get(item, [])) or "**FALTA**"
        lineas.append(f"| {item} | {_celda(texto)} | {props} | {_celda(LEGADO_121.get(item, '**FALTA**'))} |")
    (OUT / "matriz-registros-ple.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    e = EsquemaUBL()
    e22 = EsquemaUBL(XSD_DIR_22)
    for f in FILAS:
        res = e.resolver(f["xpath_ubl"])
        if res.estado == "OK":
            f["cardinalidad_ubl"] = " / ".join(res.cardinalidades)
            f["verificado_xsd"] = "sí (UBL 2.1; también 2.2)" if e22.resolver(f["xpath_ubl"]).ok else "sí (UBL 2.1; NO en 2.2)"
            if res.tipo:
                f["tipo_longitud"] += f" [XSD: {res.tipo}]"
        elif res.estado == "NO_XSD":
            f["cardinalidad_ubl"] = "—"
            f["verificado_xsd"] = "PENDIENTE: sin XSD SUNAT (sac:) en el workspace"
        else:
            f["cardinalidad_ubl"] = "—"
            f["verificado_xsd"] = f"no: {res.detalle}"
    reglas = cargar_reglas_xsl()
    for f in FILAS:
        cods, donde = codigos_para(f, reglas)
        if not cods and f["id"] in CODIGOS_MANUALES:
            cods, donde = CODIGOS_MANUALES[f["id"]]
        f["codigos_error_sunat"] = f"{cods} [{donde}]" if cods else "—"
        if cods and f["verificado_xsd"].startswith("PENDIENTE"):
            f["verificado_xsd"] = "sí (validación SUNAT XSL 06/09/2022; no existe XSD SUNAT en el workspace)"
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "matriz-trazabilidad.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(FILAS)
    with open(OUT / "discrepancias.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "fuente_a", "valor_a", "fuente_b", "estado", "decision_en_contrato"])
        w.writerows(DISCREPANCIAS)
    ok = sum(f["verificado_xsd"].startswith("sí (UBL") for f in FILAS)
    ok_xsl = sum(f["verificado_xsd"].startswith("sí (validación SUNAT") for f in FILAS)
    pend = sum(f["verificado_xsd"].startswith("PENDIENTE") for f in FILAS)
    escribir_md(ok, pend, ok_xsl)
    escribir_matriz_registros()
    print(f"{len(FILAS)} filas: {ok} verificadas en XSD UBL 2.1, {ok_xsl} en XSL SUNAT (sin XSD), {pend} PENDIENTE, {len(FILAS) - ok - ok_xsl - pend} con error")
    print(f"Filas con código de error SUNAT: {sum(f['codigos_error_sunat'] != '—' for f in FILAS)}")
    for f in FILAS:
        if not (f["verificado_xsd"].startswith("sí") or f["verificado_xsd"].startswith("PENDIENTE")):  # noqa
            print("  ERROR", f["id"], f["xpath_ubl"], f["verificado_xsd"])
    return 0



REGLAS_XSL = RAIZ / "Programa" / "referencias" / "sunat-xsl" / "reglas-xsl.csv"
XSL_POR_LITERAL = {
    "a": "ValidaExprRegFactura-2.0.1.xsl", "b": "ValidaExprRegBoleta-2.0.1.xsl",
    "c": "ValidaExprRegNC-2.0.1.xsl", "d": "ValidaExprRegND-2.0.1.xsl",
    "E": "ValidaExprRegSummary-1.1.0.xsl", "F": "ValidaExprRegSummaryVoided-1.0.1.xsl",
}


CODIGOS_MANUALES = {"MT-087": ("3206", "ValidaExprRegFactura-2.0.1.xsl (línea 911: catálogo 51 vía variable $tipoOperacion)")}


def cargar_reglas_xsl() -> dict[str, list[dict]]:
    if not REGLAS_XSL.exists():
        print("AVISO: falta referencias/sunat-xsl/reglas-xsl.csv (ejecute tools/extraer_reglas_xsl.py)")
        return {}
    por_archivo: dict[str, list[dict]] = {}
    for r_ in csv.DictReader(REGLAS_XSL.open(encoding="utf-8-sig")):
        def norm(x: str) -> str:
            x = re.sub(r"\[[^\]]*\]", "", x.strip())  # quita predicados
            x = re.sub(r"^(\$root/|\./|/)", "", x)
            return re.sub(r"\*\[local-name\(\)='?\w+'?\]/?", "", x).strip("/")
        nodo = norm(r_["nodo"])
        ctx = norm(r_.get("contexto", ""))
        if ctx in ("*", "/*") or re.fullmatch(r"(Invoice|CreditNote|DebitNote|SummaryDocuments|VoidedDocuments)", ctx):
            ctx = ""  # contexto = raíz del documento
        r_["nodo_norm"] = nodo
        r_["ruta_ctx"] = f"{ctx}/{nodo}" if ctx and nodo and not r_["nodo"].strip().startswith("$root") else nodo
        por_archivo.setdefault(r_["archivo"], []).append(r_)
    return por_archivo


def codigos_para(fila: dict, reglas: dict[str, list[dict]]) -> tuple[str, str]:
    """Heurística: la regla cuyo nodo coincide con la cola más larga del XPath (>= 2 segmentos, o 1 si es hijo directo de la raíz)."""
    lit = next((k for k, v in LIT.items() if v in fila["norma_anexo_pagina"]), None)
    archivo = XSL_POR_LITERAL.get(lit or "a")
    if fila["id"] in XSL_POR_ID:
        archivo = XSL_POR_ID[fila["id"]]
    segs = [s_ for s_ in fila["xpath_ubl"].strip("/").split("/")[1:] if s_]
    if not segs or archivo not in reglas:
        return "", ""
    for n in range(len(segs), 0, -1):
        if n == 1 and len(segs) > 1:
            break
        cola = "/".join(segs[-n:])
        if n == 1:  # hijo directo de la raíz: solo reglas cuyo contexto es la raíz
            hits = [r_ for r_ in reglas[archivo] if r_["ruta_ctx"] == cola]
        else:
            hits = [r_ for r_ in reglas[archivo]
                    if any(x == cola or x.endswith("/" + cola) for x in (r_["nodo_norm"], r_["ruta_ctx"]))]
        if hits:
            cods = sorted({c for h in hits for c in h["codigos_error"].split()})
            lineas = sorted({int(h["linea"]) for h in hits})[:4]
            return " ".join(cods[:10]) + (" …" if len(cods) > 10 else ""), f"{archivo} (líneas {', '.join(map(str, lineas))})"
    return "", ""



def _celda(v: str) -> str:
    return v.replace("|", "\\|").replace("\n", " ")


def escribir_md(ok: int, pend: int, ok_xsl: int = 0) -> None:
    lineas = [
        "# Matriz de trazabilidad normativa",
        "",
        "> **Entregable 4.** Cruce entre los datos SUNAT (Anexo 9-A, RS 117-2017) y UBL (XPath verificado contra el XSD **UBL 2.1** de `Git/UBL-2.1/xsd`, con control cruzado en 2.2).",
        "> **GENERADO** por `tools/construir_matriz.py`; verificado por `tools/verificar_matriz.py`. No editar a mano.",
        "> La matriz completa, con sus 16 columnas, está en [`matriz-trazabilidad.csv`](matriz-trazabilidad.csv) (UTF-8 con BOM, se abre en Excel).",
        "> Las discrepancias están en [`discrepancias.csv`](discrepancias.csv) y en la sección 3.",
        "",
        "## 1. Resumen",
        "",
        "| Indicador | Valor |",
        "|---|---|",
        f"| Filas | {len(FILAS)} |",
        f"| XPath verificados en el XSD UBL 2.1 (OASIS 2.1 OS; control cruzado con 2.2) | {ok} |",
        f"| Verificados en la validación SUNAT (XSL 06/09/2022), sin XSD | {ok_xsl} |",
        f"| PENDIENTE (sin XSD ni regla XSL que los cubra) | {pend} |",
        f"| Filas con códigos de error SUNAT (cruce heurístico con las XSL) | {sum(f['codigos_error_sunat'] != '—' for f in FILAS)} |",
        f"| Con error | {len(FILAS) - ok - ok_xsl - pend} |",
        f"| Discrepancias registradas | {len(DISCREPANCIAS)} |",
        "",
        "**Pistas del enunciado verificadas:** catálogo 01 → `cbc:InvoiceTypeCode` (MT-010), 02 → `cbc:DocumentCurrencyCode` (MT-013), "
        "05 → `cac:TaxScheme/cbc:ID` (MT-038, MT-066), 06 → `cbc:CompanyID/@schemeID` (MT-024, MT-028), "
        "07 → `cbc:TaxExemptionReasonCode` (MT-064), 08 → `cbc:TierRange` (MT-065), 51 → `cbc:ProfileID` (MT-004; DISC-01, DISC-06), "
        "52 → `cbc:Note/@languageLocaleID` (MT-012), y `UBLVersionID`/`CustomizationID` (MT-002, MT-003; DISC-12). Todas existen en el XSD, "
        "aunque con las discrepancias anotadas.",
        "",
        "## 2. Matriz (columnas principales)",
        "",
        "| ID | Norma y página | Dato SUNAT | Cat. | XPath UBL | Tipo | Card. UBL | Obligatoriedad | Regla | Campo DTO/schema | Operación | CU | Legado | Nubefact (ref.) | XSD | Códigos error SUNAT | Obs. |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for f in FILAS:
        lineas.append("| " + " | ".join(_celda(f[c]) for c in COLUMNAS) + " |")
    lineas += ["", "## 3. Discrepancias entre anexos, catálogos, XSD y proveedor", "",
               "| ID | Fuente A | Valor A | Fuente B | Estado | Decisión en el contrato |", "|---|---|---|---|---|---|"]
    for d in DISCREPANCIAS:
        lineas.append("| " + " | ".join(_celda(x) for x in d) + " |")
    (OUT / "matriz-trazabilidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
