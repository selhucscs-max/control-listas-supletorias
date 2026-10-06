#!/usr/bin/env python3
"""
Sincroniza fechas de CONTROL_SUPLES.ods con Google Calendar automáticamente.

Uso:
    python3 scripts/sync_google_calendar.py

Requiere:
    - Variable de entorno GOOGLE_CALENDAR_CREDENTIALS (JSON de service account)
    - GOOGLE_CALENDAR_ID (ID del calendario destino)

Este script:
1. Lee CONTROL_SUPLES.ods
2. Crea/actualiza eventos en Google Calendar para cada convocatoria
3. Evita duplicados usando el ID de convocatoria como identificador único
4. Se ejecuta automáticamente en el workflow de GitHub Actions
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
from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SHEET_NAME = "1_Datos_generales"

# Las fechas que sincronizaremos con Google Calendar
DATE_EVENTS = {
    "FECHA BASES": "📋 Publicación de bases",
    "FECHA RG AD&EX PROV": "✏️ Resultado Ad&Ex provisional",
    "FECHA RG LISTA PROV": "📄 Publicación lista provisional",
    "FECHA RG LISTA DEF": "✅ Publicación lista definitiva",
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
    """Lee los eventos del CONTROL_SUPLES.ods."""
    df = pd.read_excel(ods_path, sheet_name=SHEET_NAME, engine="odf")
    df.columns = [str(c).strip() for c in df.columns]

    # Filtrar filas válidas (igual que generate_data.py)
    valid_mask = df["AÑO"].notna() & df["ID"].notna() & (df["ID"].astype(str).str.strip() != "")
    df = df[valid_mask]

    events = []
    for _, row in df.iterrows():
        convocatoria_id = str(row["ID"]).strip()
        categoria = str(row.get("CATEGORIA", "")).strip()
        año = int(row["AÑO"])

        # Para cada tipo de evento (bases, ad&ex prov, lista prov, lista def)
        for date_col, event_type in DATE_EVENTS.items():
            fecha_raw = row.get(date_col)

            # Convertir a datetime si es necesario
            if pd.notna(fecha_raw):
                if isinstance(fecha_raw, str):
                    try:
                        fecha = pd.to_datetime(fecha_raw, dayfirst=True).date()
                    except:
                        continue
                elif isinstance(fecha_raw, (pd.Timestamp, datetime)):
                    fecha = fecha_raw.date()
                else:
                    try:
                        fecha = pd.to_datetime(fecha_raw).date()
                    except:
                        continue

                # Construir evento
                event = {
                    # Google solo admite ids con 0-9 a-v (base32hex); sha1 en hex lo cumple
                    "id": hashlib.sha1(
                        f"suple-{año}-{convocatoria_id}-{date_col}".encode("utf-8")
                    ).hexdigest(),
                    "summary": f"{event_type} - {categoria}",
                    "description": f"Convocatoria {año}/{convocatoria_id}\n{categoria}",
                    "start": {"date": str(fecha)},
                    "end": {"date": str(fecha + timedelta(days=1))},  # fin exclusivo
                    "colorId": get_color_for_event_type(date_col),
                    "transparency": "transparent",  # No bloquea tiempo
                }
                events.append(event)

    return events


def get_color_for_event_type(date_col: str) -> str:
    """Asigna un color a cada tipo de evento."""
    color_map = {
        "FECHA BASES": "10",  # Verde
        "FECHA RG AD&EX PROV": "5",  # Amarillo
        "FECHA RG LISTA PROV": "6",  # Naranja
        "FECHA RG LISTA DEF": "2",  # Azul
    }
    return color_map.get(date_col, "0")  # Gris por defecto


def sync_events(service, calendar_id: str, events: list):
    """Sincroniza eventos con Google Calendar, evitando duplicados."""
    created = 0
    updated = 0
    failed = 0

    for event in events:
        event_id = event.pop("id")

        try:
            # Intentar actualizar primero (si ya existe)
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
                    # No existe, crear nuevo
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
    # Leer variables de entorno
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
    if not calendar_id:
        raise ValueError("Variable de entorno GOOGLE_CALENDAR_ID no configurada")

    repo_root = Path(__file__).resolve().parent.parent
    ods_path = repo_root / "CONTROL_SUPLES.ods"

    if not ods_path.exists():
        print(f"❌ Archivo no encontrado: {ods_path}")
        sys.exit(1)

    # Cargar eventos desde ODS
    print("📖 Leyendo CONTROL_SUPLES.ods...")
    events = load_events_from_ods(ods_path)
    print(f"   Encontrados {len(events)} eventos")

    # Conectar a Google Calendar
    print("🔐 Autenticando con Google Calendar...")
    credentials = get_credentials()
    service = build_calendar_service(credentials)

    # Sincronizar
    print(f"📅 Sincronizando con calendario: {calendar_id}")
    created, updated, failed = sync_events(service, calendar_id, events)

    # Resumen
    print("\n" + "=" * 50)
    print(f"✨ Creados: {created}")
    print(f"✏️  Actualizados: {updated}")
    print(f"❌ Fallidos: {failed}")
    print(f"📊 Total: {len(events)} eventos")
    print("=" * 50)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
