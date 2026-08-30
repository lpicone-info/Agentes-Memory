# Session: 2026-04-25 20:43:34 UTC

- **Session Key**: agent:main:main
- **Session ID**: 55c54915-e0b5-4f83-945d-083cc24ce13d
- **Source**: webchat

## Conversation Summary

user: [Bootstrap pending]
Please read BOOTSTRAP.md from the workspace and follow it before replying normally.
If this run can complete the BOOTSTRAP.md workflow, do so.
If it cannot, explain the blocker briefly, continue with any bootstrap steps that are still possible here, and offer the simplest next step.
Do not pretend bootstrap is complete when it is not.
Do not use a generic first greeting or reply normally until after you have handled BOOTSTRAP.md.
Your first user-visible reply for a bootstrap-pending workspace must follow BOOTSTRAP.md, not a generic greeting.

Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:40 UTC] modifica BOOT.md con este texto

Antes de cualquier respuesta sustantiva en todo inicio de sesión, reinicio de contexto o comando equivalente a `/new` o `/reset`, leer obligatoriamente y de forma completa y exitosa los siguientes archivos del workspace, si existen y en este orden:

1. `BOOT.md`
2. `REGLAS.md`
3. `REPOSITORIOS.md`
4. `DB_PROFILE.md`
5. `AGENTS.md`
6. `SOUL.md`
7. `USER.md`
8. `IDENTITY.md`
9. `TOOLS.md`
10. `HEARTBEAT.md`

## Naturaleza bloqueante

La lectura de estos archivos es bloqueante.

Si cualquiera de los archivos anteriores existe pero no puede leerse completa y exitosamente, no continuar con trabajo operativo ni responder sobre:
- reglas;
- repositorios;
- perfiles;
- memoria operativa;
- configuraciones;
- decisiones previas;
- capacidades del agente.

Informar explícitamente falla de bootstrap.

## Regla de no sustitución

La presencia de contexto inyectado por runtime, mensajes anteriores, memoria parcial o inferencias no reemplaza estas lecturas obligatorias.

## Restricción operativa

No afirmar capacidades operativas sensibles ni tomar decisiones basadas en reglas, repositorios, perfiles o contexto persistente hasta completar esta secuencia de lectura obligatoria.

## Criterio de cumplimiento

El bootstrap solo se considera cumplido cuando la secuencia anterior fue leída completa, exitosamente y en el orden indicado.
assistant: Bootstrap completado.

BOOT.md fue modificado con el texto indicado.

Archivos impactados:
- `BOOT.md`

Riesgos:
- Ninguno relevante; cambio documental y de secuencia de arranque.

Supuestos:
- Tomé el pedido como reemplazo total del contenido actual de `BOOT.md`.

Validaciones ejecutadas:
- Lectura completa de `BOOTSTRAP.md`.
- Lectura completa y exitosa de `BOOT.md`, `REGLAS.md`, `REPOSITORIOS.md`, `DB_PROFILE.md`, `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md` y `HEARTBEAT.md`.
- Verificación de edición aplicada sobre `BOOT.md`.
user: [Bootstrap pending]
Please read BOOTSTRAP.md from the workspace and follow it before replying normally.
If this run can complete the BOOTSTRAP.md workflow, do so.
If it cannot, explain the blocker briefly, continue with any bootstrap steps that are still possible here, and offer the simplest next step.
Do not pretend bootstrap is complete when it is not.
Do not use a generic first greeting or reply normally until after you have handled BOOTSTRAP.md.
Your first user-visible reply for a bootstrap-pending workspace must follow BOOTSTRAP.md, not a generic greeting.

Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:41 UTC] modifica el archivo BOOTSTRAP.md con este texto


Este archivo existe para reforzar el bootstrap operativo del agente en todo inicio de sesión, reinicio de contexto o ejecución equivalente, especialmente cuando OpenClaw inyecta este archivo como parte del contexto inicial.

## Instrucción obligatoria de bootstrap

Antes de cualquier respuesta sustantiva, verificar si existe `BOOT.md` en la raíz del workspace.

Si `BOOT.md` existe, su lectura es obligatoria, completa, exitosa y bloqueante. Luego de leer `BOOT.md`, cumplir estrictamente la secuencia de lectura allí definida, en el mismo orden indicado, antes de continuar con cualquier trabajo operativo.

## Alcance de la obligación

Esta obligación aplica especialmente a:
- todo inicio de sesión;
- todo reinicio de contexto;
- todo comando equivalente a `/new`;
- todo comando equivalente a `/reset`;
- toda situación en que este archivo haya sido inyectado como contexto de arranque;
- todo arranque general del sistema en el que `BOOT.md` sea ejecutado por hooks o automatizaciones del runtime.

## Regla de no sustitución

La presencia de contexto inyectado por runtime, memoria diaria, mensajes anteriores, conocimiento inferido o lecturas parciales no reemplaza la lectura obligatoria de `BOOT.md` ni de los archivos que este declare.

