#!/usr/bin/env python3
"""
Regenera el bloque "DATOS POR DEFECTO" embebido en index.html a partir de
CONTROL_SUPLES.ods (hoja "1_Datos_generales").

Uso:
    python3 scripts/generate_data.py [ruta_ods] [ruta_index_html]

Por defecto usa CONTROL_SUPLES.ods e index.html en la raíz del repo.

Este script replica exactamente la misma selección de columnas y el mismo
criterio de filtrado ("AÑO" no vacío e "ID" no vacío) que usa la propia
página al importar un archivo manualmente (función handleFile /
processRows en index.html), de forma que los "datos por defecto" queden
siempre equivalentes a lo que se vería si alguien importara el .ods a mano.
"""
import json
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# Época de los números de serie de fecha de Excel/ODS (día 0 = 30/12/1899).
EXCEL_EPOCH = datetime(1899, 12, 30)

SHEET_NAME = "1_Datos_generales"

# Mismas columnas que usa processRows() en index.html (ver r['...']),
# en este orden para mantener el bloque legible.
COLUMNS = [
    "AÑO",
    "ID",
    "CATEGORIA",
    "AREA",
    "DIRECCION",
    "PRESENTADOS",
    "ADMITIDOS PROV",
    "EXCLUIDOS PROV",
    "ADMITIDOS DEF",
    "EXCLUIDOS DEF",
    "N.º RECL 1",
    "N.º RECL 2",
    "TIEMPO EN RESOLVER (días)",
    "PUBL BASES",
    "FECHA BASES",
    "PUBL AD&EX PROV",
    "FECHA RG AD&EX PROV",
    "PUBL RG LISTA PROV",
    "FECHA RG LISTA PROV",
    "PUBL LISTA DEF",
    "FECHA RG LISTA DEF",
    "RG BASES",
    "RG LISTA DEF",
]

DATE_COLUMNS = {
    "PUBL BASES", "FECHA BASES",
    "PUBL AD&EX PROV", "FECHA RG AD&EX PROV",
    "PUBL RG LISTA PROV", "FECHA RG LISTA PROV",
    "PUBL LISTA DEF", "FECHA RG LISTA DEF",
}

NUMERIC_COLUMNS = {
    "PRESENTADOS", "ADMITIDOS PROV", "EXCLUIDOS PROV",
    "ADMITIDOS DEF", "EXCLUIDOS DEF",
    "N.º RECL 1", "N.º RECL 2",
    "TIEMPO EN RESOLVER (días)",
}


def is_blank(v):
    if v is None:
        return True
    if isinstance(v, float) and math.isnan(v):
        return True
    try:
        if pd.isna(v):
            return True
    except (TypeError, ValueError):
        pass
    if isinstance(v, str) and v.strip() == "":
        return True
    return False


def clean_cell(col, v):
    if is_blank(v):
        return None
    if col in DATE_COLUMNS:
        if isinstance(v, (pd.Timestamp, datetime)):
            return v.strftime("%Y-%m-%d")
        # Celda mal tipada como número (en vez de fecha) en el .ods: viene
        # como el número de serie de Excel/ODS (p.ej. 46167 = 25/05/2026).
        # Sin esto, se cuela el número tal cual y el navegador lo interpreta
        # como si fuese literalmente el año 46167.
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            if 20000 <= v < 60000:
                return (EXCEL_EPOCH + timedelta(days=v)).strftime("%Y-%m-%d")
        s = str(v).strip()
        if re.fullmatch(r"\d+(\.\d+)?", s):
            serial = float(s)
            if 20000 <= serial < 60000:
                return (EXCEL_EPOCH + timedelta(days=serial)).strftime("%Y-%m-%d")
        parsed = pd.to_datetime(s, errors="coerce", dayfirst=False)
        if pd.isna(parsed):
            return s
        return parsed.strftime("%Y-%m-%d")
    if col in NUMERIC_COLUMNS:
        try:
            f = float(v)
            if f.is_integer():
                return int(f)
            return f
        except (TypeError, ValueError):
            # valores no numéricos (p.ej. errores de fórmula tipo #¡REF!)
            # se dejan pasar tal cual: el dashboard los trata como 0
            # (misma lógica que al importar el archivo manualmente).
            return str(v).strip()
    if col == "AÑO":
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return v
    return str(v).strip()


def load_rows(ods_path: Path):
    df = pd.read_excel(ods_path, sheet_name=SHEET_NAME, engine="odf")
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in ("AÑO", "ID") if c not in df.columns]
    if missing:
        raise SystemExit(f"Faltan columnas obligatorias en '{SHEET_NAME}': {missing}")

    valid_mask = df["AÑO"].notna() & df["ID"].notna() & (df["ID"].astype(str).str.strip() != "")
    df = df[valid_mask]

    rows = []
    for _, r in df.iterrows():
        row = {}
        for col in COLUMNS:
            raw = r[col] if col in df.columns else None
            row[col] = clean_cell(col, raw)
        rows.append(row)
    return rows


def replace_default_data(html: str, rows: list) -> str:
    rows_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    n = len(rows)

    comment_pattern = re.compile(
        r"// Generado automáticamente el .*? · \d+ convocatorias"
    )
    new_comment = f"// Generado automáticamente el {now} · {n} convocatorias"
    if not comment_pattern.search(html):
        raise SystemExit("No se encontró el comentario 'Generado automáticamente' en index.html")
    html = comment_pattern.sub(new_comment, html, count=1)

    rows_pattern = re.compile(r"(\(function initDefault\(\)\{\n\s*const rows = )\[.*?\](;)")
    if not rows_pattern.search(html):
        raise SystemExit("No se encontró el array 'const rows = [...]' en index.html")
    html = rows_pattern.sub(lambda m: m.group(1) + rows_json + m.group(2), html, count=1)

    return html


def main():
    repo_root = Path(__file__).resolve().parent.parent
    ods_path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "CONTROL_SUPLES.ods"
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo_root / "index.html"

    rows = load_rows(ods_path)
    html = html_path.read_text(encoding="utf-8")
    new_html = replace_default_data(html, rows)
    html_path.write_text(new_html, encoding="utf-8")
    print(f"OK: {len(rows)} convocatorias escritas como datos por defecto en {html_path.name}")


if __name__ == "__main__":
    main()
