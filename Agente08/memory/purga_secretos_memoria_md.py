#!/usr/bin/env python3

import argparse
import math
import os
import re
import stat
import sys
import tempfile
from pathlib import Path


MARKER = "[SECRETO REDACTADO]"
RC_OK = 0
RC_ERROR = 1


# ----------------------------------------------------------------------
# Mensajes del Markdown generado por genera_memoria_md.py
# ----------------------------------------------------------------------

MESSAGE_RE = re.compile(
    r"""(?ms)
    (
        ^\#\#\#[ ]\[
        (?P<timestamp>[^\]]+)
        \][ ]
        (?P<author>[^\n]+)
        \n\n
    )
    (?P<body>.*?)
    (?=
        \n---\n
        |
        \Z
    )
    """,
    re.VERBOSE,
)


# ----------------------------------------------------------------------
# Detección contextual
# ----------------------------------------------------------------------

SECRET_TERMS_RE = re.compile(
    r"""(?ix)
    \b(
        password
        | passwd
        | pwd
        | pass
        | passphrase
        | contraseña
        | contrasena
        | clave
        | token
        | api[\s_-]*key
        | apikey
        | api[\s_-]*token
        | access[\s_-]*token
        | refresh[\s_-]*token
        | client[\s_-]*secret
        | secret
        | secreto
        | credencial(?:es)?
        | pin
        | otp
        | mfa
        | 2fa
        | recovery[\s_-]*code
        | código[\s_-]*de[\s_-]*recuperación
        | codigo[\s_-]*de[\s_-]*recuperacion
    )\b
    """
)


REQUEST_SECRET_RE = re.compile(
    r"""(?ix)
    \b(
        pasame
        | pásame
        | pasáme
        | dame
        | decime
        | dime
        | indicame
        | indícame
        | mostrame
        | muestrame
        | muéstrame
        | enviame
        | envíame
        | compartime
        | comparteme
        | compárteme
        | peg[aá]
        | ingres[aá]
        | introduc[ií]
        | proporcion[aá]
        | necesito
        | confirmame
        | confirmáme
        | cuál[\s]+es
        | cual[\s]+es
        | what[\s]+is
        | provide
        | send
        | paste
        | enter
        | share
    )\b
    """
)


HOWTO_RE = re.compile(
    r"""(?ix)
    \b(
        cómo
        | como
        | dónde
        | donde
        | procedimiento
        | forma[\s]+de
        | comando[\s]+para
        | cómo[\s]+generar
        | como[\s]+generar
        | cómo[\s]+crear
        | como[\s]+crear
        | cómo[\s]+obtener
        | como[\s]+obtener
    )\b
    """
)


REFUSAL_RE = re.compile(
    r"""(?ix)
    ^\s*(
        no
        | no[\s]+te
        | no[\s]+la
        | no[\s]+lo
        | prefiero[\s]+no
        | no[\s]+tengo
        | no[\s]+quiero
        | no[\s]+puedo
    )\b
    """
)


def es_agente(author):
    return author.strip().casefold() == "agente"


def rol_opuesto(role):
    return "user" if role == "assistant" else "assistant"


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------

def entropia_shannon(valor):
    if not valor:
        return 0.0

    frecuencias = {}

    for caracter in valor:
        frecuencias[caracter] = frecuencias.get(caracter, 0) + 1

    largo = len(valor)

    return -sum(
        (cantidad / largo) * math.log2(cantidad / largo)
        for cantidad in frecuencias.values()
    )


def parece_uuid(valor):
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{8}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}",
            valor,
        )
    )


def parece_hash_hex(valor):
    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]{32,128}",
            valor,
        )
    )


def extension_conocida(valor):
    extensiones = (
        ".md",
        ".py",
        ".json",
        ".jsonl",
        ".sql",
        ".txt",
        ".doc",
        ".docx",
        ".html",
        ".htm",
        ".js",
        ".ts",
        ".tsx",
        ".php",
        ".ini",
        ".yaml",
        ".yml",
        ".xml",
        ".csv",
        ".xlsx",
        ".xls",
        ".srw",
        ".sru",
        ".srd",
        ".dll",
        ".exe",
    )

    return valor.lower().endswith(extensiones)


