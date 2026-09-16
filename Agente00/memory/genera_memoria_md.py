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


TZ_NAME = "America/Argentina/Buenos_Aires"
TZ = ZoneInfo(TZ_NAME)

AGENT_ID = "main"
PAGE_SIZE = 20

RC_OK = 0
RC_ERROR = 1
RC_SIN_ACTIVIDAD = 3


def localizar_openclaw():
    candidatos = [
        shutil.which("openclaw"),
        str(Path.home() / ".npm-global/bin/openclaw"),
        str(Path.home() / ".local/bin/openclaw"),
        "/home/linuxbrew/.linuxbrew/bin/openclaw",
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


def ejecutar_json(cmd, timeout=70):
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
            f"No se pudo interpretar la salida JSON: {exc}"
        ) from exc


def normalizar_user_id(valor):
    if not valor:
        return None

    valor = str(valor).strip()

    if valor.startswith("googlechat:"):
        valor = valor[len("googlechat:"):]

    if valor.isdigit():
        valor = f"users/{valor}"

    if valor.startswith("users/"):
        return valor

    return None


def validar_fecha(valor):
    try:
        return datetime.strptime(
            valor,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        raise ValueError(
            "La fecha debe tener formato YYYY-MM-DD."
        )


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


def user_ids_participantes(session):
    encontrados = set()

    for participante in (
        session.get("participants")
        or []
    ):
        if not isinstance(participante, dict):
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
            encontrados.add(user_id)

    return encontrados


def llamar_chat_history(
    openclaw,
    session_key,
    limit=PAGE_SIZE,
    offset=0,
):
    params = {
        "sessionKey": session_key,
        "limit": limit,
    }

    if offset:
        params["offset"] = offset

    params_json = json.dumps(
        params,
        separators=(",", ":"),
    )

    return ejecutar_json(
        [
            openclaw,
            "gateway",
            "call",
            "chat.history",
            "--params",
            params_json,
            "--timeout",
            "60000",
            "--json",
        ],
        timeout=70,
    )


def obtener_info_sesion(
    openclaw,
    session_key,
):
    data = llamar_chat_history(
        openclaw,
        session_key,
        limit=1,
        offset=0,
    )

    return (
        data.get("sessionInfo")
        or {}
    )


def buscar_sesiones_usuario(
    openclaw,
    user_id,
):
    payload = listar_sesiones(
        openclaw
    )

    sesiones = []

    nombre = None

    for session in (
        payload.get("sessions")
        or []
    ):
        if not isinstance(session, dict):
            continue

        session_key = session.get("key")

        if not session_key:
            continue

        if (
            ":googlechat:direct:"
            not in session_key
        ):
            continue

        participantes = (
            user_ids_participantes(
                session
            )
        )

        # Si sessions.list identifica
        # claramente a otro usuario,
        # no hace falta consultar
        # chat.history.
        if (
            participantes
            and user_id
            not in participantes
        ):
            continue

        try:
            info = obtener_info_sesion(
                openclaw,
                session_key,
            )

        except Exception:
            # Si participants ya confirma
            # al usuario, conservamos
            # igualmente la sesión.
            if user_id in participantes:
                sesiones.append(
                    {
                        "key": session_key,
                        "sessionId": (
                            session.get(
                                "sessionId"
                            )
                        ),
                    }
                )

            continue

        origin = (
            info.get("origin")
            or {}
        )

        origen_user_id = (
            normalizar_user_id(
                origin.get("from")
            )
        )

        if origen_user_id != user_id:
            continue

        session_id = (
            info.get("sessionId")
            or session.get("sessionId")
        )

        sesiones.append(
            {
                "key": session_key,
                "sessionId": session_id,
            }
        )

        nombre_detectado = (
            info.get("displayName")
            or origin.get("label")
        )

        if nombre_detectado:
            nombre = nombre_detectado

    # Evitar claves duplicadas.
    sesiones_unicas = []
    vistas = set()

    for sesion in sesiones:
        key = sesion["key"]

        if key in vistas:
            continue

        vistas.add(key)
        sesiones_unicas.append(
            sesion
        )

    return (
        nombre or user_id,
        sesiones_unicas,
    )


def timestamp_local(timestamp_ms):
    if timestamp_ms is None:
        return None

    try:
        timestamp_ms = int(
            timestamp_ms
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    return datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=TZ,
    )


def extraer_texto(content):
    if isinstance(content, str):
        texto = content.strip()

        return texto or None

    if not isinstance(content, list):
        return None

    textos = []

    for item in content:
        if not isinstance(item, dict):
            continue

        if item.get("type") != "text":
            continue

        texto = item.get("text")

        if not isinstance(texto, str):
            continue

        texto = texto.strip()

        if texto:
            textos.append(texto)

    if not textos:
        return None

    return "\n".join(textos)


def obtener_mensajes_fecha(
    openclaw,
    session_key,
    fecha_objetivo,
):
    offset = 0
    mensajes = []

    while True:
        data = llamar_chat_history(
            openclaw,
            session_key,
            limit=PAGE_SIZE,
            offset=offset,
        )

        pagina = (
            data.get("messages")
            or []
        )

        if not pagina:
            break

        fechas_pagina = []

        for mensaje in pagina:
            if not isinstance(
                mensaje,
                dict,
            ):
                continue

            fecha_hora = (
                timestamp_local(
                    mensaje.get(
                        "timestamp"
                    )
                )
            )

            if fecha_hora is None:
                continue

            fechas_pagina.append(
                fecha_hora.date()
            )

            if (
                fecha_hora.date()
                != fecha_objetivo
            ):
                continue

            role = mensaje.get(
                "role"
            )

            if role not in (
                "user",
                "assistant",
            ):
                continue

            texto = extraer_texto(
                mensaje.get(
                    "content"
                )
            )

            if not texto:
                continue

            openclaw_meta = (
                mensaje.get(
                    "__openclaw"
                )
                or {}
            )

            mensaje_id = (
                openclaw_meta.get("id")
                or mensaje.get(
                    "idempotencyKey"
                )
                or ""
            )

            mensajes.append(
                {
                    "id": mensaje_id,
                    "timestamp": (
                        fecha_hora
                    ),
                    "role": role,
                    "text": texto,
                }
            )

        # chat.history devuelve primero
        # el tramo más reciente y offset
        # creciente retrocede en el
        # historial.
        #
        # Si ya alcanzamos mensajes
        # anteriores a la fecha pedida,
        # no hace falta seguir paginando.
        if (
            fechas_pagina
            and min(fechas_pagina)
            < fecha_objetivo
        ):
            break

        if not data.get("hasMore"):
            break

        next_offset = data.get(
            "nextOffset"
        )

        if next_offset is None:
            break

        try:
            next_offset = int(
                next_offset
            )

        except (
            TypeError,
            ValueError,
        ):
            break

        if next_offset <= offset:
            break

        offset = next_offset

    return mensajes


def deduplicar_mensajes(
    mensajes,
):
    resultado = []
    vistos = set()

    for mensaje in mensajes:
        clave = (
            mensaje.get("id")
            or "",
            mensaje["timestamp"].timestamp(),
            mensaje["role"],
            mensaje["text"],
        )

        if clave in vistos:
            continue

        vistos.add(clave)

        resultado.append(
            mensaje
        )

    return resultado


def generar_markdown(
    nombre,
    user_id,
    fecha_objetivo,
    sesiones,
    mensajes,
):
    mensajes = sorted(
        mensajes,
        key=lambda m: (
            m["timestamp"],
            m.get("id") or "",
        ),
    )

    mensajes = (
        deduplicar_mensajes(
            mensajes
        )
    )

    fecha_visible = (
        fecha_objetivo.strftime(
            "%d/%m/%Y"
        )
    )

    inicio = (
        mensajes[0]["timestamp"]
        .strftime("%H:%M:%S")
    )

    fin = (
        mensajes[-1]["timestamp"]
        .strftime("%H:%M:%S")
    )

    lineas = []

    lineas.append(
        "# Memoria de conversación "
        f"— {nombre}"
    )

    lineas.append("")
    lineas.append("## Datos")
    lineas.append("")

    lineas.append(
        f"- **Fecha:** "
        f"{fecha_visible}"
    )

    lineas.append(
        f"- **Usuario:** "
        f"{nombre}"
    )

    lineas.append(
        "- **ID Google Chat:** "
        f"`{user_id}`"
    )

    lineas.append(
        "- **Canal:** Google Chat"
    )

    lineas.append(
        "- **Zona horaria:** "
        f"{TZ_NAME}"
    )

    lineas.append(
        "- **Cantidad de "
        "intervenciones:** "
        f"{len(mensajes)}"
    )

    lineas.append(
        f"- **Inicio:** {inicio}"
    )

    lineas.append(
        f"- **Fin:** {fin}"
    )

    lineas.append("")
    lineas.append(
        "## Sesiones revisadas"
    )
    lineas.append("")

    for sesion in sesiones:
        lineas.append(
            f"- `{sesion['key']}`"
        )

    lineas.append("")
    lineas.append(
        "## Archivos revisados"
    )
    lineas.append("")

    for sesion in sesiones:
        session_id = (
            sesion.get(
                "sessionId"
            )
        )

        if session_id:
            lineas.append(
                "- `chat.history` "
                f"(`{session_id}`)"
            )
        else:
            lineas.append(
                "- `chat.history`"
            )

    lineas.append("")
    lineas.append("---")
    lineas.append("")
    lineas.append(
        "## Transcripción completa"
    )
    lineas.append("")

    for mensaje in mensajes:
        fecha_hora = (
            mensaje["timestamp"]
            .strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )

        if (
            mensaje["role"]
            == "user"
        ):
            autor = nombre
        else:
            autor = "Agente"

        lineas.append(
            f"### [{fecha_hora}] "
            f"{autor}"
        )

        lineas.append("")
        lineas.append(
            mensaje["text"]
        )
        lineas.append("")
        lineas.append("---")
        lineas.append("")

    lineas.append("## Origen")
    lineas.append("")

    lineas.append(
        "Memoria generada "
        "automáticamente a partir "
        "del historial local de "
        "sesiones de OpenClaw."
    )

    lineas.append("")

    return "\n".join(
        lineas
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Genera una memoria "
            "Markdown diaria a partir "
            "de una conversación de "
            "Google Chat en OpenClaw."
        )
    )

    parser.add_argument(
        "user_id",
        help=(
            "ID Google Chat. "
            "Ejemplo: "
            "users/123456789"
        ),
    )

    parser.add_argument(
        "fecha",
        help=(
            "Fecha a generar en "
            "formato YYYY-MM-DD."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Ruta de salida opcional."
        ),
    )

    args = parser.parse_args()

    user_id = (
        normalizar_user_id(
            args.user_id
        )
    )

    if not user_id:
        print(
            "ERROR | ID Google Chat "
            "inválido.",
            file=sys.stderr,
        )

        return RC_ERROR

    try:
        fecha_objetivo = (
            validar_fecha(
                args.fecha
            )
        )

    except ValueError as exc:
        print(
            f"ERROR | {exc}",
            file=sys.stderr,
        )

        return RC_ERROR

    try:
        openclaw = (
            localizar_openclaw()
        )

        nombre, sesiones = (
            buscar_sesiones_usuario(
                openclaw,
                user_id,
            )
        )

    except Exception as exc:
        print(
            "ERROR | No se pudieron "
            "obtener las sesiones: "
            f"{exc}",
            file=sys.stderr,
        )

        return RC_ERROR

    if not sesiones:
        print(
            "Sin sesiones Google Chat "
            f"para {user_id}."
        )

        return RC_SIN_ACTIVIDAD

    mensajes = []

    sesiones_con_actividad = []

    for sesion in sesiones:
        try:
            mensajes_sesion = (
                obtener_mensajes_fecha(
                    openclaw,
                    sesion["key"],
                    fecha_objetivo,
                )
            )

        except Exception as exc:
            print(
                "ERROR | No se pudo "
                "leer "
                f"{sesion['key']}: "
                f"{exc}",
                file=sys.stderr,
            )

            return RC_ERROR

        if mensajes_sesion:
            sesiones_con_actividad.append(
                sesion
            )

            mensajes.extend(
                mensajes_sesion
            )

    if not mensajes:
        print(
            "Sin actividad para "
            f"{user_id} en "
            f"{args.fecha}."
        )

        return RC_SIN_ACTIVIDAD

    mensajes = sorted(
        deduplicar_mensajes(
            mensajes
        ),
        key=lambda m: (
            m["timestamp"],
            m.get("id") or "",
        ),
    )

    contenido = generar_markdown(
        nombre,
        user_id,
        fecha_objetivo,
        sesiones_con_actividad,
        mensajes,
    )

    if args.output:
        salida = Path(
            args.output
        ).expanduser()

    else:
        user_filename = (
            user_id.replace(
                "/",
                "_",
            )
        )

        salida = (
            Path.home()
            / ".openclaw"
            / "workspace"
            / "memory"
            / (
                "MEMORY-"
                f"{user_filename}-"
                f"{args.fecha}.md"
            )
        )

    salida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    salida.write_text(
        contenido,
        encoding="utf-8",
    )

    print(
        f"Usuario: {nombre}"
    )

    print(
        f"ID Google Chat: "
        f"{user_id}"
    )

    print(
        f"Fecha: "
        f"{args.fecha}"
    )

    print(
        "Intervenciones: "
        f"{len(mensajes)}"
    )

    print(
        "Memoria generada: "
        f"{salida}"
    )

    # Purgar secretos del archivo generado
    purgador = (
        Path(__file__).resolve().parent
        / "purga_secretos_memoria_md.py"
    )

    if not purgador.is_file():
        print(
            f"ERROR | No se encontró el purgador: {purgador}",
            file=sys.stderr,
        )
        return RC_ERROR

    resultado_purga = subprocess.run(
        [
            sys.executable,
            str(purgador),
            str(salida),
        ]
    )

    if resultado_purga.returncode != 0:
        print(
            f"ERROR | Falló la purga de secretos: {salida}",
            file=sys.stderr,
        )
        return RC_ERROR

    return RC_OK


if __name__ == "__main__":
    sys.exit(main())
