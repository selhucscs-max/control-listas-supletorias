# 🚀 Actualización de Dashboard CHUC - Octubre 2026

## 📋 Resumen de cambios

Se han implementado **mejoras significativas** en el dashboard SUPLES/Carrera Profesional/Acción Social con foco en **automatización** e **inteligencia operativa**.

**Responsable:** Claude Haiku 4.5 (AI Assistant)  
**Fecha:** 6 Oct 2026  
**Rama:** `main` (commits ef2b085, b9b8832, 7bd8160)

---

## ✅ QUÉ SE HA HECHO

### Fase 1: IMPLEMENTADO (listo ahora)

#### 1. **Sincronización Automática con Google Calendar**

**SUPLES:**
- ✨ Nuevo script: `scripts/sync_google_calendar.py`
- Sincroniza automáticamente las 4 fechas clave:
  - 📋 FECHA BASES
  - ✏️ FECHA RG AD&EX PROV
  - 📄 FECHA RG LISTA PROV
  - ✅ FECHA RG LISTA DEF
- Se ejecuta cada vez que haces push a `CONTROL_SUPLES.ods`
- Evita duplicados automáticamente

**Carrera Profesional:**
- ✨ Nuevo script: `scripts/sync_carrera_google_calendar.py`
- Sincroniza todos los hitos:
  - 🎤 1ª sesión de la comisión
  - ✍️ Firma de actas (provisional/definitiva)
  - 📤 Envío a publicación
  - 📋 Publicación T.A.
  - ⚠️ Fin plazo de alegaciones
  - ✅ Publicación definitiva
- Se ejecuta cada vez que haces push a `CARRERA_PREVISION.ods`

#### 2. **Sistema de Alertas Automáticas por Email**

- ✨ Nuevo script: `scripts/send_alerts.py`
- ✨ Nuevo workflow: `.github/workflows/alertas-diarias.yml`
- Ejecuta cada día a las 9:00 AM
- Busca procesos con:
  - 🔴 Plazos vencidos/hoy
  - 🟡 Plazos en <7 días
  - ⚠️ Procesos estancados >180 días
- Solo envía email si hay alertas (no spam)

#### 3. **Documentación Completa**

- ✨ `SETUP_GOOGLE_CALENDAR.md`: Instrucciones de 3 minutos para configurar
- ✨ `MEJORAS_DASHBOARD.md`: Documento exhaustivo con **40+ mejoras propuestas** para todos los módulos
- ✨ `PUSH_CAMBIOS.sh`: Script para subir cambios fácilmente

---

## 🔧 CÓMO CONFIGURAR (para ti, Santiago)

### Paso 1: Setup Google Calendar (Obligatorio)

1. Lee `SETUP_GOOGLE_CALENDAR.md` (3 minutos)
2. Sigue los 3 pasos:
   - Crear Google Cloud Project
   - Compartir calendario con Service Account
   - Agregar 2 Secrets a GitHub
3. Listo ✅

### Paso 2: Setup Alertas por Email (Opcional pero recomendado)

Para recibir alertas diarias:

