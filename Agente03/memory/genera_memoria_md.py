#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ_NAME = "America/Argentina/Buenos_Aires"

SESSIONS_DIR = Path.home() / ".openclaw/agents/main/sessions"
SESSIONS_JSON = SESSIONS_DIR / "sessions.json"

MEMORY_DIR = Path.home() / ".openclaw/workspace/memory"


def normalizar_user_id(valor: str) -> str:
    valor = valor.strip()

    if valor.startswith("googlechat:"):
        valor = valor[len("googlechat:"):]

    if valor.isdigit():
        valor = f"users/{valor}"

    if not valor.startswith("users/"):
        raise ValueError(
            "El ID debe tener formato users/123456789... "
            "o ser solamente el número."
        )

    return valor


def user_id_para_archivo(user_id: str) -> str:
    return user_id.replace("/", "_")


def cargar_sessions():
    if not SESSIONS_JSON.exists():
        raise FileNotFoundError(f"No existe: {SESSIONS_JSON}")

    with SESSIONS_JSON.open(
        encoding="utf-8",
        errors="ignore"
    ) as f:
        return json.load(f)


def buscar_sesiones_usuario(sessions, user_id):
    buscado = f"googlechat:{user_id}"
    encontrados = []

    for session_key, data in sessions.items():
        if not isinstance(data, dict):
            continue

        origin = data.get("origin") or {}

        if origin.get("from") == buscado:
            encontrados.append((session_key, data))

    if not encontrados:
        raise RuntimeError(
            f"No se encontró ninguna sesión de Google Chat para {user_id}"
        )

    return encontrados


def extraer_fecha_local(ts, tz):
    if not ts or not isinstance(ts, str):
        return None

    try:
        return datetime.fromisoformat(
            ts.replace("Z", "+00:00")
        ).astimezone(tz)
    except Exception:
        return None


def extraer_texto(content):
    textos = []

    if isinstance(content, str):
        if content.strip():
            textos.append(content.strip())

    elif isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue

            if item.get("type") == "text":
                texto = item.get("text", "")

                if texto and texto.strip():
                    textos.append(texto.strip())

    return "\n".join(textos).strip()


def archivos_de_sesion(session_id):
    archivos = []

    for f in SESSIONS_DIR.glob(session_id + "*"):
        nombre = f.name

        if not f.is_file():
            continue

        # No incorporar trayectoria interna del agente.
        if nombre.endswith(".trajectory.jsonl"):
            continue

        if nombre == "sessions.json":
            continue

        # Incluye .jsonl y .jsonl.reset.*
        if ".jsonl" in nombre:
            archivos.append(f)

    return sorted(archivos)


def recolectar_mensajes(session_ids, fecha_buscada, tz):
    mensajes = []
    vistos = set()

    for session_id in session_ids:
        for archivo in archivos_de_sesion(session_id):

            try:
                fh = archivo.open(
                    encoding="utf-8",
                    errors="ignore"
                )
            except Exception:
                continue

            with fh:
                for linea in fh:

                    try:
                        obj = json.loads(linea)
                    except Exception:
                        continue

                    if obj.get("type") != "message":
                        continue

                    msg = obj.get("message")

                    if not isinstance(msg, dict):
                        continue

                    rol = msg.get("role")

                    if rol not in ("user", "assistant"):
                        continue

                    dt = extraer_fecha_local(
                        obj.get("timestamp"),
                        tz
                    )

                    if dt is None:
                        continue

                    if dt.strftime("%Y-%m-%d") != fecha_buscada:
                        continue

                    texto = extraer_texto(
                        msg.get("content", "")
                    )

                    if not texto:
                        continue

                    if rol == "user":
                        nombre = msg.get("senderName") or "Usuario"
                    else:
                        nombre = "Agente"

                    dedupe_key = (
                        obj.get("id"),
                        obj.get("timestamp"),
                        rol,
                        texto
                    )

                    if dedupe_key in vistos:
                        continue

                    vistos.add(dedupe_key)

                    mensajes.append({
                        "dt": dt,
                        "timestamp": dt.strftime(
                            "%d/%m/%Y %H:%M:%S"
                        ),
                        "rol": rol,
                        "nombre": nombre,
                        "texto": texto,
                        "archivo": archivo.name
                    })

    mensajes.sort(key=lambda x: x["dt"])

    return mensajes