def parece_secreto_aislado(texto):
    valor = texto.strip().strip("`'\" ")

    if not valor or valor == MARKER:
        return False

    if "\n" in valor or " " in valor or "\t" in valor:
        return False

    if len(valor) < 10 or len(valor) > 300:
        return False

    if valor.startswith(
        (
            "http://",
            "https://",
            "/",
            "./",
            "../",
            "~",
        )
    ):
        return False

    if "@" in valor:
        return False

    if parece_uuid(valor):
        return False

    if parece_hash_hex(valor):
        return False

    if extension_conocida(valor):
        return False

    clases = sum(
        (
            bool(re.search(r"[a-z]", valor)),
            bool(re.search(r"[A-Z]", valor)),
            bool(re.search(r"[0-9]", valor)),
            bool(re.search(r"[^A-Za-z0-9]", valor)),
        )
    )

    return (
        clases >= 3
        and entropia_shannon(valor) >= 3.4
    )


def solicita_secreto(texto):
    if not SECRET_TERMS_RE.search(texto):
        return False

    if not REQUEST_SECRET_RE.search(texto):
        return False

    if HOWTO_RE.search(texto):
        directo = re.search(
            r"""(?ix)
            \b(
                dame
                | pasame
                | pásame
                | mostrame
                | muestrame
                | enviame
                | envíame
                | cuál[\s]+es
                | cual[\s]+es
            )\b
            """,
            texto,
        )

        if not directo:
            return False

    return True


def es_rechazo_de_entregar_secreto(texto):
    return bool(
        REFUSAL_RE.search(texto)
    )


def candidatos_de_respuesta_secreta(texto):
    candidatos = set()

    limpio = texto.strip()

    if not limpio:
        return candidatos

    simple = limpio.strip("`'\" ")

    if (
        "\n" not in simple
        and 4 <= len(simple) <= 200
        and " " not in simple
    ):
        candidatos.add(simple)

    tokens = re.findall(
        r"[^\s`'\";,(){}\[\]<>]+",
        limpio,
    )

    for token in tokens:
        token = token.strip()

        if len(token) < 4:
            continue

        if token == MARKER:
            continue

        if parece_uuid(token):
            continue

        if extension_conocida(token):
            continue

        if re.fullmatch(
            r"\d{4,10}",
            token,
        ):
            candidatos.add(token)
            continue

        clases = sum(
            (
                bool(re.search(r"[a-z]", token)),
                bool(re.search(r"[A-Z]", token)),
                bool(re.search(r"\d", token)),
                bool(re.search(r"[^A-Za-z0-9]", token)),
            )
        )

        if (
            len(token) >= 8
            and clases >= 3
        ):
            candidatos.add(token)

    return candidatos


# ----------------------------------------------------------------------
# Purga contextual
# ----------------------------------------------------------------------

def purgar_contexto(texto):
    matches = list(
        MESSAGE_RE.finditer(texto)
    )

    if not matches:
        return texto, 0, set()

    resultado = []
    posicion = 0

    pendiente_para = None
    secretos_conocidos = set()
    redacciones = 0

    for match in matches:
        resultado.append(
            texto[posicion:match.start()]
        )

        cabecera = match.group(1)

        author = match.group(
            "author"
        ).strip()

        cuerpo_original = match.group(
            "body"
        )

        role = (
            "assistant"
            if es_agente(author)
            else "user"
        )

        cuerpo = cuerpo_original

        if pendiente_para == role:

            if not es_rechazo_de_entregar_secreto(
                cuerpo_original
            ):
                secretos_conocidos.update(
                    candidatos_de_respuesta_secreta(
                        cuerpo_original
                    )
                )

                cuerpo = MARKER

                redacciones += 1

            pendiente_para = None

        elif parece_secreto_aislado(
            cuerpo_original
        ):
            secretos_conocidos.update(
                candidatos_de_respuesta_secreta(
                    cuerpo_original
                )
            )

            cuerpo = MARKER

            redacciones += 1

        if solicita_secreto(
            cuerpo_original
        ):
            pendiente_para = rol_opuesto(
                role
            )

        resultado.append(
            cabecera
        )

        resultado.append(
            cuerpo
        )

        posicion = match.end()

    resultado.append(
        texto[posicion:]
    )

    return (
        "".join(resultado),
        redacciones,
        secretos_conocidos,
    )


def purgar_secretos_conocidos(
    texto,
    secretos,
):
    total = 0

    for secreto in sorted(
        secretos,
        key=len,
        reverse=True,
    ):
        if not secreto:
            continue

        if secreto == MARKER:
            continue

        cantidad = texto.count(
            secreto
        )

        if cantidad:
            texto = texto.replace(
                secreto,
                MARKER,
            )

            total += cantidad

    return texto, total


# ----------------------------------------------------------------------
# Patrones explícitos
# ----------------------------------------------------------------------

