#!/usr/bin/env python3

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


TZ_NAME = "America/Argentina/Buenos_Aires"
TZ = ZoneInfo(TZ_NAME)

REDMINE_BASE_URL = "https://redmine.infomedical.com.ar"
REDMINE_CREDENTIAL_USER = "lestevarena"

USUARIOS_MD = os.path.expanduser("~/.openclaw/workspace/USUARIOS.md")
AGENTS_MD = os.path.expanduser("~/.openclaw/workspace/AGENTS.md")
REDMINE_INDEX = os.path.expanduser("~/.openclaw/secrets/redmine/index.tsv")

MYSQL_DEFAULTS_FILE = os.path.expanduser(
    "~/.openclaw/credentials/metricas-mysql.cnf"
)
MYSQL_DATABASE = "metricas"
MYSQL_TABLE = "tiempos_redmines"

PAGE_SIZE = 100
HTTP_TIMEOUT = 30

RC_OK = 0
RC_ERROR = 1
RC_SIN_ACTIVIDAD = 3


def limpiar_scalar(valor):
    valor = str(valor).strip()
    if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in ("'", '"'):
        valor = valor[1:-1]
    return valor.strip()


def normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.casefold()
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def normalizar_id_agente(valor):
    coincidencia = re.search(r"agente[\s_-]*0*(\d+)", str(valor or ""), flags=re.IGNORECASE)
    if not coincidencia:
        return None
    return f"agente_{int(coincidencia.group(1)):02d}"