def generar_markdown(
    mensajes,
    user_id,
    fecha,
    nombre_usuario,
    sesiones_revisadas
):
    fecha_display = datetime.strptime(
        fecha,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    inicio = mensajes[0]["dt"].strftime("%H:%M:%S")
    fin = mensajes[-1]["dt"].strftime("%H:%M:%S")

    archivos_revisados = sorted({
        m["archivo"]
        for m in mensajes
    })

    lineas = [
        f"# Memoria de conversación — {nombre_usuario}",
        "",
        "## Datos",
        "",
        f"- **Fecha:** {fecha_display}",
        f"- **Usuario:** {nombre_usuario}",
        f"- **ID Google Chat:** `{user_id}`",
        "- **Canal:** Google Chat",
        f"- **Zona horaria:** {TZ_NAME}",
        f"- **Cantidad de intervenciones:** {len(mensajes)}",
        f"- **Inicio:** {inicio}",
        f"- **Fin:** {fin}",
        "",
        "## Sesiones revisadas",
        "",
    ]

    for session_key in sesiones_revisadas:
        lineas.append(f"- `{session_key}`")

    lineas.extend([
        "",
        "## Archivos revisados",
        "",
    ])

    for archivo in archivos_revisados:
        lineas.append(f"- `{archivo}`")

    lineas.extend([
        "",
        "---",
        "",
        "## Transcripción completa",
        "",
    ])

    for m in mensajes:

        titulo = (
            m["nombre"]
            if m["rol"] == "user"
            else "Agente"
        )

        lineas.extend([
            f"### [{m['timestamp']}] {titulo}",
            "",
            m["texto"],
            "",
            "---",
            "",
        ])

    lineas.extend([
        "## Origen",
        "",
        "Memoria generada automáticamente a partir "
        "del historial local de sesiones de OpenClaw.",
        "",
    ])

    return "\n".join(lineas)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Genera un archivo de memoria Markdown con toda "
            "la conversación diaria de un usuario de Google Chat."
        )
    )

    parser.add_argument(
        "user_id",
        help=(
            "ID de Google Chat. "
            "Ej.: users/112625344596118312340"
        )
    )

    parser.add_argument(
        "fecha",
        help="Fecha a exportar en formato YYYY-MM-DD"
    )

    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Ruta alternativa del archivo Markdown. "
            "Si se omite, se guarda automáticamente "
            "en ~/.openclaw/workspace/memory/"
        )
    )

    args = parser.parse_args()

    try:
        user_id = normalizar_user_id(args.user_id)

        datetime.strptime(
            args.fecha,
            "%Y-%m-%d"
        )

    except Exception as e:
        print(
            f"ERROR: {e}",
            file=sys.stderr
        )
        sys.exit(1)

    try:
        sessions = cargar_sessions()

        sesiones_usuario = buscar_sesiones_usuario(
            sessions,
            user_id
        )

    except Exception as e:
        print(
            f"ERROR: {e}",
            file=sys.stderr
        )
        sys.exit(2)

    session_ids = []
    session_keys = []
    nombre_usuario = None

    for session_key, data in sesiones_usuario:

        session_keys.append(session_key)

        origin = data.get("origin") or {}

        if not nombre_usuario:
            nombre_usuario = origin.get("label")

        ids = list(
            data.get("usageFamilySessionIds") or []
        )

        if data.get("sessionId"):
            ids.append(data["sessionId"])

        for sid in ids:
            if sid and sid not in session_ids:
                session_ids.append(sid)

    if not nombre_usuario:
        nombre_usuario = user_id

    mensajes = recolectar_mensajes(
        session_ids,
        args.fecha,
        ZoneInfo(TZ_NAME)
    )

    if not mensajes:
        print(
            f"No se encontraron mensajes de "
            f"{user_id} para la fecha {args.fecha}.",
            file=sys.stderr
        )
        sys.exit(3)

    for m in mensajes:
        if (
            m["rol"] == "user"
            and m["nombre"] != "Usuario"
        ):
            nombre_usuario = m["nombre"]
            break

    documento = generar_markdown(
        mensajes,
        user_id,
        args.fecha,
        nombre_usuario,
        session_keys
    )

    if args.output:

        salida = Path(
            args.output
        ).expanduser()

    else:

        MEMORY_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        id_archivo = user_id_para_archivo(
            user_id
        )

        salida = (
            MEMORY_DIR
            / f"MEMORY-{id_archivo}-{args.fecha}.md"
        )

    salida.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    salida.write_text(
        documento,
        encoding="utf-8"
    )

    print(f"Usuario: {nombre_usuario}")
    print(f"ID Google Chat: {user_id}")
    print(f"Fecha: {args.fecha}")
    print(f"Intervenciones: {len(mensajes)}")
    print(f"Memoria generada: {salida}")


if __name__ == "__main__":
    main()
