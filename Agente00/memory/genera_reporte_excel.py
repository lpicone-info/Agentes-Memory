#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue


MYSQL_CONFIG = (
    Path.home()
    / ".openclaw"
    / "credentials"
    / "metricas-mysql.cnf"
)

MYSQL_DATABASE = "metricas"

HOST_PERMITIDO = "desarrollo-ia-00"


CLASIFICACION_AGENTES = [
    {
        "id_agente": "Agente08",
        "agente": "Mafalda",
        "categoria": "Proyecto Est\u00e1ndar",
        "equipo": "Atenci\u00f3n al cliente",
        "usuarios_habilitados": 5,
    },
    {
        "id_agente": "Agente07",
        "agente": "Bender",
        "categoria": "Proyecto Est\u00e1ndar",
        "equipo": "An\u00e1lisis y dise\u00f1o",
        "usuarios_habilitados": 7,
    },
    {
        "id_agente": "Agente03",
        "agente": "Stan",
        "categoria": "Proyecto Est\u00e1ndar",
        "equipo": "Desarrollo",
        "usuarios_habilitados": 6,
    },
    {
        "id_agente": "Agente04",
        "agente": "La 99",
        "categoria": "Proyecto Especial",
        "equipo": "Swiss Medical",
        "usuarios_habilitados": 7,
    },
    {
        "id_agente": "Agente05",
        "agente": "Lisa",
        "categoria": "Proyecto Especial",
        "equipo": "Coomeva Presmed",
        "usuarios_habilitados": 6,
    },
    {
        "id_agente": "Agente01",
        "agente": "Maxxuel",
        "categoria": "Proyecto Especial",
        "equipo": "Coomeva Afilmed",
        "usuarios_habilitados": 4,
    },
    {
        "id_agente": "Agente06",
        "agente": "Homero",
        "categoria": "Proyecto Especial",
        "equipo": "Prevenci\u00f3n-Brit\u00e1nico",
        "usuarios_habilitados": 6,
    },
    {
        "id_agente": "Agente02",
        "agente": "Camaron",
        "categoria": "Proyecto Est\u00e1ndar",
        "equipo": "Desarrollo web",
        "usuarios_habilitados": 2,
    },
]

CLASIFICACION_POR_ID = {
    item["id_agente"].casefold(): item
    for item in CLASIFICACION_AGENTES
}


def validar_agente():
    hostname = socket.gethostname().split(".")[0]

    if hostname != HOST_PERMITIDO:
        raise RuntimeError(
            f"Este programa solo puede ejecutarse en {HOST_PERMITIDO}. "
            f"Host actual: {hostname}"
        )


def validar_fecha(valor):
    try:
        return datetime.strptime(
            valor,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        raise ValueError(
            f"Fecha invalida: {valor}. "
            "Debe tener formato YYYY-MM-DD."
        )


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
        "No se encontro el cliente mysql."
    )


def ejecutar_consulta_json(sql):
    if not MYSQL_CONFIG.is_file():
        raise RuntimeError(
            "No existe la configuracion MySQL: "
            f"{MYSQL_CONFIG}"
        )

    mysql = localizar_mysql()

    proc = subprocess.run(
        [
            mysql,
            (
                "--defaults-extra-file="
                f"{MYSQL_CONFIG}"
            ),
            f"--database={MYSQL_DATABASE}",
            "--batch",
            "--raw",
            "--skip-column-names",
            "-e",
            sql,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=120,
        check=False,
    )

    if proc.returncode != 0:
        detalle = (
            proc.stderr
            or proc.stdout
            or "sin detalle"
        ).strip()

        raise RuntimeError(
            f"Error consultando MySQL: {detalle}"
        )

    filas = []

    for linea in proc.stdout.splitlines():
        linea = linea.strip()

        if not linea:
            continue

        try:
            filas.append(
                json.loads(linea)
            )

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "No se pudo interpretar una fila "
                "devuelta por MySQL: "
                f"{exc}"
            ) from exc

    return filas


