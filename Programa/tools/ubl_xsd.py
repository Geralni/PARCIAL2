"""Resolución de rutas (XPath simples) contra los XSD de UBL.

Uso: módulo de apoyo de verificar_matriz.py y generar_mapa_xsd.py.
Solo lee los XSD (carpeta Git/, de solo lectura). No contiene lógica de negocio.

Limitaciones conocidas (documentadas en specs/02-dominio-y-contratos/mapa-xsd.md):
- Soporta rutas absolutas del tipo /Raiz/pfx:Elem/.../@atributo, sin predicados.
- Dentro de ext:ExtensionContent (xsd:any) solo comprueba que el elemento exista
  como declaración global en algún XSD cargado (p. ej. ds:Signature).
- Los documentos SUNAT SummaryDocuments / VoidedDocuments (prefijo sac:) no tienen
  XSD en el workspace: se informan como NO_XSD.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

XSD = "http://www.w3.org/2001/XMLSchema"
NS = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "udt": "urn:oasis:names:specification:ubl:schema:xsd:UnqualifiedDataTypes-2",
}
ROOTS = {
    "Invoice": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "CreditNote": "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2",
    "DebitNote": "urn:oasis:names:specification:ubl:schema:xsd:DebitNote-2",
}
SIN_XSD = {"SummaryDocuments", "VoidedDocuments"}
ANY = ("##any", "##any")

# XSD principal: OASIS UBL 2.1 OS (el que exige el Anexo 9-A). 2.2 se usa como verificación cruzada.
DEFAULT_XSD_DIR = Path(__file__).resolve().parents[2] / "Git" / "UBL-2.1" / "xsd"
XSD_DIR_22 = (
    Path(__file__).resolve().parents[2]
    / "Git" / "tradeshift-ubl-xsd" / "src" / "main" / "resources"
    / "org" / "oasis-open" / "ubl" / "schemas"
)
VERSION = {DEFAULT_XSD_DIR: "2.1", XSD_DIR_22: "2.2"}


@dataclass
class Resultado:
    xpath: str
    estado: str  # OK | NO_EXISTE | NO_XSD | SINTAXIS
    detalle: str = ""
    cardinalidades: list[str] = field(default_factory=list)
    tipo: str = ""

    @property
    def ok(self) -> bool:
        return self.estado == "OK"


def _qname(text: str, prefixes: dict[str, str], default_ns: str) -> tuple[str, str]:
    if ":" in text:
        pfx, local = text.split(":", 1)
        return prefixes.get(pfx, pfx), local
    return default_ns, text


def _card(node: ET.Element) -> str:
    mn = node.get("minOccurs", "1")
    mx = node.get("maxOccurs", "1")
    return f"{mn}..{'n' if mx == 'unbounded' else mx}"


class EsquemaUBL:
    """Índice de elementos globales y tipos complejos de todos los XSD de la carpeta."""

    def __init__(self, xsd_dir: Path | str = DEFAULT_XSD_DIR):
        self.dir = Path(xsd_dir)
        self.elements: dict[tuple[str, str], tuple[tuple[str, str] | None, ET.Element, dict, str]] = {}
        self.ctypes: dict[tuple[str, str], tuple[ET.Element, dict, str]] = {}
        self.archivos: list[Path] = sorted(self.dir.rglob("*.xsd"))
        if not self.archivos:
            raise FileNotFoundError(f"No hay XSD en {self.dir}")
        for f in self.archivos:
            self._cargar(f)

    def _cargar(self, path: Path) -> None:
        prefixes: dict[str, str] = {}
        for ev, data in ET.iterparse(path, events=("start-ns",)):
            pfx, uri = data
            prefixes.setdefault(pfx, uri)
        root = ET.parse(path).getroot()
        tns = root.get("targetNamespace", "")
        for el in root.findall(f"{{{XSD}}}element"):
            t = el.get("type")
            tkey = _qname(t, prefixes, tns) if t else None
            self.elements[(tns, el.get("name"))] = (tkey, el, prefixes, tns)
        for ct in root.findall(f"{{{XSD}}}complexType"):
            self.ctypes[(tns, ct.get("name"))] = (ct, prefixes, tns)

    # ---------- consultas ----------
    def tipo_de(self, ekey: tuple[str, str]) -> tuple[str, str] | None:
        info = self.elements.get(ekey)
        return info[0] if info else None

    def hijos(self, tkey: tuple[str, str]) -> list[tuple[tuple[str, str], str]]:
        """Elementos hijos (clave, cardinalidad) de un tipo complejo, incluida la herencia."""
        entry = self.ctypes.get(tkey)
        if not entry:
            return []
        ct, prefixes, tns = entry
        out: list[tuple[tuple[str, str], str]] = []
        for ext in ct.iter(f"{{{XSD}}}extension"):
            if ext.get("base"):
                out.extend(self.hijos(_qname(ext.get("base"), prefixes, tns)))
        for node in ct.iter():
            if node.tag == f"{{{XSD}}}element":
                ref = node.get("ref")
                key = _qname(ref, prefixes, tns) if ref else (tns, node.get("name"))
                out.append((key, _card(node)))
            elif node.tag == f"{{{XSD}}}any":
                out.append((ANY, _card(node)))
        return out

    def atributos(self, tkey: tuple[str, str] | None, _visto: set | None = None) -> set[str]:
        if tkey is None:
            return set()
        _visto = _visto or set()
        if tkey in _visto:
            return set()
        _visto.add(tkey)
        entry = self.ctypes.get(tkey)
        if not entry:
            return set()
        ct, prefixes, tns = entry
        attrs = {a.get("name") or a.get("ref") for a in ct.iter(f"{{{XSD}}}attribute")}
        for tag in ("extension", "restriction"):
            for b in ct.iter(f"{{{XSD}}}{tag}"):
                if b.get("base"):
                    attrs |= self.atributos(_qname(b.get("base"), prefixes, tns), _visto)
        return {a for a in attrs if a}

    def base_udt(self, tkey: tuple[str, str] | None) -> str:
        """Nombre del tipo udt: base (p. ej. udt:AmountType) para la columna 'tipo'."""
        seen = 0
        while tkey and seen < 10:
            if tkey[0] == NS["udt"]:
                return f"udt:{tkey[1]}"
            entry = self.ctypes.get(tkey)
            if not entry:
                return f"{tkey[1]}"
            ct, prefixes, tns = entry
            base = None
            for tag in ("extension", "restriction"):
                b = ct.find(f".//{{{XSD}}}{tag}")
                if b is not None and b.get("base"):
                    base = _qname(b.get("base"), prefixes, tns)
                    break
            if base is None:
                return tkey[1]
            tkey, seen = base, seen + 1
        return tkey[1] if tkey else ""

    # ---------- resolución de rutas ----------
    def resolver(self, xpath: str) -> Resultado:
        xp = xpath.strip()
        if not xp.startswith("/"):
            return Resultado(xpath, "SINTAXIS", "La ruta debe empezar con '/'")
        partes = [p for p in xp.split("/") if p]
        raiz = partes[0]
        if raiz in SIN_XSD:
            return Resultado(xpath, "NO_XSD", f"{raiz} es un documento SUNAT sin XSD en el workspace")
        if raiz not in ROOTS:
            return Resultado(xpath, "SINTAXIS", f"Raíz desconocida: {raiz}")
        ekey = (ROOTS[raiz], raiz)
        tkey = self.tipo_de(ekey)
        cards: list[str] = []
        en_any = False
        for i, seg in enumerate(partes[1:], start=1):
            if seg.startswith("@"):
                if i != len(partes) - 1:
                    return Resultado(xpath, "SINTAXIS", "El atributo debe ser el último segmento")
                nombre = seg[1:]
                if en_any:
                    return Resultado(xpath, "OK", "atributo dentro de extensión (no verificable)", cards)
                if nombre in self.atributos(tkey):
                    return Resultado(xpath, "OK", "", cards, self.base_udt(tkey))
                return Resultado(xpath, "NO_EXISTE", f"atributo @{nombre} no existe en {tkey[1] if tkey else '?'}", cards)
            if ":" not in seg:
                return Resultado(xpath, "SINTAXIS", f"Segmento sin prefijo: {seg}")
            pfx, local = seg.split(":", 1)
            if pfx == "sac":
                return Resultado(xpath, "NO_XSD", "prefijo sac: (extensión SUNAT) sin XSD en el workspace", cards)
            if pfx not in NS:
                return Resultado(xpath, "SINTAXIS", f"Prefijo desconocido: {pfx}")
            key = (NS[pfx], local)
            if en_any:
                if key not in self.elements:
                    return Resultado(xpath, "NO_EXISTE", f"{seg} no está declarado globalmente", cards)
                cards.append("any")
                tkey, en_any = self.tipo_de(key), False
                continue
            hijos = self.hijos(tkey) if tkey else []
            match = [c for k, c in hijos if k == key]
            if not match:
                if any(k == ANY for k, _ in hijos):
                    en_any = True
                    if key in self.elements:
                        cards.append("any")
                        tkey, en_any = self.tipo_de(key), False
                        continue
                return Resultado(xpath, "NO_EXISTE", f"{seg} no es hijo de {tkey[1] if tkey else '?'}", cards)
            cards.append(match[0])
            tkey = self.tipo_de(key)
        return Resultado(xpath, "OK", "", cards, self.base_udt(tkey))
