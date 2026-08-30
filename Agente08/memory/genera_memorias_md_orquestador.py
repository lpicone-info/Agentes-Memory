#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_NAME = "America/Argentina/Buenos_Aires"

SESSIONS_JSON = (
    Path.home()
    / ".openclaw/agents/main/sessions/sessions.json"
)

SCRIPT_DIR = Path(__file__).resolve().parent
GENERADOR = SCRIPT_DIR / "genera_memoria_md.py"


def cargar_sessions():
    if not SESSIONS_JSON.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {SESSIONS_JSON}"
        )

    with SESSIONS_JSON.open(
        encoding="utf-8",
        errors="ignore"
    ) as f:
        return json.load(f)


def obtener_usuarios_googlechat(sessions):
    usuarios = {}

    for session_key, data in sessions.items():

        if not isinstance(data, dict):
            continue

        origin = data.get("origin") or {}

        origen_usuario = origin.get("from")

        if not origen_usuario:
            continue

        if not origen_usuario.startswith("googlechat:users/"):
            continue

        user_id = origen_usuario[len("googlechat:"):]

        if user_id not in usuarios:
            usuarios[user_id] = {
                "nombre": origin.get("label") or user_id,
                "sesiones": []
            }

        usuarios[user_id]["sesiones"].append(session_key)

    return usuarios


def ejecutar_generador(user_id, fecha):
    resultado = subprocess.run(
        [
            sys.executable,
            str(GENERADOR),
            user_id,
            fecha
        ],
        capture_output=True,
        text=True
    )

    return resultado


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Genera automáticamente las memorias Markdown "
            "de todos los usuarios de Google Chat que hayan "
            "tenido actividad durante una fecha."
        )
    )

    parser.add_argument(
        "fecha",
        nargs="?",
        help=(
            "Fecha a procesar en formato YYYY-MM-DD. "
            "Si se omite, se procesa el día actual."
        )
    )

    args = parser.parse_args()

    if args.fecha:
        try:
            datetime.strptime(
                args.fecha,
                "%Y-%m-%d"
            )
        except ValueError:
            print(
                "ERROR: la fecha debe tener formato YYYY-MM-DD.",
                file=sys.stderr
            )
            sys.exit(1)

        fecha = args.fecha

    else:
        fecha = datetime.now(
            ZoneInfo(TZ_NAME)
        ).strftime("%Y-%m-%d")

    if not GENERADOR.exists():
        print(
            f"ERROR: no existe el generador: {GENERADOR}",
            file=sys.stderr
        )
        sys.exit(2)

    try:
        sessions = cargar_sessions()
        usuarios = obtener_usuarios_googlechat(sessions)

    except Exception as e:
        print(
            f"ERROR: {e}",
            file=sys.stderr
        )
        sys.exit(3)

    if not usuarios:
        print("No se encontraron usuarios directos de Google Chat.")
        sys.exit(0)

    generadas = []
    sin_actividad = []
    errores = []

    print(f"Fecha procesada: {fecha}")
    print(f"Usuarios Google Chat detectados: {len(usuarios)}")
    print()

    for user_id, datos in sorted(usuarios.items()):

        nombre = datos["nombre"]

        resultado = ejecutar_generador(
            user_id,
            fecha
        )

        if resultado.returncode == 0:

            generadas.append(
                (user_id, nombre)
            )

            print(
                f"OK   | {nombre} | {user_id}"
            )

        elif resultado.returncode == 3:

            sin_actividad.append(
                (user_id, nombre)
            )

        else:

            mensaje = (
                resultado.stderr.strip()
                or resultado.stdout.strip()
                or f"código {resultado.returncode}"
            )

            errores.append(
                (user_id, nombre, mensaje)
            )

            print(
                f"ERROR | {nombre} | {user_id} | {mensaje}"
            )

    print()
    print("Resumen")
    print("-------")
    print(f"Memorias generadas: {len(generadas)}")
    print(f"Usuarios sin actividad: {len(sin_actividad)}")
    print(f"Errores: {len(errores)}")

    if errores:
        sys.exit(4)


if __name__ == "__main__":
    main()
