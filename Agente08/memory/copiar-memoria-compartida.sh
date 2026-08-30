#!/usr/bin/env bash

set -euo pipefail

PASSPHRASE='luis1234'

ORIGEN="$HOME/.openclaw/workspace/memory"

CLAVE_AGENTE07="$HOME/.openclaw/workspace/ssh-keys/Agente07/id_rsa_desarrollo-ia-07"
CLAVE_AGENTE03="$HOME/.openclaw/workspace/ssh-keys/Agente03/id_rsa_desarrollo-ia-03"

HOST_AGENTE07="desarrollo-ia-07@10.194.0.37"
HOST_AGENTE03="luispicone@10.194.0.32"

DESTINO_AGENTE07="/home/desarrollo-ia-07/.openclaw/workspace/memory/compartida/Agente08"
DESTINO_AGENTE03="/home/luispicone/.openclaw/workspace/memory/compartida/Agente08"

ARCHIVOS=()

while IFS= read -r -d '' ARCHIVO; do
    ARCHIVOS+=("$ARCHIVO")
done < <(
    find "$ORIGEN" \
        -maxdepth 1 \
        -type f \
        -name '*.md' \
        -print0
)

if [[ "${#ARCHIVOS[@]}" -eq 0 ]]; then
    echo "No se encontraron archivos Markdown en $ORIGEN"
    exit 0
fi

ASKPASS_SCRIPT="$(mktemp)"

cleanup() {
    rm -f "$ASKPASS_SCRIPT"
    unset SSH_KEY_PASSPHRASE
}

trap cleanup EXIT

cat > "$ASKPASS_SCRIPT" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$SSH_KEY_PASSPHRASE"
EOF

chmod 700 "$ASKPASS_SCRIPT"

export SSH_KEY_PASSPHRASE="$PASSPHRASE"
export SSH_ASKPASS="$ASKPASS_SCRIPT"
export SSH_ASKPASS_REQUIRE="force"
export DISPLAY=":0"

copiar_faltantes() {
    local CLAVE="$1"
    local HOST="$2"
    local DESTINO="$3"
    local NOMBRE_DESTINO="$4"

    local FALTANTES=()
    local ARCHIVO
    local NOMBRE
    local ESTADO

    echo
    echo "Revisando $NOMBRE_DESTINO..."

    for ARCHIVO in "${ARCHIVOS[@]}"; do
        NOMBRE="$(basename "$ARCHIVO")"

        set +e
        setsid -w ssh \
            -i "$CLAVE" \
            -o IdentitiesOnly=yes \
            -o BatchMode=no \
            -o NumberOfPasswordPrompts=1 \
            -o StrictHostKeyChecking=accept-new \
            "$HOST" \
            "test -f '$DESTINO/$NOMBRE'" \
            </dev/null

        ESTADO=$?
        set -e

        if [[ "$ESTADO" -eq 0 ]]; then
            continue
        elif [[ "$ESTADO" -eq 1 ]]; then
            FALTANTES+=("$ARCHIVO")
        else
            echo "ERROR: no se pudo verificar $NOMBRE_DESTINO."
            return "$ESTADO"
        fi
    done

    if [[ "${#FALTANTES[@]}" -eq 0 ]]; then
        echo "$NOMBRE_DESTINO: no hay archivos faltantes."
        return 0
    fi

    echo "$NOMBRE_DESTINO: ${#FALTANTES[@]} archivos faltantes."

    setsid -w scp \
        -i "$CLAVE" \
        -o IdentitiesOnly=yes \
        -o BatchMode=no \
        -o NumberOfPasswordPrompts=1 \
        -o StrictHostKeyChecking=accept-new \
        -p \
        -- "${FALTANTES[@]}" \
        "$HOST:$DESTINO/" \
        </dev/null

    echo "$NOMBRE_DESTINO: copia completada."
}

echo "Archivos Markdown en origen: ${#ARCHIVOS[@]}"

copiar_faltantes \
    "$CLAVE_AGENTE07" \
    "$HOST_AGENTE07" \
    "$DESTINO_AGENTE07" \
    "Agente07"

copiar_faltantes \
    "$CLAVE_AGENTE03" \
    "$HOST_AGENTE03" \
    "$DESTINO_AGENTE03" \
    "Agente03"

echo
echo "Sincronización de memoria compartida finalizada."
