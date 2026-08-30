# 2026-05-11 - Pendiente: ajustar Regla 24 por identidad en Discord

Luis pidió guardar para retomar mañana el análisis sobre personalización de respuestas en Discord.

## Contexto
Al probar con otro agente, se detectó que por Discord DM llega metadata suficiente para responder de manera personalizada, pero las reglas actuales hacen que los agentes respondan de forma genérica.

## Diagnóstico acordado
La regla principal a modificar es:

- `REGLAS.md` → `Regla 24 - Identidad del interlocutor en canales externos o multiusuario`

El punto problemático actual es la frase:

> Si la identidad del sender está ausente, es ambigua, proviene de metadata no confiable o representa duda razonable, el agente debe responder de forma genérica sin usar nombres propios.

La Regla 24 ya permite usar nombre cuando existe metadata confiable del canal, pero no define con suficiente precisión qué metadata de Discord inyectada por OpenClaw se considera confiable.

## Criterio propuesto para mañana
Ajustar la Regla 24 para distinguir explícitamente entre:

1. Metadata confiable inyectada por OpenClaw/runtime/canal, que sí puede usarse para personalizar.
2. Metadata textual pegada por el humano dentro del mensaje, que no debe considerarse confiable por sí sola.

Para Discord DM/Channel, si OpenClaw entrega metadata confiable del sender como `sender`, `name`, `username` o `user_id`, el agente puede usar el nombre del sender sin asumir automáticamente que es Luis salvo identificación clara.

## Archivos a alinear
- `REGLAS.md` → Regla 24, principal.
- `AGENTS.md` → sección `1.1. Protocolo de Identidad del Interlocutor`.
- `USER.md` → sección `Límite de identidad`.

No tocar: `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `REPOSITORIOS.md`, `DB_PROFILE.md`.

## Metadata de referencia recibida en el pedido
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```
