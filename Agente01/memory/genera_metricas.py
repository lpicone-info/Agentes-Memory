#!/usr/bin/env python3

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


TZ_NAME = "America/Argentina/Buenos_Aires"
TZ = ZoneInfo(TZ_NAME)

AGENT_ID = "main"
PAGE_SIZE = 20

RC_OK = 0
RC_ERROR = 1
RC_SIN_ACTIVIDAD = 3


PATRONES_TAREAS = (
    (
        "R",
        re.compile(
            r"(?i)(?<![A-Z0-9])(?:REDMINE|RM|R)\s*(?:#|N[RO]?\.?|N[°º])?\s*[-:]?\s*(\d+)(?!\d)"
        ),
    ),
    (
        "I",
        re.compile(
            r"(?i)(?<![A-Z0-9])(?:INVGATE|INVG|TICKET|I)\s*(?:#|N[RO]?\.?|N[°º])?\s*[-:]?\s*(\d+)(?!\d)"
        ),
    ),
)


def localizar_openclaw():
    candidatos = [
        shutil.which("openclaw"),
        os.path.expanduser("~/.npm-global/bin/openclaw"),
        os.path.expanduser("~/.local/bin/openclaw"),
        "/home/linuxbrew/.linuxbrew/bin/openclaw",
        "/usr/local/bin/openclaw",
        "/usr/bin/openclaw",
    ]

    for candidato in candidatos:
        if (
            candidato
            and os.path.isfile(candidato)
            and os.access(candidato, os.X_OK)
        ):
            return candidato

    raise RuntimeError(
        "No se encontro el ejecutable 'openclaw'."
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
            f"Comando fallo con codigo "
            f"{proc.returncode}: "
            f"{detalle or 'sin detalle'}"
        )

    salida = proc.stdout.strip()

    if not salida:
        raise RuntimeError(
            "El comando no devolvio salida JSON."
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


def obtener_nombre_agente(openclaw):
    try:
        identidad = ejecutar_json(
            [
                openclaw,
                "config",
                "get",
                f"agents.entries.{AGENT_ID}.identity",
                "--json",
            ],
            timeout=30,
        )

        if isinstance(identidad, dict):
            nombre = identidad.get("name")

            if isinstance(nombre, str) and nombre.strip():
                return nombre.strip()

    except Exception:
        pass

    return AGENT_ID


def obtener_id_agente():
    agents_md = os.path.expanduser(
        "~/.openclaw/workspace/AGENTS.md"
    )

    try:
        with open(
            agents_md,
            "r",
            encoding="utf-8",
        ) as archivo:
            contenido = archivo.read()

        coincidencia = re.search(
            r"\((Agente\d+)\)",
            contenido,
            flags=re.IGNORECASE,
        )

        if coincidencia:
            return coincidencia.group(1)

    except OSError:
        pass

    return AGENT_ID


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


def ruta_base_agente():
    return os.path.expanduser(
        "~/.openclaw/agents/main/agent/openclaw-agent.sqlite"
    )


def obtener_cadena_session_ids(
    conexion,
    session_id,
):
    session_ids = []
    vistos = set()
    actual = session_id

    while actual and actual not in vistos:
        vistos.add(actual)
        session_ids.append(actual)

        fila = conexion.execute(
            "SELECT previous_session_id "
            "FROM session_windows "
            "WHERE session_id = ?",
            (actual,),
        ).fetchone()

        if not fila:
            break

        actual = fila[0]

    return session_ids


def obtener_mensajes_fecha(
    session_id,
    fecha_objetivo,
):
    if not session_id:
        return []

    db_path = ruta_base_agente()

    if not os.path.isfile(db_path):
        raise RuntimeError(
            f"No existe la base del agente: {db_path}"
        )

    mensajes = []

    uri = f"file:{db_path}?mode=ro"

    with sqlite3.connect(
        uri,
        uri=True,
        timeout=30,
    ) as conexion:
        conexion.execute("PRAGMA query_only = ON")

        session_ids = obtener_cadena_session_ids(
            conexion,
            session_id,
        )

        for sid in session_ids:
            filas = conexion.execute(
                "SELECT message_id, role, text, timestamp "
                "FROM session_transcript_fts "
                "WHERE session_id = ?",
                (sid,),
            ).fetchall()

            for mensaje_id, role, texto, timestamp in filas:
                if role not in (
                    "user",
                    "assistant",
                ):
                    continue

                if not isinstance(texto, str):
                    continue

                texto = texto.strip()

                if not texto:
                    continue

                fecha_hora = timestamp_local(
                    timestamp
                )

                if fecha_hora is None:
                    continue

                if (
                    fecha_hora.date()
                    != fecha_objetivo
                ):
                    continue

                mensajes.append(
                    {
                        "id": mensaje_id or "",
                        "timestamp": fecha_hora,
                        "role": role,
                        "text": texto,
                    }
                )

    return mensajes


def deduplicar_mensajes(mensajes):
    resultado = []
    vistos = set()

    for mensaje in mensajes:
        clave = (
            mensaje.get("id") or "",
            mensaje["timestamp"].timestamp(),
            mensaje["role"],
            mensaje["text"],
        )

        if clave in vistos:
            continue

        vistos.add(clave)
        resultado.append(mensaje)

    return resultado


def calcular_tiempo_trabajo_segundos(mensajes):
    total = 0.0
    ultimo_usuario = None
    ultima_respuesta_agente = None

    for mensaje in mensajes:
        if mensaje["role"] == "user":
            if (
                ultimo_usuario is not None
                and ultima_respuesta_agente is not None
            ):
                diferencia = (
                    ultima_respuesta_agente
                    - ultimo_usuario
                ).total_seconds()

                if diferencia > 0:
                    total += diferencia

            ultimo_usuario = mensaje["timestamp"]
            ultima_respuesta_agente = None
            continue

        if (
            mensaje["role"] == "assistant"
            and ultimo_usuario is not None
        ):
            ultima_respuesta_agente = mensaje["timestamp"]

    if (
        ultimo_usuario is not None
        and ultima_respuesta_agente is not None
    ):
        diferencia = (
            ultima_respuesta_agente
            - ultimo_usuario
        ).total_seconds()

        if diferencia > 0:
            total += diferencia

    return int(round(total))


def extraer_tareas(mensajes):
    encontradas = []
    vistas = set()

    for mensaje in mensajes:
        texto = mensaje.get("text") or ""
        coincidencias = []

        for prefijo, patron in PATRONES_TAREAS:
            for match in patron.finditer(texto):
                numero = match.group(1)
                tarea = f"{prefijo}{int(numero)}"
                coincidencias.append(
                    (match.start(), tarea)
                )

        for _, tarea in sorted(
            coincidencias,
            key=lambda item: item[0],
        ):
            if tarea in vistas:
                continue

            vistas.add(tarea)
            encontradas.append(tarea)

    return encontradas


def formatear_duracion(segundos):
    segundos = max(0, int(segundos))
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)

    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def recortar(valor, ancho_maximo):
    texto = str(valor)

    if len(texto) <= ancho_maximo:
        return texto

    if ancho_maximo <= 3:
        return texto[:ancho_maximo]

    return texto[:ancho_maximo - 3] + "..."


