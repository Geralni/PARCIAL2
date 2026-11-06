"""PASO 3: imprime en Markdown la estructura UBL relevante para SUNAT.

Para cada raíz (Invoice, CreditNote, DebitNote) y cada agregado clave, lista los
hijos usados por el Anexo 9-A con su cardinalidad y tipo según el XSD cargado.

Uso:  python tools/generar_mapa_xsd.py > salida.md
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ubl_xsd import ANY, NS, ROOTS, EsquemaUBL  # noqa: E402

PFX = {v: k for k, v in NS.items()}

# Hijos de la raíz que usa el Anexo 9-A (págs. 1-27). El resto se omite.
RAIZ_RELEVANTES = [
    "UBLExtensions", "UBLVersionID", "CustomizationID", "ProfileID", "ID", "IssueDate", "IssueTime",
    "DueDate", "InvoiceTypeCode", "Note", "DocumentCurrencyCode", "LineCountNumeric", "InvoicePeriod",
    "DiscrepancyResponse", "OrderReference", "BillingReference", "DespatchDocumentReference",
    "AdditionalDocumentReference", "Signature", "AccountingSupplierParty", "AccountingCustomerParty",
    "Delivery", "PaymentMeans", "PaymentTerms", "PrepaidPayment", "AllowanceCharge", "TaxTotal",
    "LegalMonetaryTotal", "RequestedMonetaryTotal", "InvoiceLine", "CreditNoteLine", "DebitNoteLine",
]

AGREGADOS = {
    "UBLExtensions (firma)": ("ext", "UBLExtensionsType", None),
    "UBLExtension": ("ext", "UBLExtensionType", ["ExtensionContent"]),
    "ExtensionContent": ("ext", "ExtensionContentType", None),
    "Party": ("cac", "PartyType", ["PartyIdentification", "PartyName", "PostalAddress", "PartyTaxScheme", "PartyLegalEntity"]),
    "PartyTaxScheme": ("cac", "PartyTaxSchemeType", ["RegistrationName", "CompanyID", "RegistrationAddress", "TaxScheme"]),
    "Address": ("cac", "AddressType", ["ID", "AddressTypeCode", "StreetName", "CitySubdivisionName", "CityName", "CountrySubentity", "CountrySubentityCode", "District", "AddressLine", "Country"]),
    "BillingReference": ("cac", "BillingReferenceType", None),
    "Response (DiscrepancyResponse)": ("cac", "ResponseType", ["ReferenceID", "ResponseCode", "Description"]),
    "PaymentTerms": ("cac", "PaymentTermsType", ["ID", "PaymentMeansID", "PaymentPercent", "Amount", "PaymentDueDate"]),
    "AllowanceCharge": ("cac", "AllowanceChargeType", ["ChargeIndicator", "AllowanceChargeReasonCode", "MultiplierFactorNumeric", "Amount", "BaseAmount"]),
    "TaxTotal": ("cac", "TaxTotalType", None),
    "TaxSubtotal": ("cac", "TaxSubtotalType", ["TaxableAmount", "TaxAmount", "BaseUnitMeasure", "PerUnitAmount", "Percent", "TaxCategory"]),
    "TaxCategory": ("cac", "TaxCategoryType", ["ID", "Percent", "TaxExemptionReasonCode", "TierRange", "TierRatePercent", "TaxScheme"]),
    "TaxScheme": ("cac", "TaxSchemeType", ["ID", "Name", "TaxTypeCode"]),
    "MonetaryTotal": ("cac", "MonetaryTotalType", None),
    "InvoiceLine": ("cac", "InvoiceLineType", ["ID", "InvoicedQuantity", "LineExtensionAmount", "PricingReference", "Delivery", "AllowanceCharge", "TaxTotal", "Item", "Price"]),
    "CreditNoteLine": ("cac", "CreditNoteLineType", ["ID", "CreditedQuantity", "LineExtensionAmount", "PricingReference", "TaxTotal", "Item", "Price"]),
    "DebitNoteLine": ("cac", "DebitNoteLineType", ["ID", "DebitedQuantity", "LineExtensionAmount", "PricingReference", "TaxTotal", "Item", "Price"]),
    "PricingReference / Price": ("cac", "PriceType", ["PriceAmount", "PriceTypeCode"]),
    "Item": ("cac", "ItemType", ["Description", "SellersItemIdentification", "CommodityClassification", "AdditionalItemProperty"]),
    "CommodityClassification": ("cac", "CommodityClassificationType", ["ItemClassificationCode"]),
}


def nombre(key) -> str:
    if key == ANY:
        return "`xsd:any` (##other, lax)"
    return f"{PFX.get(key[0], '?')}:{key[1]}"


def fila(e: EsquemaUBL, key, card) -> str:
    tipo = "" if key == ANY else e.base_udt(e.tipo_de(key))
    attrs = "" if key == ANY else ", ".join(sorted(e.atributos(e.tipo_de(key)) - {None}))
    return f"| {nombre(key)} | {card} | {tipo} | {attrs} |"


def tabla(e: EsquemaUBL, tkey, solo) -> list[str]:
    out = ["| Elemento | Card. XSD | Tipo base | Atributos admitidos |", "|---|---|---|---|"]
    vistos = set()
    for key, card in e.hijos(tkey):
        if key in vistos:
            continue
        vistos.add(key)
        if solo and key != ANY and key[1] not in solo:
            continue
        out.append(fila(e, key, card))
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    e = EsquemaUBL()
    print(f"<!-- Generado por tools/generar_mapa_xsd.py desde {len(e.archivos)} XSD -->\n")
    for raiz, ns in ROOTS.items():
        print(f"#### Raíz `{raiz}`\n")
        print("\n".join(tabla(e, e.tipo_de((ns, raiz)), RAIZ_RELEVANTES)))
        print()
    for titulo, (pfx, tipo, solo) in AGREGADOS.items():
        print(f"#### {titulo} (`{pfx}:{tipo}`)\n")
        print("\n".join(tabla(e, (NS[pfx], tipo), solo)))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
