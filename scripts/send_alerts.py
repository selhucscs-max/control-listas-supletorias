#!/usr/bin/env python3
"""
Envía alertas por email de procesos con plazos próximos a vencer.

Se ejecuta automáticamente en GitHub Actions cada día a las 9 AM.
Revisa CONTROL_SUPLES.ods y busca convocatorias con:
- Plazo de alegaciones vence en <7 días
- Convocatoria estancada >180 días
- Lista definitiva próxima a publicarse

Solo envía email si hay alertas (no spam si todo está bien).
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl

import pandas as pd

SHEET_NAME = "1_Datos_generales"

# Columnas para revisar
DATE_COLUMNS = {
    "FECHA BASES": ("📋 Publicación de bases", 30),
    "FECHA RG AD&EX PROV": ("✏️ Resultado Ad&Ex provisional", 30),
    "FECHA RG LISTA PROV": ("📄 Publicación lista provisional", 14),
    "FECHA RG LISTA DEF": ("✅ Publicación lista definitiva", 7),
}


def load_alerts_from_ods(ods_path: Path):
    """Lee CONTROL_SUPLES.ods y busca procesos con alertas."""
    df = pd.read_excel(ods_path, sheet_name=SHEET_NAME, engine="odf")
    df.columns = [str(c).strip() for c in df.columns]

    today = datetime.now().date()
    alerts = []

    for _, row in df.iterrows():
        convocatoria_id = str(row.get("ID", "")).strip()
        categoria = str(row.get("CATEGORIA", "")).strip()
        año = row.get("AÑO")
        dias_sin_avance = row.get("DÍAS S/AVANCE")

        if not convocatoria_id or not año:
            continue

        # Alerta 1: Procesos estancados >180 días
        if pd.notna(dias_sin_avance):
            try:
                dias = int(float(dias_sin_avance))
                if dias > 180:
                    alerts.append({
                        "type": "ESTANCADO",
                        "severity": "🔴 CRÍTICO",
                        "convocatoria": f"{año}/{convocatoria_id}",
                        "categoria": categoria,
                        "message": f"Proceso estancado por {dias} días sin avance",
                    })
            except:
                pass

        # Alerta 2: Fechas próximas a vencer
        for date_col, (event_name, alert_days) in DATE_COLUMNS.items():
            fecha_raw = row.get(date_col)
            if pd.isna(fecha_raw):
                continue

            try:
                if isinstance(fecha_raw, str):
                    fecha = pd.to_datetime(fecha_raw, dayfirst=True).date()
                elif isinstance(fecha_raw, (pd.Timestamp, datetime)):
                    fecha = fecha_raw.date()
                else:
                    fecha = pd.to_datetime(fecha_raw).date()
            except:
                continue

            dias_hasta = (fecha - today).days

            # Alerta si falta < alert_days
            if 0 <= dias_hasta < alert_days:
                severity = "🔴 HOY" if dias_hasta == 0 else "🟡 PRÓXIMO" if dias_hasta <= 3 else "ℹ️ AVISO"
                alerts.append({
                    "type": "PLAZO",
                    "severity": severity,
                    "convocatoria": f"{año}/{convocatoria_id}",
                    "categoria": categoria,
                    "message": f"{event_name} en {dias_hasta} día(s) ({fecha})",
                })

    return alerts


def format_email_body(alerts: list) -> str:
    """Formatea el cuerpo del email con alertas."""
    body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; }
            .header { background: #0B2D5F; color: white; padding: 20px; border-radius: 8px; }
            .alert { margin: 15px 0; padding: 15px; border-left: 4px solid #FFA500; background: #FFF9E6; }
            .alert.critical { border-left-color: #C0392B; background: #FDF2F1; }
            .alert.urgent { border-left-color: #D97706; background: #FFFBEB; }
            .footer { margin-top: 30px; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 15px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>⚠️ Alertas del Dashboard SUPLES</h2>
            <p>Procesos que requieren atención</p>
        </div>
    """

    # Agrupar por severidad
    criticos = [a for a in alerts if "🔴" in a["severity"]]
    urgentes = [a for a in alerts if "🟡" in a["severity"]]
    informativos = [a for a in alerts if "ℹ️" in a["severity"]]

    if criticos:
        body += "<h3>🔴 Críticos (Requieren acción inmediata)</h3>"
        for alert in criticos:
            body += f"""
            <div class="alert critical">
                <strong>{alert['convocatoria']}</strong> — {alert['categoria']}<br>
                {alert['message']}
            </div>
            """

    if urgentes:
        body += "<h3>🟡 Urgentes (7-14 días)</h3>"
        for alert in urgentes:
            body += f"""
            <div class="alert urgent">
                <strong>{alert['convocatoria']}</strong> — {alert['categoria']}<br>
                {alert['message']}
            </div>
            """

    if informativos:
        body += "<h3>ℹ️ Avisos (Información)</h3>"
        for alert in informativos:
            body += f"""
            <div class="alert">
                <strong>{alert['convocatoria']}</strong> — {alert['categoria']}<br>
                {alert['message']}
            </div>
            """

    body += f"""
        <div class="footer">
            <p>Total de alertas: {len(alerts)}</p>
            <p>Generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p><a href="https://selhucscs-max.github.io/control-listas-supletorias/">Ver dashboard completo</a></p>
        </div>
    </body>
    </html>
    """

    return body


def send_email(to_address: str, subject: str, body: str):
    """Envía email usando Gmail SMTP (si están configuradas las credenciales)."""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    if not gmail_user or not gmail_password:
        print("⚠️ GMAIL_USER o GMAIL_PASSWORD no configurados")
        print("   Las alertas NO se enviarán por email")
        print("   Para habilitar: configura estos secrets en GitHub")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = to_address

        part = MIMEText(body, "html")
        msg.attach(part)

        # Conectar a Gmail
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [to_address], msg.as_string())

        print(f"✅ Email enviado a {to_address}")
        return True

    except Exception as e:
        print(f"❌ Error al enviar email: {e}")
        return False


def main():
    repo_root = Path(__file__).resolve().parent.parent
    ods_path = repo_root / "CONTROL_SUPLES.ods"

    if not ods_path.exists():
        print(f"❌ Archivo no encontrado: {ods_path}")
        sys.exit(1)

    print("📖 Leyendo CONTROL_SUPLES.ods para buscar alertas...")
    alerts = load_alerts_from_ods(ods_path)

    if not alerts:
        print("✅ No hay alertas. Todo está bajo control.")
        return

    print(f"\n🚨 Encontradas {len(alerts)} alertas:")
    for alert in alerts:
        print(f"  {alert['severity']} {alert['convocatoria']} - {alert['message']}")

    # Enviar email si hay alertas
    recipient = os.getenv("ALERT_EMAIL")
    if recipient:
        print(f"\n📧 Enviando alertas a {recipient}...")
        subject = f"⚠️ Alertas SUPLES ({len(alerts)} procesos requieren atención)"
        body = format_email_body(alerts)
        send_email(recipient, subject, body)
    else:
        print("\n⚠️ ALERT_EMAIL no configurado")
        print("   Para recibir alertas por email, configura este secret en GitHub")

    print("\n✅ Proceso de alertas completado")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
