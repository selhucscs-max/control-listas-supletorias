#!/usr/bin/env python3
"""
Regenera el bloque "DATOS POR DEFECTO — ACCIÓN SOCIAL" embebido en index.html
a partir de Indicadores.ods.

Uso:
    python3 scripts/generate_accion_data.py [ruta_ods] [ruta_index_html]

Por defecto usa Indicadores.ods e index.html en la raíz del repo.

El .ods tiene una tabla "ancha": una fila de cabecera con el título y los
años en columnas, y una fila por métrica (Total de Participantes,
Reclamaciones, Admitidos Definitivos, Excluidos Definitivos). Este script
la transforma en una fila "larga" por año — un objeto JSON por convocatoria
anual — para que sea trivial de consumir desde el dashboard (igual formato
que usa handleFileAccion()/parseAccionSheet() en index.html al importar el
archivo a mano).
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Etiqueta de fila (tal y como aparece en el .ods, en minúsculas y sin
# acentos no es necesario porque comparamos con 'in') -> clave canónica.
METRIC_MAP = [
    ("participante", "PARTICIPANTES"),
    ("reclamacion", "RECLAMACIONES"),
    ("admitido", "ADMITIDOS"),
    ("excluido", "EXCLUIDOS"),
]


def normalize_metric(label: str):
    s = str(label).strip().lower()
    for needle, key in METRIC_MAP:
        if needle in s:
            return key
    return None


def load_rows(ods_path: Path):
    df = pd.read_excel(ods_path, sheet_name=0, header=None, engine="odf")
    if df.empty:
        raise SystemExit(f"'{ods_path}' está vacío")

    header = df.iloc[0].tolist()
    # Columna 0 = etiqueta de la tabla ("Convocatoria de Ayudas de Acción
    # Social..."), columnas 1..n = años.
    year_cols = []
    for i, v in enumerate(header[1:], start=1):
        try:
            year = int(float(v))
        except (TypeError, ValueError):
            continue
        year_cols.append((i, year))
    if not year_cols:
        raise SystemExit(f"No se encontraron columnas de año en la cabecera de '{ods_path}'")

    by_year = {year: {"AÑO": year} for _, year in year_cols}

    for _, row in df.iloc[1:].iterrows():
        label = row[0]
        if label is None or (isinstance(label, float) and pd.isna(label)):
            continue
        key = normalize_metric(label)
        if key is None:
            continue
        for col_i, year in year_cols:
            v = row[col_i] if col_i < len(row) else None
            if v is None or (isinstance(v, float) and pd.isna(v)):
                by_year[year][key] = None
                continue
            try:
                f = float(v)
                by_year[year][key] = int(f) if f.is_integer() else f
            except (TypeError, ValueError):
                by_year[year][key] = str(v).strip()

    rows = [by_year[y] for _, y in sorted(year_cols, key=lambda t: t[1])]
    # Asegurar las 4 claves en todas las filas (por si falta alguna métrica)
    for r in rows:
        for _, key in METRIC_MAP:
            r.setdefault(key, None)
    return rows


def replace_default_data(html: str, rows: list) -> str:
    rows_json = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    n = len(rows)

    comment_pattern = re.compile(
        r"// Generado automáticamente \(Acción Social\) el .*? · \d+ convocatorias anuales"
    )
    new_comment = f"// Generado automáticamente (Acción Social) el {now} · {n} convocatorias anuales"
    if not comment_pattern.search(html):
        raise SystemExit(
            "No se encontró el comentario 'Generado automáticamente (Acción Social)' en index.html"
        )
    html = comment_pattern.sub(new_comment, html, count=1)

    rows_pattern = re.compile(
        r"(\(function initDefaultAccion\(\)\{\n\s*const accionRows = )\[.*?\](;)"
    )
    if not rows_pattern.search(html):
        raise SystemExit("No se encontró el array 'const accionRows = [...]' en index.html")
    html = rows_pattern.sub(lambda m: m.group(1) + rows_json + m.group(2), html, count=1)

    return html


def main():
    repo_root = Path(__file__).resolve().parent.parent
    ods_path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "Indicadores.ods"
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo_root / "index.html"

    rows = load_rows(ods_path)
    html = html_path.read_text(encoding="utf-8")
    new_html = replace_default_data(html, rows)
    html_path.write_text(new_html, encoding="utf-8")
    print(f"OK: {len(rows)} convocatorias anuales (Acción Social) escritas en {html_path.name}")


if __name__ == "__main__":
    main()
