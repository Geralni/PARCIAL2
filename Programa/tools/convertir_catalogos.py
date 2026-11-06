"""PASO 2: convierte los catálogos del Anexo 8 (Git/NN.txt) a JSON normalizado.

- Detecta si cada .txt es JSON o CSV y lo valida.
- Normaliza a items [{codigo, descripcion, ...extras}] sin alterar los códigos.
- Agrega metadatos: campo UBL destino según el Anexo 9-A (con página), fuente y
  advertencia de fuente no oficial, y el resultado del contraste con el Anexo 9-A.
- Escribe specs/02-dominio-y-contratos/catalogs/catNN.json.

Solo lee Git/ (de solo lectura). Uso:  python tools/convertir_catalogos.py
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "Git"
DESTINO = RAIZ / "Programa" / "specs" / "02-dominio-y-contratos" / "catalogs"

ADVERTENCIA = (
    "Fuente comunitaria NO oficial (última actualización 2020). "
    "Debe contrastarse con el Anexo 8 oficial de SUNAT antes de producción."
)
A9 = "Anexo 9-A, RS 117-2017"

# Metadatos por catálogo. Las páginas son del PDF Git/anexoIX-117-2017.pdf.
META: dict[str, dict] = {
    "01": {
        "nombre": "Código de tipo de documento",
        "campo_ubl": [
            ("/Invoice/cbc:InvoiceTypeCode", 1),
            ("/CreditNote/cac:BillingReference/cac:CreditNoteDocumentReference/cbc:DocumentTypeCode", 19),
            ("/SummaryDocuments/sac:SummaryDocumentsLine/cbc:DocumentTypeCode", 28),
            ("/VoidedDocuments/sac:VoidedDocumentsLine/cbc:DocumentTypeCode", 31),
        ],
        "contraste": {
            "estado": "DISCREPANCIA",
            "observaciones": [
                "Factura (pág. 1): InvoiceTypeCode an2 Catálogo 01; el valor '01' existe en el catálogo.",
                "Boleta (pág. 11): el anexo indica el valor fijo \"02\", pero en este catálogo la boleta es '03' "
                "y '02' no existe. Registrado como DISC-04.",
            ],
        },
    },
    "02": {
        "nombre": "Código de tipo de monedas",
        "campo_ubl": [
            ("/Invoice/cbc:DocumentCurrencyCode", 1),
            ("/Invoice/cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID", 7),
        ],
        "contraste": {
            "estado": "NO_APLICA",
            "observaciones": [
                "El anexo remite a ISO 4217 Alpha (@listID, pág. 1). El archivo fuente lista país-moneda; "
                "se deduplica por código de moneda.",
            ],
        },
    },
    "03": {
        "nombre": "Código de tipo de unidad de medida comercial",
        "campo_ubl": [("/Invoice/cac:InvoiceLine/cbc:InvoicedQuantity/@unitCode", 8)],
        "contraste": {
            "estado": "NO_APLICA",
            "observaciones": ["El anexo remite a UN/ECE rec 20 (@unitCodeListID, pág. 8). Es un subconjunto comercial."],
        },
    },
    "04": {
        "nombre": "Código de país",
        "campo_ubl": [
            ("/Invoice/cac:DeliveryTerms/cac:DeliveryLocation/cac:Address/cac:Country/cbc:IdentificationCode", 6)
        ],
        "contraste": {
            "estado": "NO_APLICA",
            "observaciones": ["El anexo remite a ISO 3166-1 (@listID, pág. 6); se usa el código alfa-2 (A2) como 'codigo'."],
        },
    },
    "05": {
        "nombre": "Códigos de tipos de tributos",
        "campo_ubl": [
            ("/Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID", 7),
            ("/Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:Name", 7),
            ("/Invoice/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:TaxTypeCode", 7),
            ("/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID", 10),
        ],
        "contraste": {
            "estado": "DISCREPANCIA",
            "observaciones": [
                "Factura (págs. 7 y 10): TaxScheme/cbc:ID figura como an..3 y TaxTypeCode como an4. "
                "Nota de crédito (pág. 20) y resumen diario (pág. 29): cbc:ID an4 y TaxTypeCode an3. "
                "Los códigos del catálogo son de 4 dígitos (1000, 2000...) y los internacionales de 3 letras "
                "(VAT, EXC...), lo que coincide con la NC y el RC. Registrado como DISC-05.",
                "El código 7152 (ICBPER) no tiene respaldo en el Anexo 9-A (2017). PENDIENTE: anexos posteriores (ENT-04).",
                "cbc:Name an..6: todos los nombres del catálogo caben (máx. 'ICBPER' = 6).",
            ],
        },
    },
    "06": {
        "nombre": "Código de tipo de documento de identidad",
        "campo_ubl": [
            ("/Invoice/cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID/@schemeID", 3),
            ("/Invoice/cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID/@schemeID", 3),
        ],
        "contraste": {
            "estado": "COHERENTE",
            "observaciones": ["@schemeID an1 (pág. 3): todos los códigos del catálogo tienen 1 carácter."],
        },
    },
    "07": {
        "nombre": "Código de tipo de afectación del IGV",
        "campo_ubl": [
            ("/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TaxExemptionReasonCode", 10)
        ],
        "contraste": {
            "estado": "COHERENTE",
            "observaciones": [
                "TaxExemptionReasonCode an2 (pág. 10): todos los códigos tienen 2 dígitos.",
                "La columna 'codigo_de_tributo' (relación con el catálogo 05) no figura en el Anexo 9-A: "
                "solo tiene respaldo en la fuente comunitaria. Valores como '1016 o 9996' se normalizan a lista.",
            ],
        },
    },
    "08": {
        "nombre": "Código de tipos de sistema de cálculo del ISC",
        "campo_ubl": [
            ("/Invoice/cac:InvoiceLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange", 10),
            ("/CreditNote/cac:CreditNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange", 22),
            ("/DebitNote/cac:DebitNoteLine/cac:TaxTotal/cac:TaxSubtotal/cac:TaxCategory/cbc:TierRange", 26),
        ],
        "contraste": {
            "estado": "COHERENTE",
            "observaciones": [
                "TierRange 0..1 an2 Catálogo 08 en la factura (pág. 10), la boleta (pág. 17) y la NC (pág. 22). "
                "Los 3 códigos (01, 02, 03) tienen 2 dígitos.",
                "Las tasas, los montos fijos y los apéndices del TUO IGV e ISC citados en las descripciones NO "
                "están en el workspace: son parámetros PENDIENTE.",
            ],
        },
    },
    "09": {
        "nombre": "Códigos de tipo de nota de crédito electrónica",
        "campo_ubl": [("/CreditNote/cac:DiscrepancyResponse/cbc:ResponseCode", 19)],
        "contraste": {
            "estado": "PARCIAL",
            "observaciones": [
                "ResponseCode n2 (pág. 19): todos los códigos tienen 2 dígitos.",
                "El código 13 (corrección de cuotas o fechas de pago) no tiene respaldo en el Anexo 9-A (2017). PENDIENTE (ENT-04).",
            ],
        },
    },
    "10": {
        "nombre": "Códigos de tipo de nota de débito electrónica",
        "campo_ubl": [("/DebitNote/cac:DiscrepancyResponse/cbc:ResponseCode", 23)],
        "contraste": {"estado": "COHERENTE", "observaciones": ["ResponseCode n2 (pág. 23)."]},
    },
    "16": {
        "nombre": "Código de tipo de precio de venta unitario",
        "campo_ubl": [
            ("/Invoice/cac:InvoiceLine/cac:PricingReference/cac:AlternativeConditionPrice/cbc:PriceTypeCode", 8)
        ],
        "contraste": {"estado": "COHERENTE", "observaciones": ["PriceTypeCode an2 Catálogo 16 (pág. 8)."]},
    },
    "51": {
        "nombre": "Código de tipo de operación",
        "campo_ubl": [("/Invoice/cbc:ProfileID", 1)],
        "contraste": {
            "estado": "DISCREPANCIA",
            "observaciones": [
                "ProfileID figura como 'an2 Catálogo 51' (págs. 1 y 11), pero los códigos del catálogo 51 tienen "
                "4 dígitos (0101...). Registrado como DISC-06.",
                "El @schemeURI del mismo nodo termina en 'catalogo17' (págs. 1 y 11). Registrado como DISC-01.",
                "La nota de crédito (pág. 19) no lista ProfileID; la nota de débito (pág. 23) lo lista sin catálogo.",
            ],
        },
    },
    "52": {
        "nombre": "Códigos de leyendas",
        "campo_ubl": [("/Invoice/cbc:Note/@languageLocaleID", 1)],
        "contraste": {
            "estado": "COHERENTE",
            "observaciones": ["@languageLocaleID n4 Catálogo 52 (pág. 1): todos los códigos tienen 4 dígitos."],
        },
    },
    "53": {
        "nombre": "Códigos de cargos o descuentos",
        "campo_ubl": [
            ("/Invoice/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode", 6),
            ("/Invoice/cac:InvoiceLine/cac:AllowanceCharge/cbc:AllowanceChargeReasonCode", 9),
        ],
        "contraste": {
            "estado": "COHERENTE",
            "observaciones": ["AllowanceChargeReasonCode an..2 (pág. 6) / an2 (pág. 9): todos los códigos tienen 2 dígitos."],
        },
    },
}


def detectar_y_cargar(path: Path) -> tuple[str, list[dict]]:
    texto = path.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(texto)
        if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
            raise ValueError(f"{path.name}: el JSON no es una lista de objetos")
        return "JSON", data
    except json.JSONDecodeError:
        filas = list(csv.DictReader(io.StringIO(texto)))
        if not filas:
            raise ValueError(f"{path.name}: no es JSON ni CSV válido")
        return "CSV", filas


def limpiar(v):
    return v.strip() if isinstance(v, str) else v


def normalizar(num: str, crudos: list[dict]) -> list[dict]:
    items: list[dict] = []
    if num == "02":
        vistos: dict[str, dict] = {}
        for x in crudos:
            cod = limpiar(x.get("Currency"))
            if not cod:
                continue  # entradas ISO sin moneda (p. ej. Antártida)
            it = vistos.setdefault(cod, {
                "codigo": cod,
                "descripcion": limpiar(x.get("CurrencyName")),
                "numero_iso": x.get("CurrencyNumber"),
                "decimales": limpiar(str(x.get("CurrencyMeasurementUnits"))),
                "paises": [],
            })
            it["paises"].append(limpiar(x.get("CountryName")))
        return sorted(vistos.values(), key=lambda i: i["codigo"])
    if num == "04":
        return [{"codigo": limpiar(x["A2"]), "descripcion": limpiar(x["Country"]),
                 "alfa3": limpiar(x.get("A3")), "numero_iso": x.get("Number")} for x in crudos]
    for x in crudos:
        it = {"codigo": limpiar(x["codigo"]), "descripcion": limpiar(x["descripcion"])}
        for k, v in x.items():
            if k in ("codigo", "descripcion"):
                continue
            v = limpiar(v)
            if num == "07" and k == "codigo_de_tributo":
                v = [s.strip() for s in v.split(" o ")]
            if num == "51" and k == "tipo_de_comprobante_asociado":
                v = [s.strip().rstrip(" ").strip() for s in v.replace(" ", " ").split(",")]
            it[k] = v
        items.append(it)
    return items


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    resumen = []
    for num, meta in META.items():
        src = ORIGEN / f"{num}.txt"
        formato, crudos = detectar_y_cargar(src)
        items = normalizar(num, crudos)
        codigos = [i["codigo"] for i in items]
        duplicados = sorted({c for c in codigos if codigos.count(c) > 1})
        doc = {
            "$schema": "../schemas/catalogo.schema.yaml",
            "numero": num,
            "nombre": meta["nombre"],
            "fuente": {
                "archivo": f"Git/{num}.txt",
                "formato_detectado": formato,
                "tipo": "comunitaria_no_oficial",
                "ultima_actualizacion": "2020",
                "registros_origen": len(crudos),
            },
            "advertencia": ADVERTENCIA,
            "campo_ubl": [{"xpath": x, "referencia": f"{A9}, pág. {p}"} for x, p in meta["campo_ubl"]],
            "contraste_anexo_9a": meta["contraste"],
            "duplicados_detectados": duplicados,
            "items": items,
        }
        out = DESTINO / f"cat{num}.json"
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        resumen.append((num, formato, len(crudos), len(items), duplicados))
    for r in resumen:
        print(f"cat{r[0]}: {r[1]} origen={r[2]} items={r[3]} duplicados={r[4]}")
    escribir_schema_enums()
    return 0


def escribir_schema_enums() -> None:
    """Genera schemas/catalogos.schema.yaml: un $def con enum por catálogo."""
    defs = {}
    for num, meta in META.items():
        doc = json.loads((DESTINO / f"cat{num}.json").read_text(encoding="utf-8"))
        defs[f"Cat{num}"] = {
            "title": f"Catálogo {num}: {meta['nombre']}",
            "description": f"Generado desde catalogs/cat{num}.json ({ADVERTENCIA})",
            "type": "string",
            "enum": [i["codigo"] for i in doc["items"]],
            "x-catalogo": f"../catalogs/cat{num}.json",
        }
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://specs.abc-software-corp.local/schemas/catalogos.schema.yaml",
        "title": "Códigos de catálogos SUNAT (Anexo 8)",
        "description": "GENERADO por tools/convertir_catalogos.py. No editar a mano.",
        "$defs": defs,
    }
    out = DESTINO.parent / "schemas" / "catalogos.schema.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    import yaml  # pip install -r tools/requirements.txt
    cab = "# Códigos de catálogos SUNAT (Anexo 8)\n# JSON Schema 2020-12 escrito en YAML. GENERADO por tools/convertir_catalogos.py. No editar a mano.\n"
    class Dumper(yaml.SafeDumper):
        pass

    # Cita todo texto con aspecto numérico ("08", "0208"): YAML 1.2 (p. ej. Redocly) los leería como enteros.
    numerico = re.compile(r"^[-+]?(\d[\d_]*(\.\d*)?|\.\d+)([eE][-+]?\d+)?$|^(true|false|yes|no|on|off|null|~)$", re.I)
    Dumper.add_representer(str, lambda d, v: d.represent_scalar("tag:yaml.org,2002:str", v, style="'" if numerico.match(v) else None))
    out.write_text(cab + yaml.dump(schema, Dumper=Dumper, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