def validar_fecha(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("La fecha debe tener formato YYYY-MM-DD.") from exc


def parsear_usuarios_md(ruta):
    if not os.path.isfile(ruta):
        raise RuntimeError(f"No existe el archivo de usuarios: {ruta}")

    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    agentes = []
    agente_actual = None
    usuario_actual = None
    dentro_usuarios = False

    def cerrar_usuario():
        nonlocal usuario_actual
        if agente_actual is not None and usuario_actual is not None:
            if (
                usuario_actual.get("nombre")
                and usuario_actual.get("usuario_redmine")
                and usuario_actual.get("id_googlechat")
            ):
                agente_actual["usuarios"].append(usuario_actual)
        usuario_actual = None

    def cerrar_agente():
        nonlocal agente_actual
        cerrar_usuario()
        if agente_actual is not None:
            agentes.append(agente_actual)
        agente_actual = None

    for linea in lineas:
        texto = linea.rstrip("\n")

        coincidencia_agente = re.match(
            r"^\s{2}-\s+id:\s*(agente_\d+)\s*$",
            texto,
            flags=re.IGNORECASE,
        )
        if coincidencia_agente:
            cerrar_agente()
            agente_actual = {
                "id": normalizar_id_agente(coincidencia_agente.group(1)),
                "nombre": None,
                "usuarios": [],
            }
            dentro_usuarios = False
            continue

        if agente_actual is None:
            continue

        if re.match(r"^\s{4}usuarios:\s*$", texto, flags=re.IGNORECASE):
            cerrar_usuario()
            dentro_usuarios = True
            continue

        if not dentro_usuarios:
            coincidencia_nombre_agente = re.match(r"^\s{4}nombre:\s*(.+?)\s*$", texto)
            if coincidencia_nombre_agente:
                agente_actual["nombre"] = limpiar_scalar(coincidencia_nombre_agente.group(1))
            continue

        coincidencia_usuario = re.match(r"^\s{6}-\s+nombre:\s*(.+?)\s*$", texto)
        if coincidencia_usuario:
            cerrar_usuario()
            usuario_actual = {
                "nombre": limpiar_scalar(coincidencia_usuario.group(1)),
                "usuario_redmine": None,
                "id_googlechat": None,
            }
            continue

        if usuario_actual is None:
            continue

        coincidencia_campo = re.match(
            r"^\s{8}(usuario_redmine|id_googlechat):\s*(.*?)\s*$",
            texto,
            flags=re.IGNORECASE,
        )
        if coincidencia_campo:
            campo = coincidencia_campo.group(1).lower()
            usuario_actual[campo] = limpiar_scalar(coincidencia_campo.group(2))

    cerrar_agente()

    if not agentes:
        raise RuntimeError("No se encontraron bloques de agentes en USUARIOS.md.")

    return agentes


def obtener_id_agente_desde_agents_md():
    if not os.path.isfile(AGENTS_MD):
        return None
    try:
        with open(AGENTS_MD, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
    except OSError:
        return None

    coincidencia = re.search(r"\((Agente[\s_-]*\d+)\)", contenido, flags=re.IGNORECASE)
    if not coincidencia:
        return None
    return normalizar_id_agente(coincidencia.group(1))


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
        if candidato and os.path.isfile(candidato) and os.access(candidato, os.X_OK):
            return candidato
    return None


def obtener_nombre_identidad_openclaw():
    openclaw = localizar_openclaw()
    if not openclaw:
        return None

    try:
        proc = subprocess.run(
            [
                openclaw,
                "config",
                "get",
                "agents.entries.main.identity",
                "--json",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            return None
        identidad = json.loads(proc.stdout.strip())
        if isinstance(identidad, dict):
            nombre = identidad.get("name")
            if isinstance(nombre, str) and nombre.strip():
                return nombre.strip()
    except Exception:
        return None

    return None


def detectar_agente(agentes):
    id_agente = obtener_id_agente_desde_agents_md()
    if id_agente:
        for agente in agentes:
            if agente["id"] == id_agente:
                return agente

    nombre_identidad = obtener_nombre_identidad_openclaw()
    if nombre_identidad:
        normalizado = normalizar_texto(nombre_identidad)
        for agente in agentes:
            nombre_agente = normalizar_texto(agente.get("nombre"))
            if nombre_agente and (
                normalizado == nombre_agente
                or normalizado.startswith(nombre_agente + " ")
            ):
                return agente

    raise RuntimeError(
        "No se pudo determinar el agente actual. Verifique AGENTS.md y la identidad de OpenClaw."
    )


def usuarios_del_agente(agentes, id_agente_actual):
    agente_actual = next(
        (
            agente
            for agente in agentes
            if agente["id"] == id_agente_actual
        ),
        None,
    )

    if agente_actual is None:
        raise RuntimeError(
            f"No existe el agente {id_agente_actual} en USUARIOS.md."
        )

    return list(agente_actual["usuarios"])


def resolver_credencial_redmine(usuario):
    if not os.path.isfile(REDMINE_INDEX):
        raise RuntimeError(f"No existe el registro de credenciales: {REDMINE_INDEX}")

    ruta_env = None
    with open(REDMINE_INDEX, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split(None, 1)
            if len(partes) != 2:
                continue
            login, ruta = partes
            if login.casefold() == usuario.casefold():
                ruta_env = os.path.expanduser(ruta.strip())
                break

    if not ruta_env:
        raise RuntimeError(
            f"No se encontro la credencial Redmine '{usuario}' en {REDMINE_INDEX}."
        )
    if not os.path.isfile(ruta_env):
        raise RuntimeError(f"No existe el archivo de credencial: {ruta_env}")

    variables = {}
    with open(ruta_env, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            variables[clave.strip()] = valor.strip().strip('"').strip("'")

    api_key = variables.get("REDMINE_API_KEY")
    if not api_key:
        raise RuntimeError(
            f"La credencial '{usuario}' no contiene REDMINE_API_KEY."
        )

    return api_key


def redmine_get(ruta, api_key, params=None):
    url = REDMINE_BASE_URL.rstrip("/") + "/" + ruta.lstrip("/")
    if params:
        url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"

    request = urllib.request.Request(
        url,
        headers={
            "X-Redmine-API-Key": api_key,
            "Accept": "application/json",
            "User-Agent": "genera_tiempos_redmines/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Redmine respondio HTTP {exc.code} al consultar {ruta}."
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"No se pudo conectar con Redmine: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError("Timeout al consultar Redmine.") from exc


def parsear_created_on(valor):
    if not isinstance(valor, str) or not valor.strip():
        raise RuntimeError("Redmine devolvio un time entry sin created_on.")

    texto = valor.strip()
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"

    try:
        fecha_hora = datetime.fromisoformat(texto)
    except ValueError as exc:
        raise RuntimeError(f"created_on invalido: {valor}") from exc

    if fecha_hora.tzinfo is None:
        fecha_hora = fecha_hora.replace(tzinfo=timezone.utc)

    return fecha_hora.astimezone(TZ)


def obtener_time_entries_fecha(api_key, fecha_objetivo):
    encontrados = []
    vistos = set()
    offset = 0
    ultimo_created_on = None

    while True:
        payload = redmine_get(
            "/time_entries.json",
            api_key,
            params={
                "limit": PAGE_SIZE,
                "offset": offset,
                "sort": "created_on:desc",
            },
        )

        entradas = payload.get("time_entries") or []
        if not entradas:
            break

        fechas_creacion = []
        for entrada in entradas:
            fecha_creacion = parsear_created_on(
                entrada.get("created_on")
            )
            fechas_creacion.append(fecha_creacion)

        if fechas_creacion != sorted(
            fechas_creacion,
            reverse=True,
        ):
            raise RuntimeError(
                "Redmine no devolvio los time entries ordenados por "
                "created_on descendente. Se detiene para evitar "
                "resultados incompletos."
            )

        if (
            ultimo_created_on is not None
            and fechas_creacion[0] > ultimo_created_on
        ):
            raise RuntimeError(
                "La paginacion de Redmine no mantuvo el orden "
                "descendente por created_on."
            )

        ultimo_created_on = fechas_creacion[-1]

        for entrada, fecha_creacion in zip(
            entradas,
            fechas_creacion,
        ):
            fecha_local = fecha_creacion.date()

            if fecha_local != fecha_objetivo:
                continue

            try:
                entry_id = int(entrada["id"])
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError(
                    "Redmine devolvio un time entry sin ID numerico."
                ) from exc

            if entry_id in vistos:
                continue

            vistos.add(entry_id)
            copia = dict(entrada)
            copia["_created_local"] = fecha_creacion
            encontrados.append(copia)

        # En esta instalacion validamos que Redmine respeta
        # sort=created_on:desc. Cuando el registro mas antiguo de la
        # pagina ya es anterior a la fecha buscada, las paginas siguientes
        # tambien seran anteriores y podemos detener la paginacion.
        if fechas_creacion[-1].date() < fecha_objetivo:
            break

        total_count = payload.get("total_count")
        offset += len(entradas)

        if isinstance(total_count, int) and offset >= total_count:
            break
        if len(entradas) < PAGE_SIZE:
            break

    return encontrados


def obtener_issue(issue_id, api_key, cache):
    if issue_id is None:
        return {"id": None, "subject": "-"}

    try:
        issue_id = int(issue_id)
    except (TypeError, ValueError):
        return {"id": None, "subject": "-"}

    if issue_id in cache:
        return cache[issue_id]

    payload = redmine_get(f"/issues/{issue_id}.json", api_key)
    issue = payload.get("issue")

    if not isinstance(issue, dict):
        raise RuntimeError(f"Redmine no devolvio datos del issue {issue_id}.")

    resultado = {
        "id": issue.get("id"),
        "subject": issue.get("subject") or "-",
    }
    cache[issue_id] = resultado
    return resultado


def formatear_horas(valor):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "-"

    texto = f"{numero:.2f}".rstrip("0").rstrip(".")
    return f"{texto} h"


def construir_filas(entradas, usuarios, agente, api_key, fecha_objetivo):
    usuarios_por_nombre = {}
    for usuario in usuarios:
        clave = normalizar_texto(usuario["nombre"])
        usuarios_por_nombre.setdefault(clave, usuario)

    cache_issues = {}
    filas = []

    for entrada in entradas:
        info_usuario = entrada.get("user") or {}
        nombre_redmine = info_usuario.get("name") or ""
        usuario = usuarios_por_nombre.get(normalizar_texto(nombre_redmine))

        if usuario is None:
            continue

        issue_ref = entrada.get("issue") or {}
        issue = obtener_issue(issue_ref.get("id"), api_key, cache_issues)

        spent_on = str(entrada.get("spent_on") or "").strip() or "-"
        demorado = "Si" if spent_on != fecha_objetivo.isoformat() else "No"
        proyecto = entrada.get("project") or {}

        filas.append(
            {
                "_time_entry_id": int(entrada["id"]),
                "_created_local": entrada["_created_local"],
                "id_agente": agente["id"],
                "agente": agente.get("nombre") or "-",
                "usuario": usuario["nombre"],
                "usuario_redmine": usuario["usuario_redmine"],
                "id_googlechat": usuario["id_googlechat"],
                "fecha_carga": fecha_objetivo.isoformat(),
                "fecha_imputacion": spent_on,
                "redmine": str(issue.get("id")) if issue.get("id") is not None else "-",
                "nombre_redmine": issue.get("subject") or "-",
                "proyecto": proyecto.get("name") or "-",
                "tiempo": formatear_horas(entrada.get("hours")),
                "tiempo_horas": float(entrada.get("hours") or 0),
                "comentario": entrada.get("comments") or "-",
                "demorado": demorado,
            }
        )

    filas.sort(
        key=lambda fila: (
            normalizar_texto(fila["usuario"]),
            fila["_created_local"],
            fila["_time_entry_id"],
        )
    )
    return filas


def recortar(valor, ancho_maximo):
    texto = str("" if valor is None else valor)
    texto = texto.replace("\r", " ").replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto).strip()

    if len(texto) <= ancho_maximo:
        return texto
    if ancho_maximo <= 3:
        return texto[:ancho_maximo]
    return texto[:ancho_maximo - 3] + "..."


def imprimir_grilla(filas):
    columnas = [
        ("ID agente", "id_agente", 10),
        ("Agente", "agente", 18),
        ("Usuario", "usuario", 28),
        ("Usuario Redmine", "usuario_redmine", 18),
        ("ID Google Chat", "id_googlechat", 30),
        ("Fecha carga", "fecha_carga", 11),
        ("Fecha imputacion", "fecha_imputacion", 16),
        ("Redmine", "redmine", 9),
        ("Nombre Redmine", "nombre_redmine", 40),
        ("Proyecto", "proyecto", 28),
        ("Tiempo", "tiempo", 9),
        ("Comentario", "comentario", 50),
        ("Demorado", "demorado", 8),
    ]

    filas_visibles = []
    for fila in filas:
        visible = {}
        for _, clave, ancho_maximo in columnas:
            visible[clave] = recortar(fila.get(clave, ""), ancho_maximo)
        filas_visibles.append(visible)

    anchos = []
    for titulo, clave, ancho_maximo in columnas:
        ancho = len(titulo)
        for fila in filas_visibles:
            ancho = max(ancho, len(fila.get(clave, "")))
        anchos.append(min(ancho, ancho_maximo))

    separador = "+-" + "-+-".join("-" * ancho for ancho in anchos) + "-+"
    cabecera = "| " + " | ".join(
        titulo.ljust(ancho)
        for (titulo, _, _), ancho in zip(columnas, anchos)
    ) + " |"

    print(separador)
    print(cabecera)
    print(separador)

    for fila in filas_visibles:
        valores = "| " + " | ".join(
            fila.get(clave, "").ljust(ancho)
            for (_, clave, _), ancho in zip(columnas, anchos)
        ) + " |"
        print(valores)

    print(separador)



def localizar_mysql():
    candidatos = [
        shutil.which("mysql"),
        "/usr/bin/mysql",
        "/usr/local/bin/mysql",
    ]

    for candidato in candidatos:
        if (
            candidato
            and os.path.isfile(candidato)
            and os.access(candidato, os.X_OK)
        ):
            return candidato

    raise RuntimeError(
        "No se encontro el cliente 'mysql'."
    )


def sql_texto(valor):
    if valor is None:
        return "NULL"

    texto = str(valor)
    hexadecimal = texto.encode("utf-8").hex()

    return (
        "CONVERT(X'"
        + hexadecimal
        + "' USING utf8mb4)"
    )


def ejecutar_mysql(sql, devolver_salida=False):
    if not os.path.isfile(MYSQL_DEFAULTS_FILE):
        raise RuntimeError(
            "No existe el archivo de credenciales MySQL: "
            f"{MYSQL_DEFAULTS_FILE}"
        )

    mysql = localizar_mysql()

    cmd = [
        mysql,
        f"--defaults-extra-file={MYSQL_DEFAULTS_FILE}",
        "--batch",
        "--skip-column-names",
        MYSQL_DATABASE,
    ]

    proc = subprocess.run(
        cmd,
        input=sql,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=60,
        check=False,
    )

    if proc.returncode != 0:
        detalle = (
            proc.stderr
            or proc.stdout
            or "sin detalle"
        ).strip()

        raise RuntimeError(
            "Fallo la escritura en MySQL: "
            f"{detalle}"
        )

    if devolver_salida:
        return proc.stdout

    return ""


def obtener_registros_existentes_mysql(filas):
    if not filas:
        return {}

    ids = sorted(
        {
            int(fila["_time_entry_id"])
            for fila in filas
        }
    )

    consulta = (
        "SELECT time_entry_id, id_agente "
        f"FROM {MYSQL_TABLE} "
        "WHERE time_entry_id IN ("
        + ",".join(str(valor) for valor in ids)
        + ");"
    )

    salida = ejecutar_mysql(
        consulta,
        devolver_salida=True,
    )

    existentes = {}

    for linea in salida.splitlines():
        partes = linea.split("\t")

        if len(partes) != 2:
            continue

        try:
            time_entry_id = int(partes[0])
        except ValueError:
            continue

        existentes[time_entry_id] = partes[1]

    return existentes


def guardar_filas_mysql(filas, id_agente_actual):
    existentes = obtener_registros_existentes_mysql(
        filas
    )

    sentencias = ["START TRANSACTION;"]

    insertados = 0
    actualizados = 0
    omitidos_otro_agente = 0

    for fila in filas:
        time_entry_id = int(
            fila["_time_entry_id"]
        )

        propietario = existentes.get(
            time_entry_id
        )

        if (
            propietario is not None
            and propietario != id_agente_actual
        ):
            omitidos_otro_agente += 1
            continue

        redmine = fila.get("redmine")

        if redmine in (None, "", "-"):
            redmine_sql = "NULL"
        else:
            redmine_sql = str(int(redmine))

        tiempo_horas = float(
            fila.get("tiempo_horas") or 0
        )

        valores = {
            "id_agente": sql_texto(fila["id_agente"]),
            "agente": sql_texto(fila["agente"]),
            "usuario": sql_texto(fila["usuario"]),
            "usuario_redmine": sql_texto(fila["usuario_redmine"]),
            "id_googlechat": sql_texto(fila["id_googlechat"]),
            "fecha_carga": sql_texto(fila["fecha_carga"]),
            "fecha_imputacion": sql_texto(fila["fecha_imputacion"]),
            "redmine": redmine_sql,
            "nombre_redmine": sql_texto(fila.get("nombre_redmine")),
            "proyecto": sql_texto(fila.get("proyecto")),
            "tiempo_horas": f"{tiempo_horas:.2f}",
            "comentario": sql_texto(fila.get("comentario")),
            "demorado": sql_texto(fila["demorado"]),
        }

        if propietario is None:
            sentencias.append(
                f"""
INSERT INTO {MYSQL_TABLE} (
    time_entry_id,
    id_agente,
    agente,
    usuario,
    usuario_redmine,
    id_googlechat,
    fecha_carga,
    fecha_imputacion,
    redmine,
    nombre_redmine,
    proyecto,
    tiempo_horas,
    comentario,
    demorado
) VALUES (
    {time_entry_id},
    {valores['id_agente']},
    {valores['agente']},
    {valores['usuario']},
    {valores['usuario_redmine']},
    {valores['id_googlechat']},
    {valores['fecha_carga']},
    {valores['fecha_imputacion']},
    {valores['redmine']},
    {valores['nombre_redmine']},
    {valores['proyecto']},
    {valores['tiempo_horas']},
    {valores['comentario']},
    {valores['demorado']}
);
"""
            )
            insertados += 1
            continue

        sentencias.append(
            f"""
UPDATE {MYSQL_TABLE}
SET
    agente = {valores['agente']},
    usuario = {valores['usuario']},
    usuario_redmine = {valores['usuario_redmine']},
    id_googlechat = {valores['id_googlechat']},
    fecha_carga = {valores['fecha_carga']},
    fecha_imputacion = {valores['fecha_imputacion']},
    redmine = {valores['redmine']},
    nombre_redmine = {valores['nombre_redmine']},
    proyecto = {valores['proyecto']},
    tiempo_horas = {valores['tiempo_horas']},
    comentario = {valores['comentario']},
    demorado = {valores['demorado']}
WHERE
    time_entry_id = {time_entry_id}
    AND id_agente = {valores['id_agente']};
"""
        )
        actualizados += 1

    sentencias.append("COMMIT;")

    if insertados or actualizados:
        ejecutar_mysql("\n".join(sentencias))

    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "omitidos_otro_agente": omitidos_otro_agente,
    }

def main():
    parser = argparse.ArgumentParser(
        description="Guarda en MySQL los tiempos Redmine cargados en una fecha."
    )
    parser.add_argument(
        "fecha",
        help="Fecha de carga a procesar en formato YYYY-MM-DD.",
    )
    args = parser.parse_args()

    try:
        fecha_objetivo = validar_fecha(args.fecha)
        agentes = parsear_usuarios_md(USUARIOS_MD)
        agente = detectar_agente(agentes)
        usuarios = usuarios_del_agente(agentes, agente["id"])
        api_key = resolver_credencial_redmine(REDMINE_CREDENTIAL_USER)
        entradas = obtener_time_entries_fecha(api_key, fecha_objetivo)
        filas = construir_filas(
            entradas,
            usuarios,
            agente,
            api_key,
            fecha_objetivo,
        )
    except Exception as exc:
        print(f"ERROR | {exc}", file=sys.stderr)
        return RC_ERROR

    print(f"Fecha de carga procesada: {fecha_objetivo.isoformat()}")
    print(f"Agente: {agente['id']} ({agente.get('nombre') or '-'})")
    print(f"Usuarios del agente: {len(usuarios)}")
    print()

    if not filas:
        print(
            "Sin tiempos Redmine cargados para los usuarios de este agente "
            "en la fecha indicada."
        )
        return RC_SIN_ACTIVIDAD

    try:
        resultado_db = guardar_filas_mysql(
            filas,
            agente["id"],
        )
    except Exception as exc:
        print(
            f"ERROR | {exc}",
            file=sys.stderr,
        )
        return RC_ERROR

    print(f"Tiempos encontrados: {len(filas)}")
    print(
        "Insertados: "
        f"{resultado_db['insertados']}"
    )
    print(
        "Actualizados: "
        f"{resultado_db['actualizados']}"
    )
    print(
        "Omitidos por pertenecer a otro agente: "
        f"{resultado_db['omitidos_otro_agente']}"
    )
    return RC_OK


if __name__ == "__main__":
    sys.exit(main())

