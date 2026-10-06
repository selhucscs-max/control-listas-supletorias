# 🚀 Mejoras Propuestas para Dashboard CHUC

Análisis exhaustivo de mejoras para todos los módulos del dashboard. **Prioridad: ALTA → BAJA**

---

## 📊 MÓDULO: SUPLES (Listas Supletorias)

### 🔴 PRIORIDAD ALTA

#### 1. **Panel de Control Crítico** (Inicio mejorado)
- **Problema:** La página de inicio (Resumen) no destaca los procesos urgentes
- **Solución:** Agregar sección "Alertas" al inicio con:
  - 🚨 Plazos venciendo en <7 días (alertas rojas)
  - ⚠️ Plazos en 7-14 días (alertas amarillas)
  - ℹ️ Próximos hitos esta semana
- **Impacto:** Usuario ve de un vistazo qué necesita atención inmediata
- **Esfuerzo:** Bajo (modificar JavaScript de Resumen)

#### 2. **Notificaciones Email Automáticas**
- **Problema:** No hay alertas cuando se aproximan fechas críticas
- **Solución:** Agregar a GitHub Actions:
  - Script que revisa CONTROL_SUPLES.ods cada día
  - Envía email si hay fechas vencidas/próximas (<7 días)
  - Usa Gmail API o servicio como SendGrid
- **Impacto:** No necesitas revisar constantemente el dashboard
- **Esfuerzo:** Medio (script Python + credenciales de Gmail)
- **Ejemplo:** "⚠️ ALERTA: 3 convocatorias con plazo de alegaciones venciendo mañana"

#### 3. **Vista Gantt Mejorada** (en tab "Estado")
- **Problema:** La línea temporal actual es lineal, no muestra solapamientos
- **Solución:** Reemplazar con Gantt chart que muestre:
  - Cada categoría como barra horizontal
  - Fases de cada proceso como segmentos de color
  - Solapamientos visuales (para detectar picos de carga)
  - Hoy marcado con línea roja
- **Impacto:** Visualizar presión de trabajo futura
- **Esfuerzo:** Medio (usar biblioteca como Frappe Gantt o Chart.js)

#### 4. **Filtro "Procesos en Riesgo"**
- **Problema:** Hay que buscar manualmente procesos estancados
- **Solución:** Agregar botones en "Gestión":
  - 🔴 "Estancados >180d"
  - 🟡 "Estancados 90-180d"
  - 🟢 "En movimiento"
  - ⚠️ "Plazo vence en <7d"
- **Impacto:** Filtrar procesos críticos en 1 clic
- **Esfuerzo:** Bajo (lógica de filtrado ya existe)

#### 5. **Exportar a PDF/Excel con Gráficos**
- **Problema:** Puedes exportar datos pero no reportes visuales
- **Solución:** Agregar botón en cada pestaña:
  - Exportar tabla actual + gráficos a PDF
  - Exportar datos a Excel con formato
- **Impacto:** Reportes para presentaciones a Dirección
- **Esfuerzo:** Bajo-Medio (usar bibliotecas como jsPDF, html2canvas)

#### 6. **Búsqueda Global Mejorada**
- **Problema:** Búsqueda actual solo busca por categoría
- **Solución:** Búsqueda global que busque por:
  - Categoría, área, dirección
  - Rango de fechas
  - Fase (bases, ad&ex, lista prov, lista def)
  - ID de convocatoria
- **Impacto:** Encontrar procesos más rápido
- **Esfuerzo:** Bajo (usar función find/filter existente)

---

### 🟡 PRIORIDAD MEDIA

#### 7. **Análisis Predictivo de Velocidad**
- **Problema:** No sabes cuándo terminará un proceso
- **Solución:** Mostrar en cada convocatoria:
  - Días históricos promedio para esa categoría
  - Días que lleva YA ese proceso
  - Predicción de cuándo terminará (si continúa a ritmo actual)
- **Impacto:** Mejor planificación
- **Esfuerzo:** Medio (análisis de datos)
- **Ejemplo:** "FEA Pediatría: 79 días completados, 35 días estimados restantes"

#### 8. **Dashboard de Baremación en Tiempo Real**
- **Problema:** Tab Baremación es solo estimación, no muestra progreso real
- **Solución:** Agregar columna en CONTROL_SUPLES.ods: "% BAREMADO"
  - Dashboard mostraría progreso visual (barras, porcentaje)
  - Permite seguimiento diario de baremación