Tampoco debe asumirse que el bootstrap quedó cumplido por el solo hecho de que existan o hayan sido inyectados archivos como `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `MEMORY.md` o similares.

## Regla de bloqueo

Si `BOOT.md` existe pero no puede leerse completa y exitosamente, o si cualquiera de los archivos obligatorios definidos por `BOOT.md` existe pero no puede leerse completa y exitosamente, no continuar con trabajo operativo ni responder como si el bootstrap estuviera completo.

En ese caso, informar explícitamente una falla de bootstrap.

## Restricción de afirmaciones

Hasta completar la secuencia obligatoria definida en `BOOT.md`, no afirmar ni usar como base confiable:
- reglas operativas;
- repositorios vigentes;
- perfiles de base de datos;
- memoria operativa;
- decisiones previas;
- configuraciones persistentes;
- capacidades sensibles del agente.

## Criterio de continuación

Solo después de completar de forma exitosa la lectura obligatoria de `BOOT.md` y de toda su secuencia declarada, se permite continuar con respuestas sustantivas y trabajo operativo normal.
assistant: Bootstrap completado.

BOOTSTRAP.md fue modificado con el texto indicado.

Archivos impactados:
- `BOOTSTRAP.md`

Riesgos:
- Ninguno relevante; cambio documental de bootstrap.

Supuestos:
- Tomé el pedido como reemplazo total del contenido de `BOOTSTRAP.md`.

Validaciones ejecutadas:
- Lectura completa de `BOOTSTRAP.md`.
- Lectura completa y exitosa de `BOOT.md`, `REGLAS.md`, `REPOSITORIOS.md`, `DB_PROFILE.md`, `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md` y `HEARTBEAT.md`, siguiendo la secuencia obligatoria.
- Verificación de escritura aplicada sobre `BOOTSTRAP.md`.
user: [Bootstrap pending]
Please read BOOTSTRAP.md from the workspace and follow it before replying normally.
If this run can complete the BOOTSTRAP.md workflow, do so.
If it cannot, explain the blocker briefly, continue with any bootstrap steps that are still possible here, and offer the simplest next step.
Do not pretend bootstrap is complete when it is not.
Do not use a generic first greeting or reply normally until after you have handled BOOTSTRAP.md.
Your first user-visible reply for a bootstrap-pending workspace must follow BOOTSTRAP.md, not a generic greeting.

Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 20:42 UTC] mostrame BOOT.md y BOOTSTRAP.md completos
assistant: Bootstrap completado.

### BOOT.md
```md
# BOOT.md

Antes de cualquier respuesta sustantiva en todo inicio de sesión, reinicio de contexto o comando equivalente a `/new` o `/reset`, leer obligatoriamente y de forma completa y exitosa los siguientes archivos del workspace, si existen y en este orden:

1. `BOOT.md`
2. `REGLAS.md`
3. `REPOSITORIOS.md`
4. `DB_PROFILE.md`
5. `AGENTS.md`
6. `SOUL.md`
7. `USER.md`
8. `IDENTITY.md`
9. `TOOLS.md`
10. `HEARTBEAT.md`

## Naturaleza bloqueante

La lectura de estos archivos es bloqueante.

Si cualquiera de los archivos anteriores existe pero no puede leerse completa y exitosamente, no continuar con trabajo operativo ni responder sobre:
- reglas;
- repositorios;
- perfiles;
- memoria operativa;
- configuraciones;
- decisiones previas;
- capacidades del agente.

Informar explícitamente falla de bootstrap.

## Regla de no sustitución

La presencia de contexto inyectado por runtime, mensajes anteriores, memoria parcial o inferencias no reemplaza estas lecturas obligatorias.

## Restricción operativa

No afirmar capacidades operativas sensibles ni tomar decisiones basadas en reglas, repositorios, perfiles o contexto persistente hasta completar esta secuencia de lectura obligatoria.

## Criterio de cumplimiento

El bootstrap solo se considera cumplido cuando la secuencia anterior fue leída completa, exitosamente y en el orden indicado.
```

### BOOTSTRAP.md
```md
Este archivo existe para reforzar el bootstrap operativo del agente en todo inicio de sesión, reinicio de contexto o ejecución equivalente, especialmente cuando OpenClaw inyecta este archivo como parte del contexto inicial.

## Instrucción obligatoria de bootstrap

Antes de cualquier respuesta sustantiva, verificar si existe `BOOT.md` en la raíz del workspace.

Si `BOOT.md` existe, su lectura es obligatoria, completa, exitosa y bloqueante. Luego de leer `BOOT.md`, cumplir estrictamente la secuencia de lectura allí definida, en el mismo orden indicado, antes de continuar con cualquier trabajo operativo.

## Alcance de la obligación

Esta obligación aplica especialmente a:
- todo inicio de sesión;
- todo reinicio de contexto;
- todo comando equivalente a `/new`;
- todo comando equivalente a `/reset`;
- toda situación en que este archivo haya sido inyectado como contexto de arranque;
- todo arranque general del sistema en el que `BOOT.md` sea ejecutado por hooks o automatizaciones del runtime.

## Regla de no sustitución

La presencia de contexto inyectado por runtime, memoria diaria, mensajes anteriores, conocimiento inferido o lecturas parciales no reemplaza la lectura obligatoria de `BOOT.md` ni de los archivos que este declare.

Tampoco debe asumirse que el bootstrap quedó cumplido por el solo hecho de que existan o hayan sido inyectados archivos como `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `MEMORY.md` o similares.

## Regla de bloqueo

Si `BOOT.md` existe pero no puede leerse completa y exitosamente, o si cualquiera de los archivos obligatorios definidos por `BOOT.md` existe pero no puede leerse completa y exitosamente, no continuar con trabajo operativo ni responder como si el bootstrap estuviera completo.

En ese caso, informar explícitamente una falla de bootstrap.

## Restricción de afirmaciones

Hasta completar la secuencia obligatoria definida en `BOOT.md`, no afirmar ni usar como base confiable:
- reglas operativas;
- repositorios vigentes;
- perfiles de base de datos;
- memoria operativa;
- decisiones previas;
- configuraciones persistentes;
- capacidades sensibles del agente.

## Criterio de continuación

Solo después de completar de forma exitosa la lectura obligatoria de `BOOT.md` y de toda su secuencia declarada, se permite continuar con respuestas sustantivas y trabajo operativo normal.
```
