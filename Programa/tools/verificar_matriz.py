"""PASO 7/9: verifica la matriz de trazabilidad y la coherencia del entregable.

Comprobaciones (biblioteca estándar + pyyaml para leer los schemas YAML):
  M1  Cada XPath de la matriz existe en el XSD UBL 2.1 (Git/UBL-2.1/xsd) (o está marcado PENDIENTE con motivo si no hay XSD).
  M2  La columna verificado_xsd coincide con la verificación real.
  M3  Cada regla citada existe en reglas-de-validacion.md.
  M4  Cada campo_dto_schema apunta a un schema y una propiedad existentes (o es 'interno' / '—').
  M5  Cada operationId citado existe en openapi.yaml; cada caso de uso existe en 01-casos-de-uso.md.
  M6  Cada propiedad de los schemas tiene x-trazabilidad = 'interno' o un MT-xxx existente.
  M7  Cada propiedad de los DTO Kotlin lleva comentario MT-xxx existente o 'interno'; los REG de los TODO existen.
  M8  Los XPath de catalogs/*.json existen en el XSD (o son NO_XSD).
  M9  Cada caso de uso mapea a >= 1 operación OpenAPI (x-caso-uso) y a >= 1 puerto de entrada.
  M11 Control cruzado: InvoiceType idéntico en 2.1 y 2.2, y cada XPath verificado en 2.1 se compara con 2.2 (avisos).
  M10 Cada campo PLE 14.1 y 8.1 (referencias/formatos) y cada ítem del 12.1 (FORMATO_12_1.pdf) tiene propiedad en su schema, y viceversa.

Uso:  python tools/verificar_matriz.py      (código de salida 0 = todo correcto)
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import yaml  # pip install -r tools/requirements.txt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ubl_xsd import XSD_DIR_22, EsquemaUBL  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SPECS = RAIZ / "specs"
DC = SPECS / "02-dominio-y-contratos"
MATRIZ = SPECS / "05-trazabilidad" / "matriz-trazabilidad.csv"

errores: list[str] = []
avisos: list[str] = []


def err(codigo: str, msg: str) -> None:
    errores.append(f"[{codigo}] {msg}")


def cargar_schemas() -> dict[str, dict]:
    return {p.name: yaml.safe_load(p.read_text(encoding="utf-8")) for p in (DC / "schemas").glob("*.schema.yaml")}


def resolver_puntero(schemas: dict, archivo: str, puntero: str):
    """Recorre un JSON Pointer siguiendo $ref (entre archivos del mismo directorio)."""
    nodo = schemas.get(archivo)
    if nodo is None:
        return None
    for parte in [p for p in puntero.strip("/").split("/") if p]:
        guard = 0
        while isinstance(nodo, dict) and "$ref" in nodo and parte not in nodo and guard < 10:
            ref = nodo["$ref"]
            f, _, ptr = ref.partition("#")
            archivo = f or archivo
            nodo = resolver_puntero(schemas, archivo, ptr) if ptr else schemas.get(archivo)
            guard += 1
        if isinstance(nodo, dict) and parte in nodo:
            nodo = nodo[parte]
        else:
            return None
    return nodo


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    xsd = EsquemaUBL()
    schemas = cargar_schemas()
    filas = list(csv.DictReader(MATRIZ.open(encoding="utf-8-sig")))
    ids_mt = {f["id"] for f in filas}
    reglas = set(re.findall(r"\|\s*(REG-\d{3})\s*\|", (DC / "reglas-de-validacion.md").read_text(encoding="utf-8")))
    openapi = (SPECS / "04-api" / "openapi.yaml").read_text(encoding="utf-8")
    op_ids = set(re.findall(r"operationId:\s*(\w+)", openapi))
    cu_doc = (SPECS / "01-casos-de-uso.md").read_text(encoding="utf-8") if (SPECS / "01-casos-de-uso.md").exists() else ""
    cus = set(re.findall(r"^##+\s*(CU-\d{2})", cu_doc, re.M))
    puertos_doc = (SPECS / "04-api" / "puertos.md").read_text(encoding="utf-8")

    # ---------- M1, M2 ----------
    n_ok = n_pend = n_xsl = 0
    for f in filas:
        r = xsd.resolver(f["xpath_ubl"])
        ver = f["verificado_xsd"]
        if r.estado == "OK":
            n_ok += 1
            if not ver.startswith("sí"):
                err("M2", f"{f['id']}: el XPath existe pero verificado_xsd='{ver}'")
        elif r.estado == "NO_XSD":
            if ver.startswith("sí (validación SUNAT"):
                n_xsl += 1
                if f["codigos_error_sunat"] in ("", "—"):
                    err("M1", f"{f['id']}: dice verificado en XSL SUNAT pero no tiene códigos de error")
            elif ver.startswith("PENDIENTE"):
                n_pend += 1
            else:
                err("M1", f"{f['id']}: sin XSD, sin regla XSL y no marcado PENDIENTE")
        else:
            err("M1", f"{f['id']}: {f['xpath_ubl']} -> {r.estado}: {r.detalle}")
        if not any(k in f["norma_anexo_pagina"] for k in ("pág.", "PENDIENTE", "Validación SUNAT")):
            err("M1", f"{f['id']}: norma sin página, sin XSL SUNAT y sin PENDIENTE")

        # ---------- M3 ----------
        for reg in re.findall(r"REG-\d{3}", f["regla"]):
            if reg not in reglas:
                err("M3", f"{f['id']}: regla {reg} no existe")

        # ---------- M4 ----------
        dto = f["campo_dto_schema"].strip()
        if dto and not dto.startswith(("interno", "—")):
            ref = dto.split(" ")[0]
            archivo, _, ptr = ref.partition("#")
            if archivo not in schemas:
                err("M4", f"{f['id']}: schema {archivo} no existe")
            elif resolver_puntero(schemas, archivo, ptr) is None:
                err("M4", f"{f['id']}: {ref} no resuelve")

        # ---------- M5 ----------
        for op in re.findall(r"[a-zA-Z]+", f["operacion_openapi"]):
            if op not in op_ids:
                err("M5", f"{f['id']}: operationId {op} no existe en openapi.yaml")
        for cu in re.findall(r"CU-\d{2}", f["caso_uso"]):
            if cu not in cus:
                err("M5", f"{f['id']}: {cu} no existe en 01-casos-de-uso.md")

    # ---------- M6 ----------
    n_props = 0

    def revisar_props(nombre: str, nodo, ruta: str) -> None:
        nonlocal n_props
        if isinstance(nodo, dict):
            for clave, val in nodo.items():
                if clave in ("allOf", "if", "then", "else", "oneOf", "anyOf", "not"):
                    continue  # restricciones condicionales, no definen campos nuevos
                if clave == "properties" and isinstance(val, dict):
                    for prop, ps in val.items():
                        if prop == "$schema":
                            continue
                        n_props += 1
                        tr = ps.get("x-trazabilidad") if isinstance(ps, dict) else None
                        if tr is None:
                            err("M6", f"{nombre}:{ruta}/{prop} sin x-trazabilidad")
                        elif tr != "interno" and tr not in ids_mt:
                            err("M6", f"{nombre}:{ruta}/{prop} -> {tr} no existe en la matriz")
                        revisar_props(nombre, ps, f"{ruta}/{prop}")
                else:
                    revisar_props(nombre, val, ruta)
        elif isinstance(nodo, list):
            for v in nodo:
                revisar_props(nombre, v, ruta)

    for nombre, sch in schemas.items():
        if nombre in ("catalogo.schema.yaml", "catalogos.schema.yaml"):
            continue  # metaestructura de archivos de catálogo, no DTO
        revisar_props(nombre, sch, "")

    # ---------- M7 ----------
    n_campos_kt = 0
    for kt in (DC / "dtos").rglob("*.kt"):
        for i, linea in enumerate(kt.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"\s*val\s+\w+\s*:", linea):
                n_campos_kt += 1
                mts = re.findall(r"MT-\d{3}", linea)
                if not mts and "interno" not in linea:
                    err("M7", f"{kt.name}:{i} campo sin MT-xxx ni 'interno'")
                for mt in mts:
                    if mt not in ids_mt:
                        err("M7", f"{kt.name}:{i} {mt} no existe en la matriz")
            for reg in re.findall(r"TODO\(spec: (REG-\d{3})", linea):
                if reg not in reglas:
                    err("M7", f"{kt.name}:{i} {reg} no existe")

    # ---------- M8 ----------
    for cat in sorted((DC / "catalogs").glob("cat*.json")):
        for c in json.loads(cat.read_text(encoding="utf-8"))["campo_ubl"]:
            r = xsd.resolver(c["xpath"])
            if r.estado not in ("OK", "NO_XSD"):
                err("M8", f"{cat.name}: {c['xpath']} -> {r.detalle}")

    # ---------- M9 ----------
    cu_ops: dict[str, list[str]] = {}
    for bloque in re.split(r"\n\s{4}(?=get:|post:|put:|delete:|patch:)", openapi):
        op = re.search(r"operationId:\s*(\w+)", bloque)
        cu = re.search(r"x-caso-uso:\s*(CU-\d{2})", bloque)
        if op and cu:
            cu_ops.setdefault(cu.group(1), []).append(op.group(1))
    for cu in sorted(cus):
        if not cu_ops.get(cu):
            err("M9", f"{cu} no tiene operación OpenAPI (x-caso-uso)")
        if not re.search(rf"\|\s*`\w+UseCase[^|]*\|\s*{cu}\s*\|", puertos_doc):
            err("M9", f"{cu} no tiene puerto de entrada en puertos.md")

    # ---------- M10 ----------
    estructura = RAIZ / "referencias" / "formatos" / "estructura-ple.json"
    n_ple = 0
    if not estructura.exists():
        err("M10", "falta referencias/formatos/estructura-ple.json (ejecute tools/extraer_formatos_excel.py)")
    else:
        libros = json.loads(estructura.read_text(encoding="utf-8"))["libros"]
        for libro, archivo in {"14.1": "registro-ventas-14-1.schema.yaml", "8.1": "registro-compras-8-1.schema.yaml"}.items():
            sch = schemas[archivo]
            props = sch["properties"]["filas"]["items"]["properties"] | sch["properties"]
            en_schema = {v["x-campo-ple"] for v in props.values() if isinstance(v, dict) and "x-campo-ple" in v}
            en_ple = {c["campo"] for c in libros[libro]["campos"] if " al " not in c["campo"]}
            n_ple += len(en_ple)
            for faltante in sorted(en_ple - en_schema, key=int):
                err("M10", f"{archivo}: campo PLE {libro} #{faltante} sin propiedad (x-campo-ple)")
            for sobrante in sorted(en_schema - en_ple):
                err("M10", f"{archivo}: x-campo-ple {sobrante} no existe en la estructura PLE {libro}")

    from construir_matriz import ITEMS_121
    texto121 = (DC / "schemas" / "registro-inventario-12-1.schema.yaml").read_text(encoding="utf-8")
    items_schema = set(re.findall(r"x-item-121:\s*'?([a-z]+-[a-z])'?", texto121))
    for faltante in sorted(set(ITEMS_121) - items_schema):
        err("M10", f"registro-inventario-12-1.schema.yaml: ítem {faltante} del FORMATO_12_1.pdf sin propiedad (x-item-121)")
    for sobrante in sorted(items_schema - set(ITEMS_121)):
        err("M10", f"registro-inventario-12-1.schema.yaml: x-item-121 {sobrante} no existe en el formato")
    n_ple += len(ITEMS_121)

    # ---------- M11 ----------
    import xml.etree.ElementTree as ET
    X = "{http://www.w3.org/2001/XMLSchema}"

    def hijos_invoice(path: Path) -> list[tuple[str, str]]:
        ct = next(c for c in ET.parse(path).getroot().findall(X + "complexType") if c.get("name") == "InvoiceType")
        return [(e.get("ref"), f'{e.get("minOccurs", "1")}..{e.get("maxOccurs", "1")}') for e in ct.iter(X + "element")]
    if hijos_invoice(xsd.dir / "maindoc" / "UBL-Invoice-2.1.xsd") != hijos_invoice(XSD_DIR_22 / "maindoc" / "UBL-Invoice-2.2.xsd"):
        err("M11", "InvoiceType difiere entre 2.1 y 2.2")
    xsd22 = EsquemaUBL(XSD_DIR_22)
    n_cruce = 0
    for f in filas:
        r21 = xsd.resolver(f["xpath_ubl"])
        if r21.estado != "OK":
            continue
        r22 = xsd22.resolver(f["xpath_ubl"])
        n_cruce += 1
        if not r22.ok:
            avisos.append(f"{f['id']}: existe en 2.1 pero no en 2.2")
        elif r21.cardinalidades != r22.cardinalidades:
            avisos.append(f"{f['id']}: cardinalidad 2.1 {r21.cardinalidades} != 2.2 {r22.cardinalidades}")
    m11 = f"{n_cruce} XPath verificados en 2.1 y comparados con 2.2: {len(avisos)} diferencias"

    print(f"Matriz: {len(filas)} filas | XPath OK en XSD UBL 2.1: {n_ok} | verificados en XSL SUNAT (sin XSD): {n_xsl} | PENDIENTE: {n_pend}")
    print(f"M11 2.1 vs 2.2: {m11}")
    for a in avisos:
        print("  aviso", a)
    print(f"Registros: {n_ple} campos/ítems (14.1 + 8.1 PLE, 12.1 PDF) cubiertos por schema")
    print(f"Schemas: {len(schemas)} archivos, {n_props} propiedades revisadas | DTO Kotlin: {n_campos_kt} campos")
    print(f"Casos de uso: {len(cus)} | operationIds: {len(op_ids)} | reglas: {len(reglas)}")
    if errores:
        print(f"\n{len(errores)} ERROR(ES):")
        for e in errores:
            print("  " + e)
        return 1
    print("\nOK: todas las comprobaciones M1-M11 pasaron.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
