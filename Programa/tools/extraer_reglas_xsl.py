"""Extrae las reglas de validación de las hojas XSL de SUNAT (Git/XSL Actualizado al 06092022 (1)/validaciones).

Cada <xsl:call-template> con parámetros node / errorCode* / regexp / catalogo / expresion se registra como
una regla: documento, archivo, línea, plantilla, contexto (último template match / for-each select
previo; heurístico, no resuelve anidamientos), nodo (XPath relativo al contexto), expresión regular,
catálogo, códigos de error y el comentario '<!-- ... ERROR nnnn -->' más cercano.

Solo lee Git/ (solo lectura). No ejecuta las XSL (usan extensiones IBM DataPower).
Salida: Programa/referencias/sunat-xsl/reglas-xsl.csv          Uso: python tools/extraer_reglas_xsl.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
XSL_DIR = RAIZ / "Git" / "XSL Actualizado al 06092022 (1)" / "validaciones"
OUT = RAIZ / "Programa" / "referencias" / "sunat-xsl"

# Hoja XSL -> documento (las demás se extraen igual, marcadas como fuera de alcance)
DOCUMENTOS = {
    "ValidaExprRegFactura-2.0.1.xsl": "Factura (01)",
    "ValidaExprRegBoleta-2.0.1.xsl": "Boleta (03)",
    "ValidaExprRegNC-2.0.1.xsl": "Nota de crédito (07)",
    "ValidaExprRegND-2.0.1.xsl": "Nota de débito (08)",
    "ValidaExprRegSummary-1.1.0.xsl": "Resumen diario (RC) v1.1",
    "ValidaExprRegSummary-1.0.1.xsl": "Resumen diario (RC) v1.0",
    "ValidaExprRegSummaryVoided-1.0.1.xsl": "Comunicación de baja (RA)",
    "ValidaExprRegOtrosVoided-1.0.1.xsl": "Reversión/baja de otros CPE (RR)",
    "ValidaExprRegAdquiriente-2.0.1.xsl": "Adquirente (padrón)",
    "ValidaExprRegAdqOtros-2.0.1.xsl": "Adquirente (otros)",
    "ValidaExprRegOperador-2.0.1.xsl": "Operador (OSE)",
}
COLUMNAS = ["documento", "archivo", "linea", "plantilla", "contexto", "nodo", "regexp", "catalogo", "codigos_error", "comentario"]

RE_CALL = re.compile(r'<xsl:call-template\s+name="([^"]+)"\s*>(.*?)</xsl:call-template>', re.S)
RE_PARAM = re.compile(r'<xsl:with-param\s+name="([^"]+)"\s+select="(.*?)"\s*/>', re.S)
RE_COMENT = re.compile(r"<!--(.*?)-->", re.S)
RE_CONTEXTO = re.compile(r'<xsl:(?:template\s+match|for-each\s+select)="([^"]+)"')


def quitar_comillas(v: str) -> str:
    v = v.strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == "'" else v


def extraer(path: Path) -> list[dict]:
    texto = path.read_text(encoding="utf-8", errors="replace")
    filas = []
    for m in RE_CALL.finditer(texto):
        params = {k: quitar_comillas(v) for k, v in RE_PARAM.findall(m.group(2))}
        codigos = sorted({v for k, v in params.items() if k.startswith("errorCode") and re.fullmatch(r"\d{4}", v)})
        if not codigos:
            continue
        previo = texto[max(0, m.start() - 600):m.start()]
        ctx = RE_CONTEXTO.findall(texto, 0, m.start())
        contexto = ctx[-1] if ctx else ""
        coment = [c.strip() for c in RE_COMENT.findall(previo) if "ERROR" in c.upper()]
        filas.append({
            "documento": DOCUMENTOS.get(path.name, "fuera de alcance"),
            "archivo": path.name,
            "linea": texto.count("\n", 0, m.start()) + 1,
            "plantilla": m.group(1),
            "contexto": contexto,
            "nodo": params.get("node", params.get("idCatalogo", "")),
            "regexp": params.get("regexp", ""),
            "catalogo": params.get("catalogo", ""),
            "codigos_error": " ".join(codigos),
            "comentario": re.sub(r"\s+", " ", coment[-1])[:200] if coment else "",
        })
    return filas


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if not XSL_DIR.exists():
        print(f"No existe {XSL_DIR}")
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    todas: list[dict] = []
    for f in sorted(XSL_DIR.glob("*.xsl")):
        filas = extraer(f)
        todas += filas
        print(f"{f.name}: {len(filas)} reglas con código de error")
    with open(OUT / "reglas-xsl.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(todas)
    print(f"Total: {len(todas)} reglas; códigos distintos: {len({c for r in todas for c in r['codigos_error'].split()})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
