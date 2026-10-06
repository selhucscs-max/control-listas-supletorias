# 📅 Sincronización con Google Calendar

Tu dashboard ahora sincroniza automáticamente todas las fechas de `CONTROL_SUPLES.ods` con tu calendario de Google "suple".

## ⚡ Instalación en 3 minutos

### Paso 1: Crear Google Cloud Project (2 min)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. **Crear proyecto** → Nombre: `SUPLES Dashboard`
3. Busca **"Google Calendar API"** → Habilitar
4. En el menú lateral: **Credenciales** → **Crear credenciales**
   - Tipo: **Service Account**
   - Nombre: `suples-sync`
   - ID de servicio: `suples-sync@...`
   - Clic en **Crear y continuar**
5. En la sección "Clave":
   - **Crear clave** → JSON
   - Se descarga un archivo `...json`

### Paso 2: Compartir calendario con la Service Account (30 seg)

1. En [Google Calendar](https://calendar.google.com/)
2. Haz clic derecho en el calendario "suple" → **Configuración**
3. Ve a **Compartir con personas y grupos**
4. **Agregar personas**: Pega el email de tu service account
   - Lo encuentras en el JSON descargado: `"client_email": "suples-sync@..."`
   - Dale permisos: **Hacer cambios en eventos**

### Paso 3: Agregar Secrets a GitHub (1 min)

1. Ve a tu repo en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Clic en **New repository secret** y añade estos dos:

#### Secret 1: `GOOGLE_CALENDAR_CREDENTIALS`
- **Value**: El contenido COMPLETO del archivo JSON descargado
- Pégalo tal cual, entre llaves `{...}`

#### Secret 2: `GOOGLE_CALENDAR_ID`
- **Value**: El ID de tu calendario "suple"
- Lo encuentras en [Google Calendar](https://calendar.google.com/):
  - Click derecho en "suple" → **Configuración** → Baja hasta encontrar **"ID del calendario"**
  - Parece: `usuario@gmail.com` o `abcd123efgh456@group.calendar.google.com`

---

## ✅ Listo, ¡funciona automáticamente!

Cada vez que hagas push a `CONTROL_SUPLES.ods`, GitHub Actions:
1. ✨ Genera los datos JSON del dashboard
2. 📅 Sincroniza automáticamente las fechas con Google Calendar
3. 📝 Crea un commit con los cambios

### Qué se sincroniza:

| Columna del .ods | Evento en Google Calendar |
|------------------|--------------------------|
| `FECHA BASES` | 📋 Publicación de bases |
| `FECHA RG AD&EX PROV` | ✏️ Resultado Ad&Ex provisional |
| `FECHA RG LISTA PROV` | 📄 Publicación lista provisional |
| `FECHA RG LISTA DEF` | ✅ Publicación lista definitiva |

---

## 🔍 Verificar que funciona

1. Haz un pequeño cambio en `CONTROL_SUPLES.ods` (ej: cambia una fecha o un número)
2. Commit y push a GitHub
3. Ve a **Actions** → Verás el workflow ejecutándose
4. Una vez termine, abre Google Calendar → Los eventos estarán actualizados ✅

---

## ❓ Troubleshooting

**"Variable de entorno GOOGLE_CALENDAR_CREDENTIALS no configurada"**
- ✅ Verifica que el Secret se llama exactamente `GOOGLE_CALENDAR_CREDENTIALS` (mayúsculas)
- ✅ Que el JSON es válido (pegalo en [jsonlint.com](https://jsonlint.com/) si no estás seguro)

**"Error 404: Calendario no encontrado"**
- ✅ Verifica que el `GOOGLE_CALENDAR_ID` es correcto
- ✅ Que la Service Account tiene permisos en ese calendario

**Los eventos no aparecen en Google Calendar**
- ✅ Verifica que ya has compartido el calendario con el email de la Service Account
- ✅ Dale permisos de "Hacer cambios en eventos"

---

## 📋 Notas técnicas

- Los eventos se crean con ID único: `suple-[AÑO]-[ID_CONVOCATORIA]-[TIPO_EVENTO]`
- Esto evita duplicados cuando sincronizas varias veces
- Los eventos son "transparentes" (no bloquean tu calendario)
- Se asigna un color distinto a cada tipo de evento para visualización rápida

¡Listo! Ahora tu dashboard está completamente automatizado. 🚀