- **Impacto:** Saber exactamente cuánto queda por baremaizar
- **Esfuerzo:** Bajo (agregar columna + lógica de visualización)

#### 9. **Comparativa Año vs Año**
- **Problema:** No ves fácilmente cómo va 2026 vs 2025
- **Solución:** En "Evolución", agregar gráfico que compare:
  - Convocatorias por mes (2026 vs 2025)
  - Tasa de admisión (2026 vs 2025)
  - Días medios de resolución (2026 vs 2025)
- **Impacto:** Detectar desviaciones rápido
- **Esfuerzo:** Bajo (Chart.js ya está configurado)

#### 10. **Reclamaciones por Fase Mejorado**
- **Problema:** Solo ves número total de reclamaciones
- **Solución:** Mostrar:
  - Tasa de reclamación por categoría (% de presentados)
  - Motivos más frecuentes (si se registran)
  - Tendencia de reclamaciones por año
- **Impacto:** Identificar categorías problemáticas
- **Esfuerzo:** Medio (requiere nuevas columnas en .ods)

---

### 🟢 PRIORIDAD BAJA

#### 11. **Dark Mode**
- **Solución:** Toggle en header que cambia CSS
- **Impacto:** Menos fatiga ocular
- **Esfuerzo:** Bajo

#### 12. **Exportar Eventos a Outlook/iCal**
- **Solución:** Botón "Exportar a Outlook" que descargue .ics
- **Impacto:** Integración con calendario corporativo
- **Esfuerzo:** Bajo

#### 13. **Historial de Cambios Auditoría**
- **Solución:** Log de quién importó datos, cuándo, qué cambió
- **Impacto:** Trazabilidad
- **Esfuerzo:** Medio

---

## 📈 MÓDULO: CARRERA PROFESIONAL

### 🔴 PRIORIDAD ALTA

#### 1. **Sincronización con Google Calendar** (Similar a SUPLES)
- **Problema:** Los hitos de Carrera ya están en Google Calendar, pero no sincroniza automáticamente
- **Solución:** Crear script paralelo a SUPLES:
  - Lee CARRERA_PREVISION.ods
  - Sincroniza con Google Calendar
  - Crea eventos para: 1ª sesión, firma provisional, firma definitiva, publicación
- **Impacto:** Los hitos de Carrera aparecen automáticamente en Google Calendar
- **Esfuerzo:** Bajo (copiar/adaptar script de SUPLES)

#### 2. **Notificaciones de Hitos Próximos**
- **Problema:** Hitos próximos (2-7 días) no notifican
- **Solución:** Email automático cuando faltan 3 y 1 día para cada hito
- **Impacto:** No se te olvida ningún hito
- **Esfuerzo:** Bajo (script Python similar a SUPLES)

#### 3. **Vista de "Estado Activo" Mejorada**
- **Problema:** No ves fácilmente cuántas comisiones están en cada fase
- **Solución:** Agregar panel con:
  - Fase 1: Sesión → X comisiones
  - Fase 2: Alegaciones → Y comisiones
  - Fase 3: Definitiva → Z comisiones
  - Timeline horizontal mostrando progreso
- **Impacto:** Snapshot del estado de Carrera en 2 segundos
- **Esfuerzo:** Bajo

#### 4. **Fechas de Cierre Predichas**
- **Problema:** No sabes cuándo terminarán todos los procesos
- **Solución:** Mostrar:
  - Comisión con cierre más próximo (y cuándo)
  - Promedio de duración total
  - Línea de cierre estimada en cronograma
- **Impacto:** Planificar mejor
- **Esfuerzo:** Bajo

---

### 🟡 PRIORIDAD MEDIA

#### 5. **Exportar Cronograma a PowerPoint**
- **Solución:** Botón que exporta cronograma + tablas a PPTX
- **Impacto:** Presentar a Dirección/Comisiones
- **Esfuerzo:** Medio (usar python-pptx)

#### 6. **Alertas de Conflicto de Fechas**
- **Problema:** Dos comisiones pueden tener fechas conflictivas
- **Solución:** Sistema que avisa si dos comisiones tienen:
  - Misma fecha de sesión (si comparten tribunal)
  - Alegaciones solapadas (conflicto de disponibilidad)
