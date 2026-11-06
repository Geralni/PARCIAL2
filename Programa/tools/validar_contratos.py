"""PASO 9: validación de contratos y ejemplos.

  V1  Cada schemas/*.schema.yaml (JSON Schema 2020-12 escrito en YAML) es válido contra el meta-schema y sus $ref resuelven.
  V2  Cada catalogs/catNN.json valida contra catalogo.schema.yaml.
  V3  openapi.yaml es OpenAPI 3.1 válido; cada operación declara x-puerto-entrada y x-caso-uso.
  V4  samples/*.json validan contra su schema (por prefijo de nombre).
  V5  samples/xml/*.xml validan contra el XSD UBL 2.1 (Git/UBL-2.1/xsd) y, como control, contra 2.2.
  V6  Ninguna credencial en Programa/ (búsqueda heurística de tokens y rutas de API reales).

Requisitos:  pip install -r tools/requirements.txt
Uso:         python tools/validar_contratos.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
    from lxml import etree
    from openapi_spec_validator import validate as validar_openapi
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover
    print(f"Falta una dependencia ({exc.name}). Ejecute: pip install -r tools/requirements.txt")
    raise SystemExit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ubl_xsd import DEFAULT_XSD_DIR, XSD_DIR_22  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DC = RAIZ / "specs" / "02-dominio-y-contratos"
SAMPLES = RAIZ / "samples"

MAPA_SAMPLES = {
    "factura": "comprobante.schema.yaml",
    "boleta": "comprobante.schema.yaml",
    "nota": "nota.schema.yaml",
    "comunicacion-baja": "comunicacion-baja.schema.yaml",
    "resumen-diario": "resumen-diario.schema.yaml",
    "registro-ventas": "registro-ventas-14-1.schema.yaml",
    "registro-inventario": "registro-inventario-12-1.schema.yaml",
}
XSD_RAIZ = {
    (raiz, ver): base / "maindoc" / f"UBL-{raiz}-{ver}.xsd"
    for raiz in ("Invoice", "CreditNote", "DebitNote")
    for ver, base in (("2.1", DEFAULT_XSD_DIR), ("2.2", XSD_DIR_22))
}
# Heurística de credenciales: cadenas largas tras 'token'/'authorization', o URLs de API de proveedores reales.
PATRONES_SECRETOS = [
    re.compile(r"(?i)(token|authorization|bearer)\s*[:=\"' ]+\s*[A-Za-z0-9_\-]{24,}"),
    re.compile(r"(?i)https?://api\.nubefact\.com/api/v1/[A-Za-z0-9\-]{8,}"),
    re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"),
]

errores: list[str] = []


def ok(msg: str) -> None:
    print(f"  OK  {msg}")


def fallo(codigo: str, msg: str) -> None:
    errores.append(f"[{codigo}] {msg}")
    print(f"  ERR [{codigo}] {msg}")


def refs(nodo, acc):
    if isinstance(nodo, dict):
        for k, v in nodo.items():
            if k == "$ref" and isinstance(v, str):
                acc.append(v)
            else:
                refs(v, acc)
    elif isinstance(nodo, list):
        for v in nodo:
            refs(v, acc)
    return acc


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    schemas = {p.name: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted((DC / "schemas").glob("*.schema.yaml"))}
    registry = Registry().with_resources([(s["$id"], Resource.from_contents(s)) for s in schemas.values()])

    print("V1 meta-schema 2020-12 y $ref")
    for nombre, s in schemas.items():
        try:
            Draft202012Validator.check_schema(s)
            resolver = registry.resolver(base_uri=s["$id"])
            for r in refs(s, []):
                resolver.lookup(r)
            ok(nombre)
        except Exception as e:  # noqa: BLE001
            fallo("V1", f"{nombre}: {e}")

    def validador(nombre: str) -> Draft202012Validator:
        return Draft202012Validator(schemas[nombre], registry=registry, format_checker=FormatChecker())

    print("V2 catálogos")
    vc = validador("catalogo.schema.yaml")
    for cat in sorted((DC / "catalogs").glob("cat*.json")):
        errs = list(vc.iter_errors(json.loads(cat.read_text(encoding="utf-8"))))
        fallo("V2", f"{cat.name}: {errs[0].message}") if errs else ok(cat.name)

    print("V3 OpenAPI 3.1")
    api_path = RAIZ / "specs" / "04-api" / "openapi.yaml"
    try:
        spec = yaml.safe_load(api_path.read_text(encoding="utf-8"))
        validar_openapi(spec, base_uri=api_path.resolve().as_uri())
        ops = [o for p in spec["paths"].values() for o in p.values() if isinstance(o, dict) and "operationId" in o]
        faltan = [o["operationId"] for o in ops if "x-puerto-entrada" not in o or "x-caso-uso" not in o]
        if faltan:
            fallo("V3", f"operaciones sin x-puerto-entrada/x-caso-uso: {faltan}")
        else:
            ok(f"openapi.yaml ({len(ops)} operaciones, todas con puerto y caso de uso)")
    except Exception as e:  # noqa: BLE001
        fallo("V3", f"openapi.yaml: {e}")

    print("V4 samples JSON")
    for f in sorted(SAMPLES.glob("*.json")):
        clave = next((k for k in MAPA_SAMPLES if f.stem.startswith(k)), None)
        if not clave:
            fallo("V4", f"{f.name}: sin schema asociado")
            continue
        errs = sorted(validador(MAPA_SAMPLES[clave]).iter_errors(json.loads(f.read_text(encoding="utf-8"))), key=str)
        if errs:
            fallo("V4", f"{f.name}: {errs[0].json_path}: {errs[0].message}")
        else:
            ok(f"{f.name} ↔ {MAPA_SAMPLES[clave]}")

    print("V5 samples XML contra XSD UBL 2.1 (y 2.2)")
    cache: dict[tuple[str, str], etree.XMLSchema] = {}
    for f in sorted((SAMPLES / "xml").glob("*.xml")):
        doc = etree.parse(str(f))
        raiz = etree.QName(doc.getroot()).localname
        for ver in ("2.1", "2.2"):
            clave = (raiz, ver)
            if clave not in XSD_RAIZ:
                fallo("V5", f"{f.name}: raíz {raiz} sin XSD {ver}")
                continue
            if clave not in cache:
                cache[clave] = etree.XMLSchema(etree.parse(str(XSD_RAIZ[clave])))
            if cache[clave].validate(doc):
                ok(f"{f.name} ({raiz}, UBL {ver})")
            else:
                fallo("V5", f"{f.name} (UBL {ver}): {cache[clave].error_log.last_error}")

    print("V6 búsqueda de credenciales")
    encontrados = 0
    for f in RAIZ.rglob("*"):
        if f.is_dir() or f.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".kt", ".py", ".csv", ".xml", ".txt"}:
            continue
        texto = f.read_text(encoding="utf-8", errors="ignore")
        for pat in PATRONES_SECRETOS:
            if pat is PATRONES_SECRETOS[0] and f.name == Path(__file__).name:
                continue
            if pat.search(texto):
                encontrados += 1
                fallo("V6", f"posible credencial en {f.relative_to(RAIZ)} (patrón {pat.pattern[:30]}…)")
    if not encontrados:
        ok("sin credenciales detectadas")

    print()
    if errores:
        print(f"{len(errores)} ERROR(ES)")
        return 1
    print("OK: V1-V6 pasaron.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