def imprimir_grilla(fila):
    columnas = [
        ("ID agente", "agente_id", 12),
        ("Agente", "agente", 28),
        ("Usuario", "usuario", 24),
        ("ID usuario", "usuario_id", 28),
        ("Fecha", "fecha", 10),
        ("Inicio", "inicio", 8),
        ("Fin", "fin", 8),
        ("Interacciones", "interacciones", 13),
        ("Tiempo agente", "tiempo_agente", 13),
        ("Tareas", "tareas", 36),
    ]

    anchos = []

    for titulo, clave, ancho_maximo in columnas:
        valor = recortar(
            fila.get(clave, ""),
            ancho_maximo,
        )
        fila[clave] = valor
        anchos.append(
            max(len(titulo), len(valor))
        )

    separador = "+-" + "-+-".join(
        "-" * ancho
        for ancho in anchos
    ) + "-+"

    cabecera = "| " + " | ".join(
        titulo.ljust(ancho)
        for (titulo, _, _), ancho
        in zip(columnas, anchos)
    ) + " |"

    valores = "| " + " | ".join(
        str(fila.get(clave, "")).ljust(ancho)
        for (_, clave, _), ancho
        in zip(columnas, anchos)
    ) + " |"

    print(separador)
    print(cabecera)
    print(separador)
    print(valores)
    print(separador)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Calcula metricas diarias de una "
            "conversacion de Google Chat en OpenClaw."
        )
    )

    parser.add_argument(
        "user_id",
        help=(
            "ID Google Chat. "
            "Ejemplo: users/123456789"
        ),
    )

    parser.add_argument(
        "fecha",
        help=(
            "Fecha a procesar en formato YYYY-MM-DD."
        ),
    )

    args = parser.parse_args()

    user_id = normalizar_user_id(
        args.user_id
    )

    if not user_id:
        print(
            "ERROR | ID Google Chat invalido.",
            file=sys.stderr,
        )
        return RC_ERROR

    try:
        fecha_objetivo = validar_fecha(
            args.fecha
        )

    except ValueError as exc:
        print(
            f"ERROR | {exc}",
            file=sys.stderr,
        )
        return RC_ERROR

    try:
        openclaw = localizar_openclaw()
        agente_id = obtener_id_agente()
        agente = obtener_nombre_agente(
            openclaw
        )

        nombre, sesiones = (
            buscar_sesiones_usuario(
                openclaw,
                user_id,
            )
        )

    except Exception as exc:
        print(
            "ERROR | No se pudieron obtener "
            f"las sesiones: {exc}",
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

    for sesion in sesiones:
        try:
            mensajes.extend(
                obtener_mensajes_fecha(
                    sesion.get("sessionId"),
                    fecha_objetivo,
                )
            )

        except Exception as exc:
            print(
                "ERROR | No se pudo leer "
                f"{sesion['key']}: {exc}",
                file=sys.stderr,
            )
            return RC_ERROR

    mensajes = sorted(
        deduplicar_mensajes(
            mensajes
        ),
        key=lambda m: (
            m["timestamp"],
            m.get("id") or "",
        ),
    )

    mensajes_usuario = [
        mensaje
        for mensaje in mensajes
        if mensaje["role"] == "user"
    ]

    if not mensajes_usuario:
        print(
            "Sin actividad del usuario "
            f"{user_id} en {args.fecha}."
        )
        return RC_SIN_ACTIVIDAD

    mensajes_agente = [
        mensaje
        for mensaje in mensajes
        if mensaje["role"] == "assistant"
    ]

    inicio = (
        mensajes_usuario[0]["timestamp"]
        .strftime("%H:%M:%S")
    )

    fin = "-"

    if mensajes_agente:
        fin = (
            mensajes_agente[-1]["timestamp"]
            .strftime("%H:%M:%S")
        )

    tiempo_segundos = (
        calcular_tiempo_trabajo_segundos(
            mensajes
        )
    )

    tareas = extraer_tareas(
        mensajes
    )

    fila = {
        "agente_id": agente_id,
        "agente": agente,
        "usuario": nombre,
        "usuario_id": user_id,
        "fecha": fecha_objetivo.isoformat(),
        "inicio": inicio,
        "fin": fin,
        "interacciones": len(mensajes_usuario),
        "tiempo_agente": formatear_duracion(
            tiempo_segundos
        ),
        "tareas": ", ".join(tareas) or "-",
    }

    imprimir_grilla(fila)

    return RC_OK


if __name__ == "__main__":
    sys.exit(main())