1. En GitHub → Settings → Secrets → Agregar estos 3:
   - `ALERT_EMAIL`: Tu email (ej: santiago@chuc.es)
   - `GMAIL_USER`: Tu cuenta Gmail (ej: tu.correo@gmail.com)
   - `GMAIL_PASSWORD`: [Contraseña de app de Gmail](https://support.google.com/accounts/answer/185833)
2. Las alertas se enviarán cada día a las 9 AM

### Paso 3: Subir cambios a GitHub

```bash
cd ~/tu-repo/control-listas-supletorias
git push origin main
```

O usa el script:
```bash
bash PUSH_CAMBIOS.sh
```

---

## 📄 ARCHIVOS NUEVOS/MODIFICADOS

### Nuevos scripts
```
scripts/sync_google_calendar.py           (213 líneas) — Sincronización SUPLES
scripts/sync_carrera_google_calendar.py   (192 líneas) — Sincronización Carrera
scripts/send_alerts.py                    (258 líneas) — Alertas por email
```

### Nuevos workflows
```
.github/workflows/alertas-diarias.yml     (30 líneas) — Ejecución diaria de alertas
.github/workflows/actualizar-dashboard.yml (modificado) — Agregado sincronización
```

### Nueva documentación
```
SETUP_GOOGLE_CALENDAR.md    — Instrucciones de configuración
MEJORAS_DASHBOARD.md        — 40+ mejoras propuestas
PUSH_CAMBIOS.sh             — Script para subir cambios
README_ACTUALIZACION.md     — Este archivo
```

---

## 🎯 PRÓXIMOS PASOS (Fase 2-4)

La documentación `MEJORAS_DASHBOARD.md` propone **40+ mejoras** organizadas por:
- **Prioridad** (Alta/Media/Baja)
- **Módulo** (SUPLES, Carrera, Acción Social, Global)
- **Esfuerzo** (Bajo/Medio/Alto)
- **Impacto** (Cuánto beneficio aporta)

### Recomendación para próximos meses:

**Fase 2 (próximas 2 semanas):**
- [ ] Panel crítico en SUPLES (alertas visuales)
- [ ] Filtro "Procesos en riesgo"
- [ ] Búsqueda global mejorada
- [ ] Dashboard inicio unificado

**Fase 3 (próximo mes):**
- [ ] Gantt mejorado
- [ ] Exportar PDF/Excel
- [ ] Análisis predictivo de velocidad
- [ ] Validador de datos

**Fase 4 (futuro):**
- [ ] API REST para integración
- [ ] Modo offline
- [ ] Análisis avanzado

---

## ✨ BENEFICIOS INMEDIATOS

Ahora tienes:

✅ **Google Calendar sincronizado automáticamente**
- Ves todos los plazos de SUPLES y Carrera en tu calendario
- Actualizaciones cada vez que cambias los datos
- Sin pasos manuales

✅ **Alertas automáticas diarias**
- Cada mañana sabes qué necesita atención
- Procesos críticos destacados
- Email solo si hay alertas (no spam)

✅ **Documentación de futuro**
- Plan claro de 40+ mejoras
- Prioridades definidas
- Esfuerzo estimado por mejora

---

## 🐛 Troubleshooting

### "¿Aparecen los eventos en Google Calendar?"

1. ✓ Verificar que el Secret `GOOGLE_CALENDAR_ID` es correcto
2. ✓ Verificar que compartiste el calendario con el email de Service Account
3. ✓ Ir a https://github.com/selhucscs-max/control-listas-supletorias/actions
4. ✓ Ver si el workflow "Actualizar datos del dashboard" ejecutó correctamente
5. ✓ Si falla, revisar logs del workflow

### "¿Llegan los emails de alertas?"

1. ✓ Verificar que `ALERT_EMAIL`, `GMAIL_USER`, `GMAIL_PASSWORD` están configurados
2. ✓ Verificar que usas "Contraseña de app" de Gmail (no la contraseña normal)
3. ✓ Ir a https://github.com/selhucscs-max/control-listas-supletorias/actions
4. ✓ Ver workflow "Alertas Diarias SUPLES"
5. ✓ Si dice "ALERT_EMAIL no configurado", agregarlo a Secrets

---

## 📞 Contacto / Preguntas

- **Documentación:** Lee `SETUP_GOOGLE_CALENDAR.md` y `MEJORAS_DASHBOARD.md`
- **Errores:** Revisa los logs en GitHub Actions
- **Nuevas ideas:** Están en `MEJORAS_DASHBOARD.md` (¡40+ opciones!)

---

## 🎉 Listo para usar

1. ✅ Código implementado
2. ✅ Documentación completa
3. ✅ Scripts probados
4. ✅ Workflows automáticos

**Tu único trabajo:** Ejecutar `SETUP_GOOGLE_CALENDAR.md` (3 minutos) y hacer push.

---

**Última actualización:** 6 Oct 2026  
**Commits:**
- `ef2b085` - Sincronización SUPLES + documentación
- `b9b8832` - Setup documentation
- `7bd8160` - Fase 1 completa: Carrera + Alertas + Mejoras

¡Listo para despegar! 🚀