def obtener_interacciones(
    fecha_desde,
    fecha_hasta,
):
    sql = f"""
SELECT JSON_OBJECT(
    'id_agente', id_agente,
    'agente', agente,
    'usuario', usuario,
    'id_usuario', id_usuario,
    'fecha',
        DATE_FORMAT(fecha, '%Y-%m-%d'),
    'hora_inicio',
        TIME_FORMAT(
            hora_inicio,
            '%H:%i:%s'
        ),
    'hora_fin',
        IF(
            hora_fin IS NULL,
            NULL,
            TIME_FORMAT(
                hora_fin,
                '%H:%i:%s'
            )
        ),
    'cantidad_interacciones',
        cantidad_interacciones,
    'tiempo_agente',
        SEC_TO_TIME(
            tiempo_agente_segundos
        ),
    'tiempo_agente_segundos',
        tiempo_agente_segundos,
    'tareas',
        tareas
)
FROM interacciones_usuarios
WHERE fecha BETWEEN
      '{fecha_desde}'
      AND '{fecha_hasta}'
  AND id_usuario NOT IN (
      'users/103530042020124588192',
      'users/104589903420005473781',
      'users/101490756487558923795'
  )
ORDER BY
    fecha,
    id_agente,
    usuario;
"""

    return ejecutar_consulta_json(
        sql
    )


def obtener_tiempos_redmine(
    fecha_desde,
    fecha_hasta,
):
    sql = f"""
SELECT JSON_OBJECT(
    'id_agente', id_agente,
    'agente', agente,
    'usuario', usuario,
    'usuario_redmine',
        usuario_redmine,
    'fecha_carga',
        DATE_FORMAT(
            fecha_carga,
            '%Y-%m-%d'
        ),
    'fecha_imputacion',
        DATE_FORMAT(
            fecha_imputacion,
            '%Y-%m-%d'
        ),
    'redmine',
        redmine,
    'nombre_redmine',
        nombre_redmine,
    'proyecto',
        proyecto,
    'tiempo_horas',
        tiempo_horas,
    'comentario',
        comentario,
    'demorado',
        demorado
)
FROM tiempos_redmines
WHERE fecha_imputacion BETWEEN
      '{fecha_desde}'
      AND '{fecha_hasta}'
  AND id_googlechat NOT IN (
      'users/103530042020124588192',
      'users/104589903420005473781',
      'users/101490756487558923795'
  )
ORDER BY
    fecha_imputacion,
    id_agente,
    usuario,
    redmine;
"""

    return ejecutar_consulta_json(
        sql
    )



def obtener_clasificacion(id_agente):
    clave = str(id_agente or "").strip().casefold()
    clasificacion = CLASIFICACION_POR_ID.get(clave)

    if clasificacion is None:
        raise RuntimeError(
            "No existe clasificacion configurada para "
            f"el agente: {id_agente or 'SIN ID'}"
        )

    return clasificacion


def entero_seguro(valor):
    if valor is None or valor == "":
        return 0

    return int(valor)


def clave_primera_interaccion(fila):
    return (
        fila.get("fecha") or "9999-12-31",
        fila.get("hora_inicio") or "23:59:59",
        str(fila.get("id_agente") or "").casefold(),
    )


def calcular_porcentajes_100(valores):
    valores = [max(0, int(valor)) for valor in valores]
    total = sum(valores)

    if total == 0:
        return [0.0 for _ in valores]

    bases = []
    restos = []

    for indice, valor in enumerate(valores):
        base, resto = divmod(valor * 10000, total)
        bases.append(base)
        restos.append((resto, indice))

    faltantes = 10000 - sum(bases)

    for _, indice in sorted(
        restos,
        key=lambda item: (item[0], -item[1]),
        reverse=True,
    )[:faltantes]:
        bases[indice] += 1

    return [base / 10000.0 for base in bases]



