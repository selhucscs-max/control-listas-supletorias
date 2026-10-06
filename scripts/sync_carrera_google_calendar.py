#!/usr/bin/env python3
"""
Sincroniza hitos de CARRERA_PREVISION.ods con Google Calendar automáticamente.

Crea eventos para:
- 1ª sesión de la comisión
- Firma de actas (fase provisional)
- Envío a publicación
- Publicación T.A. (provisional)
- Fin del plazo de alegaciones
- 2ª sesión de la comisión
- Firma de actas (fase definitiva)
- Envío a publicación definitiva
- Publicación definitiva
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SHEET_NAME = "Procesos"

# Solo se sincronizan fechas recientes o futuras (por defecto, últimos 60 días)
CUTOFF = datetime.now().date() - timedelta(days=int(os.getenv("CALENDAR_DAYS_BACK", "60")))

# Los hitos que sincronizaremos (basados en columnas de CARRERA_PREVISION.ods)
MILESTONE_EVENTS = {
    "1ª sesión de la comisión": "🎤",
    "Firma de actas (fase provisional)": "✍️",
    "Envío a publicación": "📤",
    "Publicación T.A. (provisional)": "📋",
    "Fin del plazo de alegaciones": "⚠️",
    "2ª sesión de la comisión": "🎤",
    "Firma de actas (fase definitiva)": "✍️",
    "Envío a publicación definitiva": "📤",
    "Publicación definitiva": "✅",
}


def get_credentials():
    """Obtiene credenciales de Google Calendar desde variable de entorno."""
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    if not creds_json:
        raise ValueError(
            "Variable de entorno GOOGLE_CALENDAR_CREDENTIALS no configurada"
        )

    try:
        creds_dict = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
        return credentials
    except json.JSONDecodeError as e:
        raise ValueError(f"GOOGLE_CALENDAR_CREDENTIALS no es JSON válido: {e}")


def build_calendar_service(credentials):
    """Construye el servicio de Google Calendar API."""
    return build("calendar", "v3", credentials=credentials)


def load_events_from_ods(ods_path: Path):
    """Lee los hitos del CARRERA_PREVISION.ods."""
    try:
        df = pd.read_excel(ods_path, sheet_name=SHEET_NAME, engine="odf")
    except Exception as e:
        print(f"⚠️ No se pudo leer '{SHEET_NAME}': {e}")
        print("   Buscando otras hojas disponibles...")
        xls = pd.ExcelFile(ods_path, engine="odf")
        print(f"   Hojas disponibles: {xls.sheet_names}")
        return []

    df.columns = [str(c).strip() for c in df.columns]

    events = []

    # Buscar filas con proceso/convocatoria
    for _, row in df.iterrows():
        # Identificador del proceso
        proceso_name = str(row.get("Proceso", "")).strip() if "Proceso" in df.columns else ""
        convocatoria = str(row.get("Convocatoria", "")).strip() if "Convocatoria" in df.columns else ""
        comision = str(row.get("Comisión", "")).strip() if "Comisión" in df.columns else ""

        if not proceso_name or not convocatoria:
            continue

        # Identificador único
        process_id = f"{convocatoria}-{comision}".replace(" ", "-").lower()

        # Buscar columnas de fecha para cada hito
        for milestone_name, emoji in MILESTONE_EVENTS.items():
            # Buscar columna que tenga el nombre del hito
            fecha_col = None
            for col in df.columns:
                if milestone_name.lower() in col.lower():
                    fecha_col = col
                    break

            if not fecha_col or pd.isna(row.get(fecha_col)):
                continue

            fecha_raw = row[fecha_col]

            # Convertir a datetime si es necesario
            try:
                if isinstance(fecha_raw, str):
                    fecha = pd.to_datetime(fecha_raw, dayfirst=True).date()
                elif isinstance(fecha_raw, (pd.Timestamp, datetime)):
                    fecha = fecha_raw.date()
                else:
                    fecha = pd.to_datetime(fecha_raw).date()
            except:
                continue

            if fecha < CUTOFF:
                continue

            # Construir evento
            event = {
                # Google solo admite ids con 0-9 a-v (base32hex); sha1 en hex lo cumple
                "id": hashlib.sha1(
                    f"carrera-{process_id}-{milestone_name}".encode("utf-8")
                ).hexdigest(),
                "summary": f"{emoji} {milestone_name} — {comision} ({convocatoria})",
                "description": f"Convocatoria: {convocatoria}\nComisión: {comision}\nProceso: {proceso_name}",
                "start": {"date": str(fecha)},
                "end": {"date": str(fecha + timedelta(days=1))},  # fin exclusivo
                "colorId": get_color_for_phase(milestone_name),
                "transparency": "transparent",
            }
            events.append(event)

    return events


def get_color_for_phase(milestone_name: str) -> str:
    """Asigna un color según la fase del hito."""
    if "provisional" in milestone_name.lower():
        return "5"  # Amarillo (fase provisional)
    elif "definitiva" in milestone_name.lower():
        return "2"  # Azul (fase definitiva)
    elif "sesión" in milestone_name.lower():
        return "10"  # Verde (sesión)
    elif "alegaciones" in milestone_name.lower():
        return "6"  # Naranja (alertas)
    elif "publicación" in milestone_name.lower():
        return "3"  # Cyan (publicación)
    else:
        return "0"  # Gris


def sync_events(service, calendar_id: str, events: list):
    """Sincroniza eventos con Google Calendar."""
    created = 0
    updated = 0
    failed = 0

    for event in events:
        event_id = event.pop("id")

        try:
            try:
                service.events().update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event,
                ).execute()
                updated += 1
                print(f"✏️ Actualizado: {event['summary']}")
            except HttpError as e:
                if e.resp.status == 404:
                    event["id"] = event_id
                    service.events().insert(
                        calendarId=calendar_id,
                        body=event,
                    ).execute()
                    created += 1
                    print(f"✨ Creado: {event['summary']}")
                else:
                    raise

        except Exception as e:
            failed += 1
            print(f"❌ Error en {event['summary']}: {e}")

    return created, updated, failed


def main():
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
    if not calendar_id:
        print("⚠️ GOOGLE_CALENDAR_ID no configurado. Saltando sincronización de Carrera.")
        return

    repo_root = Path(__file__).resolve().parent.parent
    ods_path = repo_root / "CARRERA_PREVISION.ods"

    if not ods_path.exists():
        print(f"⚠️ Archivo no encontrado: {ods_path}")
        return

    print("📖 Leyendo CARRERA_PREVISION.ods...")
    events = load_events_from_ods(ods_path)

    if not events:
        print("   No se encontraron hitos para sincronizar")
        return

    print(f"   Encontrados {len(events)} hitos")

    print("🔐 Autenticando con Google Calendar...")
    credentials = get_credentials()
    service = build_calendar_service(credentials)

    print(f"📅 Sincronizando Carrera Profesional...")
    created, updated, failed = sync_events(service, calendar_id, events)

    print("\n" + "=" * 50)
    print(f"✨ Creados: {created}")
    print(f"✏️  Actualizados: {updated}")
    print(f"❌ Fallidos: {failed}")
    print(f"📊 Total: {len(events)} hitos")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