def purgar_patrones(texto):

    total = 0

    def aplicar(
        patron,
        reemplazo,
        flags=0,
    ):
        nonlocal texto
        nonlocal total

        regex = re.compile(
            patron,
            flags,
        )

        texto, cantidad = regex.subn(
            reemplazo,
            texto,
        )

        total += cantidad

    # --------------------------------------------------------------
    # Claves privadas
    # --------------------------------------------------------------

    aplicar(
        r"""
        -----BEGIN[ ]
        (?:
            RSA[ ]PRIVATE[ ]KEY
            | EC[ ]PRIVATE[ ]KEY
            | DSA[ ]PRIVATE[ ]KEY
            | OPENSSH[ ]PRIVATE[ ]KEY
            | ENCRYPTED[ ]PRIVATE[ ]KEY
            | PRIVATE[ ]KEY
        )
        [ ]*-----
        .*?
        -----END[ ]
        (?:
            RSA[ ]PRIVATE[ ]KEY
            | EC[ ]PRIVATE[ ]KEY
            | DSA[ ]PRIVATE[ ]KEY
            | OPENSSH[ ]PRIVATE[ ]KEY
            | ENCRYPTED[ ]PRIVATE[ ]KEY
            | PRIVATE[ ]KEY
        )
        [ ]*-----
        """,
        MARKER,
        re.IGNORECASE
        | re.DOTALL
        | re.VERBOSE,
    )

    aplicar(
        r"""
        -----BEGIN[ ]PGP[ ]PRIVATE[ ]KEY[ ]BLOCK-----
        .*?
        -----END[ ]PGP[ ]PRIVATE[ ]KEY[ ]BLOCK-----
        """,
        MARKER,
        re.IGNORECASE
        | re.DOTALL
        | re.VERBOSE,
    )

    # --------------------------------------------------------------
    # Authorization / headers
    # --------------------------------------------------------------

    aplicar(
        r"""(?im)
        ^
        (
            [ \t]*
            (?:
                Authorization
                | Proxy-Authorization
            )
            [ \t]*:[ \t]*
            (?:
                Bearer
                | Basic
                | Token
            )
            [ \t]+
        )
        [^\r\n]+
        $
        """,
        rf"\1{MARKER}",
        re.VERBOSE,
    )

    aplicar(
        r"""(?im)
        ^
        (
            [ \t]*
            (?:
                X-API-Key
                | X-Auth-Token
                | X-Amz-Security-Token
            )
            [ \t]*:[ \t]*
        )
        [^\r\n]+
        $
        """,
        rf"\1{MARKER}",
        re.VERBOSE,
    )

    aplicar(
        r"""(?im)
        ^
        (
            [ \t]*
            (?:
                Cookie
                | Set-Cookie
            )
            [ \t]*:[ \t]*
        )
        [^\r\n]+
        $
        """,
        rf"\1{MARKER}",
        re.VERBOSE,
    )

    # --------------------------------------------------------------
    # Nombre base de secreto
    # --------------------------------------------------------------

    etiqueta = r"""
        (?:
            password
            | passwd
            | pwd
            | pass
            | passphrase
            | contrase(?:ñ|n)a
            | clave
            | token
            | api[\s_-]*key
            | apikey
            | api[\s_-]*token
            | access[\s_-]*token
            | refresh[\s_-]*token
            | client[\s_-]*secret
            | secret
            | secreto
            | pin
            | otp
            | mfa
            | 2fa
            | recovery[\s_-]*code
            | codigo[\s_-]*de[\s_-]*recuperacion
            | código[\s_-]*de[\s_-]*recuperación
        )
    """

    # --------------------------------------------------------------
    # Credenciales calificadas por servicio
    #
    # contraseña SVN: xxxx
    # pass PEPE: xxxx
    # clave SSH: xxxx
    # password DB: xxxx
    # token Jira: xxxx
    #
    # Se permiten hasta 4 palabras entre el nombre del secreto
    # y ":" o "=".
    # --------------------------------------------------------------

    aplicar(
        rf"""(?imx)
        ^
        (
            [ \t]*
            {etiqueta}
            (?:
                [ \t]+
                [A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_.-]+
            ){{0,4}}
            [ \t]*
            (?:
                =
                | :
            )
            [ \t]*
        )
        [^\r\n]+
        $
        """,
        rf"\1{MARKER}",
    )

    # --------------------------------------------------------------
    # Variables técnicas
    #
    # DB_PASSWORD=xxxx
    # SVN_PASS=xxxx
    # JIRA_TOKEN=xxxx
    # CLIENT_SECRET=xxxx
    # --------------------------------------------------------------

    aplicar(
        r"""(?imx)
        ^
        (
            [ \t]*
            [A-Za-z][A-Za-z0-9_.-]*
            (?:
                [_\.-]password
                | [_\.-]passwd
                | [_\.-]pwd
                | [_\.-]pass
                | [_\.-]token
                | [_\.-]secret
                | [_\.-]api[_\.-]?key
                | [_\.-]private[_\.-]?key
                | [_\.-]client[_\.-]?secret
            )
            [ \t]*
            (?:
                =
                | :
            )
            [ \t]*
        )
        [^\r\n]+
        $
        """,
        rf"\1{MARKER}",
    )

    # --------------------------------------------------------------
    # JSON / diccionarios
    #
    # "password": "xxxx"
    # 'token': 'xxxx'
    # --------------------------------------------------------------

    aplicar(
        rf"""(?ix)
        (
            ["']
            {etiqueta}
            ["']
            [ \t]*:[ \t]*
            ["']
        )
        [^"'\r\n]*
        (["'])
        """,
        rf"\1{MARKER}\2",
    )

    # --------------------------------------------------------------
    # Lenguaje natural
    #
    # la contraseña SVN es xxxx
    # mi clave es xxxx
    # el token Jira es xxxx
    # --------------------------------------------------------------

    aplicar(
        rf"""(?ix)
        (
            \b
            (?:
                la
                | el
                | mi
            )?
            [ \t]*
            {etiqueta}
            (?:
                [ \t]+
                [A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_.-]+
            ){{0,4}}
            [ \t]+
            (?:
                es
                | is
            )
            [ \t]+
        )
        [^\r\n]+
        """,
        rf"\1{MARKER}",
    )

    # --------------------------------------------------------------
    # Argumentos CLI
    #
    # --password xxxx
    # --pass xxxx
    # --token xxxx
    # --password=xxxx
    # --------------------------------------------------------------

    aplicar(
        r"""(?ix)
        (
            --
            (?:
                password
                | passwd
                | pwd
                | pass
                | passphrase
                | token
                | api-key
                | apikey
                | access-token
                | refresh-token
                | client-secret
                | secret
                | secret-key
                | private-key
                | auth-token
                | jira-token
                | github-token
            )
            (?:
                =
                | [\t ]+
            )
        )
        (?:
            "[^"\r\n]*"
            | '[^'\r\n]*'
            | [^\s]+
        )
        """,
        rf"\1{MARKER}",
    )

    # sshpass -p xxxx
    aplicar(
        r"""(?ix)
        (
            \bsshpass
            [\t ]+
            -p
            [\t ]+
        )
        (?:
            "[^"\r\n]*"
            | '[^'\r\n]*'
            | [^\s]+
        )
        """,
        rf"\1{MARKER}",
    )

    # curl -u usuario:password
    aplicar(
        r"""(?ix)
        (
            \bcurl\b
            [^\r\n]*?
            [\t ]+
            (?:
                -u
                | --user
            )
            [\t ]+
        )
        (?:
            "[^"\r\n]*"
            | '[^'\r\n]*'
            | [^\s]+
        )
        """,
        rf"\1{MARKER}",
    )

    # --------------------------------------------------------------
    # Credenciales dentro de URLs
    #
    # https://usuario:password@host
    # svn://usuario:password@host
    # --------------------------------------------------------------

    aplicar(
        r"""(?ix)
        (
            \b
            (?:
                https?
                | svn
                | svn\+ssh
                | ssh
                | ftp
                | ftps
            )
            ://
            [^/\s:@]+
            :
        )
        [^@\s/]+
        (@)
        """,
        rf"\1{MARKER}\2",
    )

    # --------------------------------------------------------------
    # Secretos en parámetros URL
    # --------------------------------------------------------------

    aplicar(
        r"""(?ix)
        (
            [\?&]
            (?:
                token
                | access_token
                | refresh_token
                | api_key
                | apikey
                | client_secret
                | password
                | passwd
                | pwd
                | pass
                | auth_token
                | signature
                | sig
                | x-amz-signature
                | x-amz-security-token
                | x-goog-signature
            )
            =
        )
        [^&#\s]+
        """,
        rf"\1{MARKER}",
    )

    # --------------------------------------------------------------
    # Formatos conocidos de tokens
    # --------------------------------------------------------------

    patrones_tokens = [

        # JWT
        r"\beyJ[A-Za-z0-9_-]{5,}\."
        r"[A-Za-z0-9_-]{5,}\."
        r"[A-Za-z0-9_-]{5,}\b",

        # OpenAI / Anthropic
        r"\bsk-(?:proj-|ant-)?"
        r"[A-Za-z0-9_-]{16,}\b",

        # GitHub
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
        r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",

        # GitLab
        r"\bglpat-[A-Za-z0-9_-]{20,}\b",

        # Slack
        r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",

        # Google API Key
        r"\bAIza[A-Za-z0-9_-]{20,}\b",

        # AWS Access Key
        r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",

        # Stripe
        r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b",

        # SendGrid
        r"\bSG\."
        r"[A-Za-z0-9_-]{16,}\."
        r"[A-Za-z0-9_-]{16,}\b",

        # HashiCorp Vault
        r"\bhvs\.[A-Za-z0-9_-]{20,}\b",
    ]

    for patron in patrones_tokens:
        aplicar(
            patron,
            MARKER,
            re.IGNORECASE,
        )

    return texto, total