- **Impacto:** Evitar conflictos de agenda
- **Esfuerzo:** Medio

---

## 💰 MÓDULO: AYUDAS DE ACCIÓN SOCIAL

### 🔴 PRIORIDAD ALTA

#### 1. **Dashboard de Participación por Departamento**
- **Problema:** No sabes qué departamentos participan más
- **Solución:** Gráfico de barras: participantes por departamento
  - Mostrar top 5 departamentos
  - Comparación años
- **Impacto:** Identificar departamentos con baja participación
- **Esfuerzo:** Medio (requiere nueva columna "DEPARTAMENTO" en Indicadores.ods)

#### 2. **Análisis de Tasa de Reclamación**
- **Problema:** No ves si la tasa de reclamación es normal/alta
- **Solución:** Mostrar:
  - Tasa de reclamación anual (% sobre participantes)
  - Tendencia (roja si sube, verde si baja)
  - Comparativa con años anteriores
  - Motivos principales (si se registran)
- **Impacto:** Detectar insatisfacción
- **Esfuerzo:** Bajo (datos ya existen)

#### 3. **Predicción de Admisiones/Exclusiones**
- **Problema:** No sabes cuál será la tasa final
- **Solución:** Mostrar predicción basada en años anteriores:
  - "Tasa histórica de admisión: 79%"
  - "Predicción 2026: ~1020 admitidos (si sigue tendencia)"
- **Impacto:** Planificación presupuestaria
- **Esfuerzo:** Bajo

#### 4. **Segmentación por Tipo de Ayuda**
- **Problema:** No distingues entre tipos de ayuda
- **Solución:** Agregar columna "TIPO_AYUDA" (Guardería, Vivienda, Educación, etc.)
  - Mostrar participación por tipo
  - Tasa de aprobación por tipo
- **Impacto:** Decisiones sobre presupuesto por tipo
- **Esfuerzo:** Medio

---

### 🟡 PRIORIDAD MEDIA

#### 5. **Comparativa por Categoría Profesional**
- **Solución:** Filtro que muestre participación por categoría (Facultativos, No facultativos, etc.)
- **Impacto:** Equidad
- **Esfuerzo:** Bajo

---

## 🌐 MEJORAS GLOBALES (todos los módulos)

### 🔴 PRIORIDAD ALTA

#### 1. **Dashboard Unificado de Inicio**
- **Problema:** Cada módulo tiene su propio Resumen
- **Solución:** Crear página de INICIO con:
  - 3 cards: SUPLES / Carrera / Acción Social
  - Alertas críticas de los 3 (si hay)
  - Últimas actividades (convocatorias publicadas, comisiones sesionadas, etc.)
  - Link rápido a cada módulo
- **Impacto:** Visión de 360° al abrir el dashboard
- **Esfuerzo:** Bajo-Medio

#### 2. **Importador de Datos Mejorado**
- **Problema:** Importar datos puede romper esquema
- **Solución:** Agregar validaciones antes de importar:
  - ✓ Verificar que todas las columnas requeridas existen
  - ✓ Validar formatos de fecha
  - ✓ Advertencia si hay nuevas filas sin completar
  - ✓ Preview de cambios antes de importar
- **Impacto:** Evitar errores
- **Esfuerzo:** Medio

#### 3. **Sincronización de Datos Entre Módulos**
- **Problema:** SUPLES y Carrera tienen categorías, pero no sincronizadas
- **Solución:** Script que valida que categorías en ambos archivos coinciden
  - Alerta si hay categorías nuevas/faltantes
- **Impacto:** Integridad de datos
- **Esfuerzo:** Bajo

#### 4. **API REST para Integración**
- **Problema:** No puedes acceder a datos del dashboard desde otros sistemas (Portafirmas, etc.)
- **Solución:** Crear API simple (Node.js/Python Flask):
  - GET /api/suples → JSON con convocatorias
  - GET /api/carrera → JSON con hitos
  - GET /api/accion-social → JSON con participantes
- **Impacto:** Integración con Portafirmas, reportes automáticos, etc.
- **Esfuerzo:** Alto (requiere servidor)

