#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


TZ = ZoneInfo("America/Argentina/Buenos_Aires")

AGENT_ID = "main"

GENERATOR = (
    Path.home()
    / ".openclaw/workspace/memory/genera_memoria_md.py"
)

RC_OK = 0
RC_SIN_ACTIVIDAD = 3


def localizar_openclaw():
    candidatos = [
        shutil.which("openclaw"),
        str(Path.home() / ".npm-global/bin/openclaw"),
        str(Path.home() / ".local/bin/openclaw"),
        "/usr/local/bin/openclaw",
        "/usr/bin/openclaw",
    ]

    for candidato in candidatos:

        if (
            candidato
            and Path(candidato).is_file()
            and os.access(candidato, os.X_OK)
        ):
            return candidato

    raise RuntimeError(
        "No se encontró el ejecutable 'openclaw'."
    )


def ejecutar_json(cmd, timeout=60):

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )

    if proc.returncode != 0:

        detalle = (
            proc.stderr
            or proc.stdout
            or ""
        ).strip()

        raise RuntimeError(
            f"Comando falló con código "
            f"{proc.returncode}: "
            f"{detalle or 'sin detalle'}"
        )

    salida = proc.stdout.strip()

    if not salida:

        raise RuntimeError(
            "El comando no devolvió salida JSON."
        )

    try:

        return json.loads(salida)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"No se pudo interpretar "
            f"la salida JSON: {exc}"
        ) from exc


def listar_sesiones(openclaw):

    return ejecutar_json(
        [
            openclaw,
            "sessions",
            "--agent",
            AGENT_ID,
            "--limit",
            "all",
            "--json",
        ],
        timeout=60,
    )


def obtener_metadata_chat(
    openclaw,
    session_key,
):

    params = json.dumps(
        {
            "sessionKey": session_key,
            "limit": 1,
        },
        separators=(",", ":"),
    )

    data = ejecutar_json(
        [
            openclaw,
            "gateway",
            "call",
            "chat.history",
            "--params",
            params,
            "--timeout",
            "60000",
            "--json",
        ],
        timeout=70,
    )

    return data.get("sessionInfo") or {}


def normalizar_user_id(valor):

    if not valor:
        return None

    valor = str(valor).strip()

    if valor.startswith("googlechat:"):

        valor = valor[
            len("googlechat:"):
        ]

    if valor.startswith("users/"):
        return valor

    return None


def user_id_desde_participantes(
    session,
):

    for participante in (
        session.get("participants")
        or []
    ):

        if not isinstance(
            participante,
            dict,
        ):
            continue

        identity = (
            participante.get("identity")
            or {}
        )

        if (
            identity.get("pluginId")
            != "googlechat"
        ):
            continue

        user_id = normalizar_user_id(
            identity.get("id")
        )

        if user_id:
            return user_id

    return None


def obtener_usuarios_googlechat(
    openclaw,
    sessions_payload,
):

    usuarios = {}

    for session in (
        sessions_payload.get("sessions")
        or []
    ):

        if not isinstance(
            session,
            dict,
        ):
            continue

        session_key = session.get("key")

        if not session_key:
            continue

        # Solo conversaciones directas
        # de Google Chat.
        if (
            ":googlechat:direct:"
            not in session_key
        ):
            continue

        # Primer intento:
        # obtener el usuario desde
        # participants de sessions.list.
        user_id = (
            user_id_desde_participantes(
                session
            )
        )

        nombre = None

        # chat.history nos da
        # sessionInfo completo,
        # incluyendo origin.from
        # y displayName.
        try:

            info = obtener_metadata_chat(
                openclaw,
                session_key,
            )

        except Exception:

            info = {}

        origin = (
            info.get("origin")
            or {}
        )

        user_id_metadata = (
            normalizar_user_id(
                origin.get("from")
            )
        )

        if user_id_metadata:
            user_id = user_id_metadata

        nombre = (
            info.get("displayName")
            or origin.get("label")
            or user_id
        )

        if not user_id:
            continue

        if user_id not in usuarios:

            usuarios[user_id] = {
                "nombre": (
                    nombre
                    or user_id
                ),
                "sesiones": [],
            }

        elif (
            nombre
            and usuarios[user_id]["nombre"]
            == user_id
        ):

            usuarios[user_id][
                "nombre"
            ] = nombre

        usuarios[user_id][
            "sesiones"
        ].append(session_key)

    return usuarios


def ejecutar_generador(
    user_id,
    fecha,
):

    if not GENERATOR.is_file():

        return (
            127,
            "",
            (
                "No existe el generador: "
                f"{GENERATOR}"
            ),
        )

    proc = subprocess.run(
        [
            str(GENERATOR),
            user_id,
            fecha,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    return (
        proc.returncode,
        proc.stdout.strip(),
        proc.stderr.strip(),
    )


def parsear_fecha(valor):

    if valor:

        try:

            return datetime.strptime(
                valor,
                "%Y-%m-%d",
            ).date().isoformat()

        except ValueError:

            raise SystemExit(
                "La fecha debe tener "
                "formato YYYY-MM-DD."
            )

    return (
        datetime.now(TZ)
        .date()
        .isoformat()
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Genera memorias Markdown "
            "diarias para usuarios "
            "de Google Chat."
        )
    )

    parser.add_argument(
        "fecha",
        nargs="?",
        help=(
            "Fecha a procesar en "
            "formato YYYY-MM-DD. "
            "Por defecto: hoy."
        ),
    )

    args = parser.parse_args()

    fecha = parsear_fecha(
        args.fecha
    )

    try:

        openclaw = (
            localizar_openclaw()
        )

        sessions_payload = (
            listar_sesiones(
                openclaw
            )
        )

        usuarios = (
            obtener_usuarios_googlechat(
                openclaw,
                sessions_payload,
            )
        )

    except Exception as exc:

        print(
            "ERROR | "
            "No se pudieron obtener "
            "las sesiones de OpenClaw: "
            f"{exc}"
        )

        return 1

    print(
        f"Fecha procesada: {fecha}"
    )

    print(
        "Usuarios Google Chat "
        f"detectados: {len(usuarios)}"
    )

    print()

    generadas = 0
    sin_actividad = 0
    errores = 0

    for user_id in sorted(
        usuarios,
        key=lambda uid: (
            usuarios[uid]["nombre"]
            or uid
        ).lower(),
    ):

        nombre = (
            usuarios[user_id][
                "nombre"
            ]
            or user_id
        )

        rc, stdout, stderr = (
            ejecutar_generador(
                user_id,
                fecha,
            )
        )

        if rc == RC_OK:

            generadas += 1

            print(
                f"OK | "
                f"{nombre} | "
                f"{user_id}"
            )

        elif rc == RC_SIN_ACTIVIDAD:

            sin_actividad += 1

        else:

            errores += 1

            detalle = (
                stderr
                or stdout
                or (
                    "código de salida "
                    f"{rc}"
                )
            )

            print(
                f"ERROR | "
                f"{nombre} | "
                f"{user_id} | "
                f"{detalle}"
            )

    print()

    print("Resumen")

    print(
        "Memorias generadas: "
        f"{generadas}"
    )

    print(
        "Usuarios sin actividad: "
        f"{sin_actividad}"
    )

    print(
        "Errores: "
        f"{errores}"
    )

    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