# ----------------------------------------------------------------------
# Escritura
# ----------------------------------------------------------------------

def escribir_atomico(
    ruta,
    contenido,
    tenia_bom,
    newline,
):
    modo_original = stat.S_IMODE(
        ruta.stat().st_mode
    )

    if newline != "\n":
        contenido = contenido.replace(
            "\n",
            newline,
        )

    datos = contenido.encode(
        "utf-8"
    )

    if tenia_bom:
        datos = (
            b"\xef\xbb\xbf"
            + datos
        )

    fd, temporal = tempfile.mkstemp(
        prefix=f".{ruta.name}.",
        suffix=".tmp",
        dir=str(ruta.parent),
    )

    try:

        with os.fdopen(
            fd,
            "wb",
        ) as archivo:
            archivo.write(datos)

        os.chmod(
            temporal,
            modo_original,
        )

        os.replace(
            temporal,
            ruta,
        )

    except Exception:

        try:
            os.unlink(
                temporal
            )
        except OSError:
            pass

        raise


# ----------------------------------------------------------------------
# Proceso principal
# ----------------------------------------------------------------------

def purgar_archivo(ruta):

    raw = ruta.read_bytes()

    tenia_bom = raw.startswith(
        b"\xef\xbb\xbf"
    )

    if tenia_bom:
        raw = raw[3:]

    try:
        texto_original = raw.decode(
            "utf-8"
        )

    except UnicodeDecodeError as exc:

        raise RuntimeError(
            "El archivo no está codificado "
            f"en UTF-8: {exc}"
        ) from exc

    newline = (
        "\r\n"
        if "\r\n" in texto_original
        else "\n"
    )

    texto = texto_original.replace(
        "\r\n",
        "\n",
    )

    # 1. Detección contextual
    (
        texto,
        total_contexto,
        secretos_conocidos,
    ) = purgar_contexto(
        texto
    )

    # 2. Repeticiones de secretos obtenidos por contexto
    (
        texto,
        total_conocidos,
    ) = purgar_secretos_conocidos(
        texto,
        secretos_conocidos,
    )

    # 3. Patrones explícitos
    (
        texto,
        total_patrones,
    ) = purgar_patrones(
        texto
    )

    total = (
        total_contexto
        + total_conocidos
        + total_patrones
    )

    original_normalizado = (
        texto_original.replace(
            "\r\n",
            "\n",
        )
    )

    if texto != original_normalizado:

        escribir_atomico(
            ruta,
            texto,
            tenia_bom,
            newline,
        )

    return total


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Purga contraseñas, tokens, claves "
            "y otros secretos de una memoria "
            "Markdown generada por OpenClaw."
        )
    )

    parser.add_argument(
        "archivo",
        help=(
            "Archivo MEMORY-*.md "
            "que se modificará in-place."
        ),
    )

    args = parser.parse_args()

    ruta = Path(
        args.archivo
    ).expanduser()

    if not ruta.is_file():

        print(
            "ERROR | No existe el archivo: "
            f"{ruta}",
            file=sys.stderr,
        )

        return RC_ERROR

    try:

        total = purgar_archivo(
            ruta
        )

    except Exception as exc:

        print(
            "ERROR | No se pudo purgar "
            f"el archivo: {exc}",
            file=sys.stderr,
        )

        return RC_ERROR

    print(
        f"Purga completada: {ruta}"
    )

    print(
        "Secretos redactados: "
        f"{total}"
    )

    return RC_OK


if __name__ == "__main__":
    sys.exit(main())