#### 5. **Modo Offline / Caché Mejorado**
- **Problema:** Si falla internet, dashboard no funciona
- **Solución:** Service Worker que cachea datos
  - Funciona offline con última versión de datos
  - Sincroniza cuando se reconecta
- **Impacto:** Usar dashboard sin internet
- **Esfuerzo:** Medio

---

### 🟡 PRIORIDAD MEDIA

#### 6. **Tema Corporativo Mejorado**
- **Problema:** Diseño básico, no refleja branding de SCS
- **Solución:** 
  - Agregar logo SCS/CHUC en header
  - Colores corporativos (azul SCS)
  - Footer con links a intranet/recursos
- **Impacto:** Profesionalidad
- **Esfuerzo:** Bajo

#### 7. **Responsivo Mejorado**
- **Problema:** En tablets no optimizado
- **Solución:** Ajustar breakpoints, tamaños de fuente
- **Impacto:** Mejor uso en iPad
- **Esfuerzo:** Bajo

#### 8. **Búsqueda Global**
- **Problema:** Tienes que cambiar de pestaña para buscar en módulo diferente
- **Solución:** Buscador global (Ctrl+K) que busca en SUPLES, Carrera, Acción Social
- **Impacto:** Encontrar cualquier cosa desde cualquier lugar
- **Esfuerzo:** Medio

#### 9. **Comentarios/Anotaciones**
- **Problema:** No puedes anotar notas en los procesos
- **Solución:** Agregar botón "Comentario" en cada convocatoria
  - Comentarios guardados en localStorage/IndexedDB
  - Solo local (no sincroniza, es personal)
- **Impacto:** Recordatorios personales
- **Esfuerzo:** Bajo

#### 10. **Impresión Optimizada**
- **Problema:** Imprimir el dashboard es feo
- **Solución:** CSS @media print que optimiza para papel
  - Oculta navegación
  - Ajusta colores para B&N
- **Impacto:** Reportes impresos legibles
- **Esfuerzo:** Bajo

---

### 🟢 PRIORIDAD BAJA

#### 11. **Estadísticas de Uso**
- **Solución:** Analytics simple que registra:
  - Pestañas más visitadas
  - Búsquedas más comunes
  - Hora de pico de uso
- **Impacto:** Entender uso real del dashboard
- **Esfuerzo:** Bajo

#### 12. **Tutorial Interactivo**
- **Solución:** Primera vez que abres, tour de características
- **Impacto:** Nuevos usuarios aprenden rápido
- **Esfuerzo:** Medio

#### 13. **Modo Presentación (Kiosk)**
- **Solución:** Pantalla que muestra Resumen SUPLES actualizado cada 30 seg
  - Para oficina/recepción
- **Impacto:** Información en vivo en pantalla pública
- **Esfuerzo:** Bajo

---

## 📋 RESUMEN DE MEJORAS POR IMPACTO/ESFUERZO

### Máximo impacto, mínimo esfuerzo (HACER PRIMERO):
1. Panel crítico SUPLES (alertas)
2. Filtro "Procesos en riesgo"
3. Sincronización Carrera con Google Calendar
4. Notificaciones de hitos próximos
5. Búsqueda global mejorada

### Impacto medio, esfuerzo medio (después):
6. Gantt mejorado SUPLES
7. Exportar PDF/Excel
8. Dashboard inicio unificado
9. Análisis reclamaciones Acción Social

### Alto esfuerzo pero muy valioso (futuro):
10. API REST
11. Modo offline
12. Notificaciones email automáticas

---

## 🎯 PLAN DE ACCIÓN PROPUESTO

**Fase 1 (INMEDIATO - esta semana):**
- ✅ Sincronización Google Calendar SUPLES (HECHO)
- ✅ Sincronización Google Calendar Carrera (adaptar script)
- Notificaciones email automáticas

**Fase 2 (próximas 2 semanas):**
- Panel crítico SUPLES
- Filtro "Procesos en riesgo"
- Búsqueda global mejorada
- Dashboard inicio unificado

**Fase 3 (próximo mes):**
- Gantt mejorado
- Exportar PDF/Excel
- Análisis predictivo velocidad
- Validador datos

**Fase 4 (futuro):**
- API REST
- Modo offline
- Análisis avanzado

---

**Última actualización:** 6 Oct 2026
**Autor:** Claude Haiku + Santiago Fariña

