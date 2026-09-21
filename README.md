# Dashboard SUPLE · Servicio de Selección, Evaluación y Formación (CHUC / SCS)

Dashboard interactivo autocontenido (un único `index.html`) con **4 módulos**, accesibles desde una pantalla selectora tras introducir la clave de acceso.

## Módulos

### 1. Listas Supletorias (SUPLE)
- 8 pestañas: Resumen general, Estado actual, Por año, Por categoría, Gestión/Tiempos (P50/P75/P95, con Gantt de Baremación), Datos completos, entre otras.
- 381 convocatorias (2020–2026).
- Filtro global de año + estado, serializado en la URL.
- Datos por defecto embebidos desde `CONTROL_SUPLES.ods`.

### 2. Ayudas de Acción Social
- 4 pestañas: Resumen, Por año, Evolución, Datos.
- Datos por defecto embebidos desde `Indicadores.ods`.

### 3. Carrera Profesional
- 6 pestañas: Resumen, Cronograma (Gantt), Agenda, Calendario, Plazos/avisos, Datos.
- Sigue el estado de cada proceso (convocatoria × comisión) a través de sus hitos (sesiones, firma de actas, publicaciones provisional/definitiva) y valida automáticamente 5 reglas de plazos (firma ≤ 7 días, alegaciones ≈ 10 días hábiles, revisión 7–14 días, envío→publicación 10–15 días).
- Datos por defecto embebidos desde `CARRERA_PREVISION.ods`. El parser (`parseCarreraSheet`) no depende del número de convocatorias/comisiones: reconoce automáticamente las filas de datos, así que añadir nuevas convocatorias o comisiones al `.ods` no requiere tocar código.

### 4. Formación
- Catálogo de actividades formativas gestionadas por el Servicio de Selección, Evaluación y Formación.
- Filtros por dirección/servicio, modalidad (Presencial/Online/Mixto) y búsqueda por título/código.
- Datos por defecto embebidos (191 actividades a fecha de la última generación).

## Patrón "tambor" (auto-actualización de datos)

Cada módulo con fuente `.ods` (SUPLE, Acción Social, Carrera Profesional) sigue el mismo patrón:

1. **Datos por defecto embebidos** en `index.html` (funcionan sin conexión, sirven de respaldo).
2. **Auto-carga en vivo**: al abrir el dashboard, un script al final de `<body>` intenta descargar el `.ods` correspondiente (mismo origen) y, si lo encuentra, sustituye los datos por defecto por los del archivo en vivo — sin tocar código.
3. **Importación manual**: arrastra y suelta un `.ods`/`.xlsx`/`.csv` desde el botón de importación de cada módulo para cargar datos puntuales (se guardan en `localStorage`, no se suben a ningún sitio).
4. **Script de regeneración** (`scripts/generate_data.py`, `generate_accion_data.py`, `generate_carrera_data.py`): reescribe los datos por defecto embebidos en `index.html` a partir del `.ods` correspondiente.
5. **GitHub Action** (`.github/workflows/actualizar-dashboard.yml`): al subir una nueva versión de `CONTROL_SUPLES.ods`, `Indicadores.ods` o `CARRERA_PREVISION.ods` al repositorio, regenera automáticamente `index.html` y lo commitea.

El módulo de Formación no sigue este patrón (su fuente original era un HTML con datos embebidos, no una hoja de cálculo); sus datos por defecto se actualizan regenerando manualmente el bloque `initDefaultFormacion` en `index.html`.

## Acceso

- Clave de acceso: **`255623`** (filtro casual, no es seguridad real — ver más abajo).
- Identidad visual: SCS · azul `#0055A5`.

## Subir a GitHub Pages / actualizar el repositorio

1. En el repo, pulsa **Add file → Upload files**.
2. Arrastra los archivos que hayan cambiado (típicamente `index.html`, y si procede el `.ods` actualizado, el script `generate_*.py` correspondiente, y `.github/workflows/actualizar-dashboard.yml`).
3. Commit directamente a `main`.
4. GitHub Pages se actualiza solo en 1–2 minutos.

## ⚠️ Sobre la "clave de acceso"

La clave (`255623`) está embebida en el HTML como filtro de acceso casual. **No es seguridad real**: cualquier persona que abra el código fuente (F12) puede verla. Sirve para evitar accesos accidentales, no para proteger información sensible.

Si necesitas seguridad real: aloja el dashboard en un servicio con autenticación (intranet del SCS, Cloudflare Access, Netlify Identity, etc.), o usa un repositorio **privado** + GitHub Pages con plan de pago.

## Cambiar la clave de acceso

Edita `index.html`, busca `const ACCESS_KEY = "255623";` y sustituye el valor.

## Estructura del repositorio

```
.
├── index.html                              # Dashboard completo (HTML + CSS + JS + datos de los 4 módulos)
├── CONTROL_SUPLES.ods                      # Fuente de datos · Listas Supletorias
├── Indicadores.ods                         # Fuente de datos · Acción Social
├── CARRERA_PREVISION.ods                   # Fuente de datos · Carrera Profesional
├── scripts/
│   ├── generate_data.py                    # Regenera datos por defecto (SUPLE)
│   ├── generate_accion_data.py             # Regenera datos por defecto (Acción Social)
│   └── generate_carrera_data.py            # Regenera datos por defecto (Carrera Profesional)
├── .github/workflows/actualizar-dashboard.yml   # Regenera y commitea index.html automáticamente
└── README.md                               # Este archivo
```

## Licencia / uso

Uso interno · Servicio de Selección, Evaluación y Formación · CHUC / Servicio Canario de la Salud.
