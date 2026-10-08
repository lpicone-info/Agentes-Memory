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
            "Generando Excel..."
        )

        generar_excel(
            salida,
            interacciones,
            tiempos_redmine,
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