def construir_interaccion_agente_por_equipo(interacciones):
    acumulados = {}

    for config in CLASIFICACION_AGENTES:
        acumulados[config["id_agente"].casefold()] = {
            "peticion": 0,
            "segundos": 0,
            "usuarios": set(),
        }

    for fila in interacciones:
        config = obtener_clasificacion(
            fila.get("id_agente")
        )
        clave = config["id_agente"].casefold()
        cantidad = entero_seguro(
            fila.get("cantidad_interacciones")
        )
        segundos = entero_seguro(
            fila.get("tiempo_agente_segundos")
        )

        acumulados[clave]["peticion"] += cantidad
        acumulados[clave]["segundos"] += segundos

        user_id = fila.get("id_usuario")
        if cantidad > 0 and user_id:
            acumulados[clave]["usuarios"].add(
                str(user_id)
            )

    peticiones = [
        acumulados[config["id_agente"].casefold()]["peticion"]
        for config in CLASIFICACION_AGENTES
    ]
    segundos_agentes = [
        acumulados[config["id_agente"].casefold()]["segundos"]
        for config in CLASIFICACION_AGENTES
    ]
    porcentajes_peticion = calcular_porcentajes_100(
        peticiones
    )
    porcentajes_horas = calcular_porcentajes_100(
        segundos_agentes
    )

    filas = []

    for indice, config in enumerate(CLASIFICACION_AGENTES):
        datos = acumulados[
            config["id_agente"].casefold()
        ]

        filas.append(
            {
                "agente": config["agente"],
                "categoria": config["categoria"],
                "equipo": config["equipo"],
                "peticion": datos["peticion"],
                "porcentaje_peticion": (
                    porcentajes_peticion[indice]
                ),
                "horas_agente": (
                    datos["segundos"] / 3600.0
                ),
                "porcentaje_horas": (
                    porcentajes_horas[indice]
                ),
                "usuarios_habilitados": (
                    config["usuarios_habilitados"]
                ),
                "usuarios_participantes": len(
                    datos["usuarios"]
                ),
            }
        )

    return filas

def construir_interaccion_usuario_por_equipo(interacciones):
    acumulados = {}

    for fila in interacciones:
        user_id = fila.get("id_usuario")

        if not user_id:
            continue

        config = obtener_clasificacion(
            fila.get("id_agente")
        )
        clave_usuario = str(user_id)
        clave_interaccion = clave_primera_interaccion(
            fila
        )

        if clave_usuario not in acumulados:
            acumulados[clave_usuario] = {
                "usuario": fila.get("usuario") or clave_usuario,
                "peticion": 0,
                "segundos": 0,
                "primera_clave": clave_interaccion,
                "categoria": config["categoria"],
                "equipo": config["equipo"],
            }

        datos = acumulados[clave_usuario]
        datos["peticion"] += entero_seguro(
            fila.get("cantidad_interacciones")
        )
        datos["segundos"] += entero_seguro(
            fila.get("tiempo_agente_segundos")
        )

        if clave_interaccion < datos["primera_clave"]:
            datos["primera_clave"] = clave_interaccion
            datos["categoria"] = config["categoria"]
            datos["equipo"] = config["equipo"]
            datos["usuario"] = (
                fila.get("usuario") or clave_usuario
            )

    datos_ordenados = sorted(
        acumulados.values(),
        key=lambda datos: (
            str(datos["usuario"]).casefold(),
            datos["equipo"].casefold(),
        ),
    )

    porcentajes_peticion = calcular_porcentajes_100(
        [datos["peticion"] for datos in datos_ordenados]
    )
    porcentajes_horas = calcular_porcentajes_100(
        [datos["segundos"] for datos in datos_ordenados]
    )

    filas = []

    for indice, datos in enumerate(datos_ordenados):
        filas.append(
            {
                "usuario": datos["usuario"],
                "categoria": datos["categoria"],
                "equipo": datos["equipo"],
                "peticion": datos["peticion"],
                "porcentaje_peticion": (
                    porcentajes_peticion[indice]
                ),
                "horas_agente": (
                    datos["segundos"] / 3600.0
                ),
                "porcentaje_horas": (
                    porcentajes_horas[indice]
                ),
            }
        )

    return filas

