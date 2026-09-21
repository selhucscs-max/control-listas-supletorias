#!/usr/bin/env python3
"""
Regenera el bloque "DATOS POR DEFECTO — CARRERA PROFESIONAL" embebido en
index.html a partir de CARRERA_PREVISION.ods.

Uso:
    python3 scripts/generate_carrera_data.py [ruta_ods] [ruta_index_html]

Por defecto usa CARRERA_PREVISION.ods e index.html en la raíz del repo.

El .ods tiene una estructura de bloques repetidos: por cada convocatoria hay
una fila de cabecera de bloque ("CARRERA / PROVISIONAL / DEFINITIVA"), una
fila de cabecera de columnas ("CONVOCATORIA / COMISIÓN / 1º SESIÓN / ..."),
y luego una fila por comisión. Este script no depende del número de bloques
ni de comisiones: vuelca la hoja entera como una rejilla (lista de listas,
igual que XLSX.utils.sheet_to_json(ws,{header:1}) en el navegador) para que
el parser JS parseCarreraSheet() —usado también al arrastrar un archivo o al
cargar CARRERA_PREVISION.ods en vivo— sea la única fuente de verdad sobre
qué filas son de datos y qué columnas son qué hito.
"""
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

import pandas as pd


def load_grid(ods_path: Path):
    df = pd.read_excel(ods_path, sheet_name=0, header=None, engine="odf")
    if df.empty:
        raise SystemExit(f"'{ods_path}' está vacío")

    grid = []
    for _, row in df.iterrows():
        vals = []
        for v in row.tolist():
            if v is None or (isinstance(v, float) and pd.isna(v)):
                vals.append(None)
            elif isinstance(v, (datetime, date)):
                vals.append(v.strftime("%Y-%m-%d"))
            else:
                vals.append(v)
        grid.append(vals)
    return grid


def replace_default_data(html: str, grid: list) -> str:
    grid_json = json.dumps(grid, ensure_ascii=False, separators=(",", ":"))
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    # Cuenta filas de datos reales (con CONVOCATORIA y COMISIÓN en col. 0 y 1,
    # descartando cabeceras de bloque/columna) solo para el comentario.
    n = 0
    for row in grid:
        if not row or len(row) < 2:
            continue
        c0 = str(row[0]).strip() if row[0] is not None else ""
        c1 = str(row[1]).strip() if row[1] is not None else ""
        if not c0 or not c1:
            continue
        if c0.upper().startswith("CARRERA") or c0.upper().startswith("CONVOCATORIA"):
            continue
        if c1.upper().startswith("COMISI"):
            continue
        n += 1

    comment_pattern = re.compile(
        r"// Generado automáticamente \(Carrera Profesional\) el .*? · \d+ procesos? \(convocatoria × comisión\)"
    )
    plural = "procesos" if n != 1 else "proceso"
    new_comment = f"// Generado automáticamente (Carrera Profesional) el {now} · {n} {plural} (convocatoria × comisión)"
    if not comment_pattern.search(html):
        raise SystemExit(
            "No se encontró el comentario 'Generado automáticamente (Carrera Profesional)' en index.html"
        )
    html = comment_pattern.sub(new_comment, html, count=1)

    grid_pattern = re.compile(
        r"(\(function initDefaultCarrera\(\)\{\n\s*const carreraGrid = )\[.*?\](;)"
    )
    if not grid_pattern.search(html):
        raise SystemExit("No se encontró el array 'const carreraGrid = [...]' en index.html")
    html = grid_pattern.sub(lambda m: m.group(1) + grid_json + m.group(2), html, count=1)

    return html


def main():
    repo_root = Path(__file__).resolve().parent.parent
    ods_path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "CARRERA_PREVISION.ods"
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo_root / "index.html"

    grid = load_grid(ods_path)
    html = html_path.read_text(encoding="utf-8")
    new_html = replace_default_data(html, grid)
    html_path.write_text(new_html, encoding="utf-8")
    print(f"OK: {len(grid)} filas de la hoja (Carrera Profesional) escritas en {html_path.name}")


if __name__ == "__main__":
    main()
