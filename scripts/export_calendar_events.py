#!/usr/bin/env python3
"""
Exporta a calendar_events.json los eventos de SUPLES escritos A MANO en Google Calendar,
para que el dashboard los muestre en la pestaña Calendario.

Reglas:
- Se ignoran los eventos creados por sync_google_calendar.py (su id es un sha1 de 40 hex).
- Solo se exportan eventos cuyo título o descripción contenga la palabra clave
  (por defecto "suple", sin distinguir mayúsculas ni acentos). Así los eventos
  personales del calendario no acaban publicados en la web.
- Ventana: desde 120 días atrás hasta 400 días adelante.

Requiere GOOGLE_CALENDAR_CREDENTIALS y GOOGLE_CALENDAR_ID (mismos secretos que la sincronización).
Opcional: CALENDAR_KEYWORD para cambiar la palabra clave.
"""

import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

TZ = "Atlantic/Canary"
SYNC_ID = re.compile(r"^[0-9a-f]{40}$")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def main():
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
    if not creds_json or not calendar_id:
        raise ValueError("Faltan GOOGLE_CALENDAR_CREDENTIALS o GOOGLE_CALENDAR_ID")
    keyword = norm(os.getenv("CALENDAR_KEYWORD", "suple"))

    credentials = Credentials.from_service_account_info(
        json.loads(creds_json), scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    service = build("calendar", "v3", credentials=credentials, cache_discovery=False)

    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=120)).isoformat()
    time_max = (now + timedelta(days=400)).isoformat()

    eventos, page = [], None
    while True:
        resp = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
            maxResults=250,
            timeZone=TZ,
            pageToken=page,
        ).execute()

        for e in resp.get("items", []):
            if e.get("status") == "cancelled" or SYNC_ID.match(e.get("id", "")):
                continue
            titulo = (e.get("summary") or "").strip()
            desc = (e.get("description") or "").strip()
            if keyword not in norm(titulo + " " + desc):
                continue
            start, end = e.get("start", {}), e.get("end", {})
            ev = {"id": e["id"], "titulo": titulo or "(sin título)"}
            if "date" in start:                      # evento de día completo (fin exclusivo)
                ev["inicio"], ev["fin"] = start["date"], end.get("date", start["date"])
            elif "dateTime" in start:                # evento con hora (ya en hora de Canarias)
                ev["inicio"] = start["dateTime"][:10]
                ev["hora"] = start["dateTime"][11:16]
                ev["fin"] = (datetime.fromisoformat(end["dateTime"][:10]) + timedelta(days=1)).date().isoformat() \
                    if end.get("dateTime") else None
            else:
                continue
            eventos.append(ev)

        page = resp.get("nextPageToken")
        if not page:
            break

    eventos.sort(key=lambda x: (x["inicio"], x.get("hora", ""), x["id"]))
    out = Path(__file__).resolve().parent.parent / "calendar_events.json"
    out.write_text(json.dumps({"eventos": eventos}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Eventos manuales exportados: {len(eventos)} (palabra clave: '{keyword}')")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