def propiedad(
    nombre,
    valor,
):
    prop = PropertyValue()
    prop.Name = nombre
    prop.Value = valor

    return prop


def iniciar_libreoffice():
    ejecutable = (
        shutil.which("libreoffice")
        or shutil.which("soffice")
    )

    if not ejecutable:
        raise RuntimeError(
            "No se encontro LibreOffice."
        )

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    sock.bind(
        (
            "127.0.0.1",
            0,
        )
    )

    puerto = sock.getsockname()[1]

    sock.close()

    perfil = tempfile.mkdtemp(
        prefix="reporte_excel_lo_"
    )

    perfil_url = (
        uno.systemPathToFileUrl(
            perfil
        )
    )

    proc = subprocess.Popen(
        [
            ejecutable,
            "--headless",
            "--nologo",
            "--nodefault",
            "--nofirststartwizard",
            (
                "-env:UserInstallation="
                f"{perfil_url}"
            ),
            (
                "--accept="
                "socket,"
                "host=127.0.0.1,"
                f"port={puerto};"
                "urp;"
                "StarOffice.ServiceManager"
            ),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    contexto_local = (
        uno.getComponentContext()
    )

    resolver = (
        contexto_local
        .ServiceManager
        .createInstanceWithContext(
            (
                "com.sun.star.bridge."
                "UnoUrlResolver"
            ),
            contexto_local,
        )
    )

    contexto = None

    for _ in range(50):
        try:
            contexto = resolver.resolve(
                (
                    "uno:"
                    "socket,"
                    "host=127.0.0.1,"
                    f"port={puerto};"
                    "urp;"
                    "StarOffice."
                    "ComponentContext"
                )
            )

            break

        except Exception:
            time.sleep(0.2)

    if contexto is None:
        proc.terminate()

        shutil.rmtree(
            perfil,
            ignore_errors=True,
        )

        raise RuntimeError(
            "No se pudo conectar "
            "con LibreOffice."
        )

    return (
        contexto,
        proc,
        perfil,
    )


def escribir_tabla(
    hoja,
    encabezados,
    claves,
    filas,
    anchos,
):
    for columna, encabezado in enumerate(
        encabezados
    ):
        celda = (
            hoja.getCellByPosition(
                columna,
                0,
            )
        )

        celda.setString(
            encabezado
        )

    ultima_columna = (
        len(encabezados) - 1
    )

    rango_encabezado = (
        hoja.getCellRangeByPosition(
            0,
            0,
            ultima_columna,
            0,
        )
    )

    rango_encabezado.CharWeight = 150
    rango_encabezado.CharColor = 0xFFFFFF
    rango_encabezado.CellBackColor = 0x1F4E78

    for numero_fila, fila in enumerate(
        filas,
        start=1,
    ):
        for (
            numero_columna,
            clave,
        ) in enumerate(claves):

            valor = fila.get(
                clave
            )

            celda = (
                hoja.getCellByPosition(
                    numero_columna,
                    numero_fila,
                )
            )

            if valor is None:
                celda.setString("")

            elif isinstance(
                valor,
                (int, float),
            ):
                celda.setValue(
                    float(valor)
                )

            else:
                celda.setString(
                    str(valor)
                )

    for indice, ancho in enumerate(
        anchos
    ):
        columna = (
            hoja.getColumns()
            .getByIndex(indice)
        )

        columna.Width = ancho

    if filas:
        rango = (
            hoja.getCellRangeByPosition(
                0,
                0,
                ultima_columna,
                len(filas),
            )
        )

        rango.IsTextWrapped = True


def activar_autofiltro(
    documento,
    hoja,
    nombre,
    cantidad_columnas,
    cantidad_filas,
):
    try:
        rangos = (
            documento
            .getDatabaseRanges()
        )

        direccion = (
            hoja
            .getCellRangeByPosition(
                0,
                0,
                cantidad_columnas - 1,
                cantidad_filas,
            )
            .getRangeAddress()
        )

        rangos.addNewByName(
            nombre,
            direccion,
        )

        rango_db = (
            rangos.getByName(
                nombre
            )
        )

        rango_db.AutoFilter = True

    except Exception:
        pass



def aplicar_formato_numerico(
    documento,
    hoja,
    columna,
    cantidad_filas,
    formato,
):
    if cantidad_filas <= 0:
        return

    try:
        locale = uno.createUnoStruct(
            "com.sun.star.lang.Locale"
        )
        formatos = documento.getNumberFormats()
        clave = formatos.queryKey(
            formato,
            locale,
            True,
        )

        if clave == -1:
            clave = formatos.addNew(
                formato,
                locale,
            )

        rango = hoja.getCellRangeByPosition(
            columna,
            1,
            columna,
            cantidad_filas,
        )
        rango.NumberFormat = clave

    except Exception:
        pass

def congelar_primera_fila(
    documento,
    hoja,
):
    try:
        controlador = (
            documento
            .getCurrentController()
        )

        controlador.setActiveSheet(
            hoja
        )

        controlador.freezeAtPosition(
            0,
            1,
        )

    except Exception:
        pass


def generar_excel(
    salida,
    interacciones,
    tiempos_redmine,
    interaccion_agente_equipo,
    interaccion_usuario_equipo,
):
    (
        contexto,
        proc,
        perfil,
    ) = iniciar_libreoffice()

    documento = None

    try:
        gestor = (
            contexto.ServiceManager
        )

        escritorio = (
            gestor
            .createInstanceWithContext(
                (
                    "com.sun.star.frame."
                    "Desktop"
                ),
                contexto,
            )
        )

        documento = (
            escritorio
            .loadComponentFromURL(
                "private:factory/scalc",
                "_blank",
                0,
                (
                    propiedad(
                        "Hidden",
                        True,
                    ),
                ),
            )
        )

        hojas = (
            documento.getSheets()
        )

        hoja_interacciones = (
            hojas.getByIndex(0)
        )

        hoja_interacciones.setName(
            "Interacciones usuarios"
        )

        hojas.insertNewByName(
            "Tiempos Redmine",
            1,
        )

        hoja_redmine = (
            hojas.getByName(
                "Tiempos Redmine"
            )
        )

        hojas.insertNewByName(
            "Interaccion agente por equipo",
            2,
        )

        hoja_agente_equipo = (
            hojas.getByName(
                "Interaccion agente por equipo"
            )
        )

        hojas.insertNewByName(
            "Interaccion usuario por equipo",
            3,
        )

        hoja_usuario_equipo = (
            hojas.getByName(
                "Interaccion usuario por equipo"
            )
        )

        encabezados_interacciones = [
            "ID agente",
            "Agente",
            "Usuario",
            "Fecha",
            "Hora inicio",
            "Hora fin",
            "Cantidad interacciones",
            "Tiempo agente",
            "Tareas",
        ]

        claves_interacciones = [
            "id_agente",
            "agente",
            "usuario",
            "fecha",
            "hora_inicio",
            "hora_fin",
            "cantidad_interacciones",
            "tiempo_agente",
            "tareas",
        ]

        anchos_interacciones = [
            2500,
            3500,
            4500,
            2600,
            2600,
            2600,
            4200,
            3200,
            9000,
        ]

        escribir_tabla(
            hoja_interacciones,
            encabezados_interacciones,
            claves_interacciones,
            interacciones,
            anchos_interacciones,
        )

        activar_autofiltro(
            documento,
            hoja_interacciones,
            "FiltroInteracciones",
            len(
                encabezados_interacciones
            ),
            len(interacciones),
        )

        congelar_primera_fila(
            documento,
            hoja_interacciones,
        )

        encabezados_redmine = [
            "ID agente",
            "Agente",
            "Usuario",
            "Usuario Redmine",
            "Fecha carga",
            "Fecha imputacion",
            "Redmine",
            "Nombre Redmine",
            "Proyecto",
            "Tiempo horas",
            "Comentario",
            "Demorado",
        ]

        claves_redmine = [
            "id_agente",
            "agente",
            "usuario",
            "usuario_redmine",
            "fecha_carga",
            "fecha_imputacion",
            "redmine",
            "nombre_redmine",
            "proyecto",
            "tiempo_horas",
            "comentario",
            "demorado",
        ]

        anchos_redmine = [
            2500,
            3500,
            4500,
            3500,
            2800,
            3200,
            2500,
            6000,
            6000,
            3000,
            10000,
            2500,
        ]

        escribir_tabla(
            hoja_redmine,
            encabezados_redmine,
            claves_redmine,
            tiempos_redmine,
            anchos_redmine,
        )

        activar_autofiltro(
            documento,
            hoja_redmine,
            "FiltroRedmine",
            len(
                encabezados_redmine
            ),
            len(tiempos_redmine),
        )

        congelar_primera_fila(
            documento,
            hoja_redmine,
        )

        encabezados_agente_equipo = [
            "Agente",
            "Categor\u00eda",
            "Equipo",
            "Petici\u00f3n",
            "% Petici\u00f3n",
            "Horas agente",
            "% Horas",
            "Usuarios habilitados",
            "Usuarios participantes",
        ]

        claves_agente_equipo = [
            "agente",
            "categoria",
            "equipo",
            "peticion",
            "porcentaje_peticion",
            "horas_agente",
            "porcentaje_horas",
            "usuarios_habilitados",
            "usuarios_participantes",
        ]

        anchos_agente_equipo = [
            3500,
            4200,
            5000,
            2600,
            3000,
            3200,
            2600,
            4300,
            4800,
        ]

        escribir_tabla(
            hoja_agente_equipo,
            encabezados_agente_equipo,
            claves_agente_equipo,
            interaccion_agente_equipo,
            anchos_agente_equipo,
        )

        activar_autofiltro(
            documento,
            hoja_agente_equipo,
            "FiltroAgenteEquipo",
            len(encabezados_agente_equipo),
            len(interaccion_agente_equipo),
        )

        congelar_primera_fila(
            documento,
            hoja_agente_equipo,
        )

        aplicar_formato_numerico(
            documento,
            hoja_agente_equipo,
            3,
            len(interaccion_agente_equipo),
            "0",
        )
        aplicar_formato_numerico(
            documento,
            hoja_agente_equipo,
            4,
            len(interaccion_agente_equipo),
            "0.00%",
        )
        aplicar_formato_numerico(
            documento,
            hoja_agente_equipo,
            5,
            len(interaccion_agente_equipo),
            "0.00",
        )
        aplicar_formato_numerico(
            documento,
            hoja_agente_equipo,
            6,
            len(interaccion_agente_equipo),
            "0.00%",
        )
        aplicar_formato_numerico(
            documento,
            hoja_agente_equipo,
            7,
            len(interaccion_agente_equipo),
            "0",
        )
        aplicar_formato_numerico(
            documento,
            hoja_agente_equipo,
            8,
            len(interaccion_agente_equipo),
            "0",
        )

        encabezados_usuario_equipo = [
            "Usuario",
            "Categor\u00eda",
            "Equipo",
            "Petici\u00f3n",
            "% Petici\u00f3n",
            "Horas agente",
            "% Horas",
        ]

        claves_usuario_equipo = [
            "usuario",
            "categoria",
            "equipo",
            "peticion",
            "porcentaje_peticion",
            "horas_agente",
            "porcentaje_horas",
        ]

        anchos_usuario_equipo = [
            5000,
            4200,
            5000,
            2600,
            3000,
            3200,
            2600,
        ]

        escribir_tabla(
            hoja_usuario_equipo,
            encabezados_usuario_equipo,
            claves_usuario_equipo,
            interaccion_usuario_equipo,
            anchos_usuario_equipo,
        )

        activar_autofiltro(
            documento,
            hoja_usuario_equipo,
            "FiltroUsuarioEquipo",
            len(encabezados_usuario_equipo),
            len(interaccion_usuario_equipo),
        )

        congelar_primera_fila(
            documento,
            hoja_usuario_equipo,
        )

        aplicar_formato_numerico(
            documento,
            hoja_usuario_equipo,
            3,
            len(interaccion_usuario_equipo),
            "0",
        )
        aplicar_formato_numerico(
            documento,
            hoja_usuario_equipo,
            4,
            len(interaccion_usuario_equipo),
            "0.00%",
        )
        aplicar_formato_numerico(
            documento,
            hoja_usuario_equipo,
            5,
            len(interaccion_usuario_equipo),
            "0.00",
        )
        aplicar_formato_numerico(
            documento,
            hoja_usuario_equipo,
            6,
            len(interaccion_usuario_equipo),
            "0.00%",
        )

        salida.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        url_salida = (
            uno.systemPathToFileUrl(
                str(
                    salida.resolve()
                )
            )
        )

        documento.storeAsURL(
            url_salida,
            (
                propiedad(
                    "FilterName",
                    (
                        "Calc MS Excel "
                        "2007 XML"
                    ),
                ),
                propiedad(
                    "Overwrite",
                    True,
                ),
            ),
        )

    finally:
        if documento is not None:
            try:
                documento.close(
                    True
                )

            except Exception:
                try:
                    documento.dispose()

                except Exception:
                    pass

        try:
            proc.terminate()
            proc.wait(timeout=5)

        except Exception:
            try:
                proc.kill()

            except Exception:
                pass

        shutil.rmtree(
            perfil,
            ignore_errors=True,
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Genera un reporte Excel "
            "de metricas de interacciones "
            "y tiempos Redmine."
        )
    )

    parser.add_argument(
        "fecha_desde",
        help=(
            "Fecha desde "
            "YYYY-MM-DD"
        ),
    )

    parser.add_argument(
        "fecha_hasta",
        help=(
            "Fecha hasta "
            "YYYY-MM-DD"
        ),
    )

    parser.add_argument(
        "archivo_salida",
        help=(
            "Ruta del archivo XLSX "
            "a generar"
        ),
    )

    args = parser.parse_args()

    try:
        validar_agente()

        fecha_desde = (
            validar_fecha(
                args.fecha_desde
            )
        )

        fecha_hasta = (
            validar_fecha(
                args.fecha_hasta
            )
        )

        if fecha_desde > fecha_hasta:
            raise ValueError(
                "La fecha desde no puede "
                "ser posterior a la "
                "fecha hasta."
            )

        salida = Path(
            args.archivo_salida
        ).expanduser()

        if (
            salida.suffix.lower()
            != ".xlsx"
        ):
            salida = (
                salida.with_suffix(
                    ".xlsx"
                )
            )

        print(
            "Consultando interacciones..."
        )

        interacciones = (
            obtener_interacciones(
                fecha_desde.isoformat(),
                fecha_hasta.isoformat(),
            )
        )

        print(
            "Consultando tiempos Redmine..."
        )

        tiempos_redmine = (
            obtener_tiempos_redmine(
                fecha_desde.isoformat(),
                fecha_hasta.isoformat(),
            )
        )

        print(
            "Calculando resumenes por equipo..."
        )

        interaccion_agente_equipo = (
            construir_interaccion_agente_por_equipo(
                interacciones
            )
        )

        interaccion_usuario_equipo = (
            construir_interaccion_usuario_por_equipo(
                interacciones
            )
        )

        print(
            "Generando Excel..."
        )

        generar_excel(
            salida,
            interacciones,
            tiempos_redmine,
            interaccion_agente_equipo,
            interaccion_usuario_equipo,
        )

        print()

        print(
            "Interacciones: "
            f"{len(interacciones)}"
        )

        print(
            "Tiempos Redmine: "
            f"{len(tiempos_redmine)}"
        )

        print(
            "Agentes por equipo: "
            f"{len(interaccion_agente_equipo)}"
        )

        print(
            "Usuarios por equipo: "
            f"{len(interaccion_usuario_equipo)}"
        )

        print(
            "Archivo generado: "
            f"{salida.resolve()}"
        )

        return 0

    except Exception as exc:
        print(
            f"ERROR | {exc}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())

