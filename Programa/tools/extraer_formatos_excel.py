"""Extrae la estructura de los formatos de libros (14.1, 8.1, 13.1 y PLE) desde los Excel de Git/.

Fuentes (Git/, SOLO LECTURA; plantillas COMUNITARIAS, no oficiales):
  - "registro ventas formato 14.1.xls"                      -> columnas del formato impreso 14.1
  - "592044723-FORMATO-8-1.xlsx"                           -> columnas del formato impreso 8.1 (simplificado)
  - "464918148-11-FORMATO-DE-KARDEX-SEGUN-SUNAT-xls.xls"   -> columnas del formato 13.1 (¡no es 12.1!)
  - "Macro excel Registro de compras y ventas excel 2019 MOD.xlsm"
        hojas Estructura (PLE 8.1, 8.2, 8.3, 14.1, 14.2), Reglas (regla general por Tabla 10)
        y Tablas Generales (tablas PLE).

Seguridad: solo se abren las hojas nombradas aquí (nunca 'Pasword', 'Inicio', 'Sistema'); las macros
no se ejecutan (openpyxl keep_vba=False); no se copian filas de datos de ejemplo (contienen RUC de terceros).

Salida: Programa/referencias/formatos/*.json|csv
Requisitos: openpyxl, xlrd (ver tools/requirements.txt).  Uso: python tools/extraer_formatos_excel.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import openpyxl
import xlrd

RAIZ = Path(__file__).resolve().parents[2]
GIT = RAIZ / "Git"
OUT = RAIZ / "Programa" / "referencias" / "formatos"

F141 = GIT / "registro ventas formato 14.1.xls"
F81 = GIT / "592044723-FORMATO-8-1.xlsx"
F131 = GIT / "464918148-11-FORMATO-DE-KARDEX-SEGUN-SUNAT-xls.xls"
MACRO = GIT / "Macro excel Registro de compras y ventas excel 2019 MOD.xlsm"
HOJAS_PERMITIDAS = {"Estructura", "Reglas", "Tablas Generales"}
TABLAS_EXCLUIDAS = {"17"}  # plan de cuentas: no es tabla tributaria


def txt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return re.sub(r"\s+", " ", str(v)).strip()


def columnas_por_encabezado(filas: list[list], desde: int, hasta: int) -> list[dict]:
    """Une verticalmente las celdas de encabezado (filas desde..hasta, 1-based) por columna."""
    ncol = max(len(f) for f in filas)
    cols = []
    for c in range(ncol):
        partes = [txt(filas[r][c]) for r in range(desde - 1, hasta) if c < len(filas[r]) and txt(filas[r][c])]
        if partes:
            cols.append({"columna": c + 1, "encabezado": " / ".join(partes)})
    return cols


def filas_xls(p: Path) -> list[list]:
    sh = xlrd.open_workbook(str(p)).sheet_by_index(0)
    return [sh.row_values(r) for r in range(sh.nrows)]


def filas_xlsx(p: Path) -> list[list]:
    ws = openpyxl.load_workbook(p, data_only=True).worksheets[0]
    return [[c.value for c in row] for row in ws.iter_rows()]


def plantillas() -> dict:
    f141, f81, f131 = filas_xls(F141), filas_xlsx(F81), filas_xls(F131)
    return {
        "14.1": {
            "archivo": f"Git/{F141.name}", "hoja": "F 14.1 Reg. de Ventas", "titulo": txt(f141[0][0]),
            "cabecera": ["PERIODO", "RUC", "APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL"],
            "columnas": columnas_por_encabezado(f141, 7, 12),
        },
        "8.1": {
            "archivo": f"Git/{F81.name}", "hoja": "FORMATO 8.1 REGISTRO DE COMPRAS", "titulo": txt(f81[2][1]),
            "cabecera": ["PERIODO", "RUC", "APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL"],
            "columnas": columnas_por_encabezado(f81, 4, 7),
            "observacion": "Plantilla simplificada: una sola columna de base imponible e IGV; incluye columnas contables 'DIVISIONARIA'.",
        },
        "13.1": {
            "archivo": f"Git/{F131.name}", "hoja": "F 13.1 Det.Inv.Per.Val.", "titulo": txt(f131[0][0]),
            "cabecera": [txt(f131[r][0]).rstrip(":") for r in range(2, 11) if txt(f131[r][0])],
            "columnas": columnas_por_encabezado(f131, 13, 15),
            "observacion": "El nombre del archivo dice 'kardex', pero es el FORMATO 13.1 (valorizado), no el 12.1. "
                           "Las filas de datos de ejemplo (empresa de terceros) NO se extraen.",
        },
    }


def estructura_ple(ws) -> dict:
    libros: dict[str, dict] = {}
    actual = None
    for row in ws.iter_rows(values_only=True, max_col=8):
        c = [txt(v) for v in row] + [""] * 8
        m = re.match(r"^(8\.[1-3]|14\.[12])\s+(.+)$", c[1])
        if m:
            actual = libros.setdefault(m.group(1), {"titulo": c[1], "campos": [], "notas": []})
            continue
        if actual is None or c[1] in ("", "Campo"):
            continue
        if re.match(r"^\d+( al \d+)?$", c[1]):
            actual["campos"].append({
                "campo": c[1], "longitud": c[2], "obligatorio": c[3], "llave_unica": c[4],
                "descripcion": c[5], "formato": c[6], "observaciones": c[7],
            })
        elif c[1].startswith("(") or actual["notas"]:
            actual["notas"].append(c[1])
    return libros


def tablas_generales(ws) -> dict:
    tablas: dict[str, dict] = {}
    actual = None
    for row in ws.iter_rows(values_only=True, max_col=6):
        c = [txt(v) for v in row] + [""] * 6
        m = re.match(r"(?i)^TABLA\s+(\d+)\s*[:\"]?\s*(.*)$", c[1])
        if m:
            actual = None if m.group(1) in TABLAS_EXCLUIDAS else tablas.setdefault(
                m.group(1), {"titulo": c[1], "columnas": None, "items": []})
            continue
        if actual is None or not c[1]:
            continue
        if actual["columnas"] is None:
            actual["columnas"] = [x for x in c[1:5] if x]
            continue
        actual["items"].append({"codigo": c[1], "descripcion": c[2], **({"extra": c[3]} if c[3] else {})})
    return tablas


def reglas_tabla10(ws) -> list[list[str]]:
    out = []
    for i, row in enumerate(ws.iter_rows(values_only=True, max_col=26), 1):
        if i >= 3:
            fila = [txt(v) for v in row]
            if any(fila):
                out.append(fila)
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    pl = plantillas()
    (OUT / "plantillas-columnas.json").write_text(json.dumps(pl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    wb = openpyxl.load_workbook(MACRO, read_only=True, data_only=True, keep_vba=False)
    faltan = HOJAS_PERMITIDAS - set(wb.sheetnames)
    if faltan:
        raise SystemExit(f"Hojas no encontradas: {faltan}")
    ple = estructura_ple(wb["Estructura"])
    tablas = tablas_generales(wb["Tablas Generales"])
    reglas = reglas_tabla10(wb["Reglas"])
    fuente = {"archivo": f"Git/{MACRO.name}", "tipo": "plantilla comunitaria (no oficial)",
              "nota": "Archivo idéntico (mismo SHA-256) a 'Macro excel ... MOD (1).xlsm'."}
    (OUT / "estructura-ple.json").write_text(json.dumps({"fuente": fuente, "libros": ple}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "tablas-ple.json").write_text(json.dumps({"fuente": fuente, "tablas": tablas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for libro, datos in ple.items():
        with open(OUT / f"estructura-ple-{libro.replace('.', '-')}.csv", "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(datos["campos"][0]))
            w.writeheader()
            w.writerows(datos["campos"])
    with open(OUT / "reglas-generales-tabla10.csv", "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(reglas)

    for k, v in pl.items():
        print(f"plantilla {k}: {len(v['columnas'])} columnas")
    for k, v in ple.items():
        print(f"PLE {k}: {len(v['campos'])} campos, {len(v['notas'])} notas")
    print("tablas PLE:", ", ".join(f"{k}({len(v['items'])})" for k, v in sorted(tablas.items(), key=lambda x: int(x[0]))))
    print(f"reglas tabla 10: {len(reglas)} filas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
