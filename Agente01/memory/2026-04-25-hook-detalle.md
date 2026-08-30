# Session: 2026-04-25 21:33:28 UTC

- **Session Key**: agent:main:main
- **Session ID**: e9ab7541-1cf8-4545-831f-aea2d54a8d02
- **Source**: webchat

## Conversation Summary

user: System (untrusted): [2026-04-25 21:06:47 UTC] Exec failed (neat-sag, signal SIGTERM) :: meout\":30}"}],"api":"openai-codex-responses","provider":"openai-codex","model":"gpt-5.4","usage":{"input":35991,"output":254,"cacheRead":21376,"cacheWrite":0,"totalTokens":57621,…

Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:08 UTC] quiero entender como funciona el hook y su creacion en detalle
assistant: Funciona así, en detalle:

### 1. Qué es `boot-md`
Es un hook interno bundled de OpenClaw.

Archivo descriptivo:
- `/home/luispicone/.npm-global/lib/node_modules/openclaw/dist/bundled/boot-md/HOOK.md`

Ahí dice:
- nombre: `boot-md`
- evento: `gateway:startup`
- propósito: ejecutar `BOOT.md` al arrancar el gateway, para cada scope de agente configurado

### 2. Dónde vive la implementación
Handler:
- `/home/luispicone/.npm-global/lib/node_modules/openclaw/dist/bundled/boot-md/handler.js`

### 3. Cuándo se dispara
Se ejecuta solo en el evento de arranque del gateway.

La condición está acá:
```js
if (!isGatewayStartupEvent(event)) return;
```

O sea, no corre por mensaje, ni por sesión nueva, ni por cada turno. Corre en startup del gateway.

### 4. Cómo decide qué workspaces revisar
El handler obtiene los agentes configurados:

```js
const agentIds = listAgentIds(cfg);
```

Luego, para cada agente resuelve su workspace:

```js
const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
```

Después intenta correr `BOOT.md` en ese workspace.

### 5. Qué archivo busca
Busca exactamente:

```js
const BOOT_FILENAME = "BOOT.md";
```

Y lo carga con:

```js
const bootPath = path.join(workspaceDir, BOOT_FILENAME);
```

Si no existe:
- `status: "missing"` → se saltea

Si existe pero está vacío:
- `status: "empty"` → se saltea

### 6. Cómo ejecuta el contenido
No interpreta `BOOT.md` como código del sistema. Lo transforma en un prompt para el agente.

Construye este prompt:

```js
"You are running a boot check. Follow BOOT.md instructions exactly."
...
"BOOT.md:"
<contenido de BOOT.md>
...
"If BOOT.md asks you to send a message, use the message tool..."
...
"If nothing needs attention, reply with ONLY: NO_REPLY"
```

O sea:
- lee el markdown
- lo incrusta como instrucciones
- lanza una corrida interna del agente

### 7. Cómo invoca al agente
Genera un `sessionId` especial tipo boot:

```js
boot-<timestamp>-<uuid>
```

Y luego llama:

```js
await agentCommand({
  message,
  sessionKey,
  sessionId,
  deliver: false,
  senderIsOwner: true
}, bootRuntime, params.deps);
```

Puntos clave:
- `deliver: false`: no entrega esa corrida como mensaje visible al usuario
- `senderIsOwner: true`: la ejecución se trata como interna/propietaria
- usa la sesión main del agente, pero con resguardo/restauración del mapping

### 8. Qué hace con la sesión
Antes de correr el boot:
- hace snapshot del mapping de la main session store

Después:
- lo restaura

Eso evita que la ejecución bootstrap deje contaminado el mapeo normal de la sesión principal.

### 9. Qué pasa si falla
Si falla la lectura de `BOOT.md`:
- loguea error

Si falla la corrida del agente:
- loguea `boot-md failed for agent startup run`

Si no hay `BOOT.md` o está vacío:
- no falla, simplemente lo omite

### 10. Cómo se “crea” este hook
No está creado por tu `openclaw.json`. Ya viene bundled dentro de OpenClaw.

Tu config solo lo habilita:

```json
"hooks": {
  "internal": {
    "enabled": true,
    "entries": {
      "boot-md": {
        "enabled": true
      }
    }
  }
}
```

O sea:
- la creación real está en el código instalado de OpenClaw
- `openclaw.json` solo activa o desactiva esa entrada

### 11. Conclusión importante
`boot-md`:
- sí ejecuta `BOOT.md`
- pero lo hace en `gateway startup`
- no garantiza por sí mismo que en cada sesión nueva se inyecten todos los archivos del bootstrap
- es una corrida interna de arranque, no un mecanismo automático por mensaje

Si querés, te muestro ahora el flujo exacto desde `openclaw.json` hasta `agentCommand`, paso por paso, con los fragmentos de código relevantes.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:12 UTC] como se puede modificar esta parte para que aparte de que se ejecute en el inicio del gateway, tambien se ejecute cuando se hace un /new por ejemplo

3. Cuándo se dispara
Se ejecuta solo en el evento de arranque del gateway.

La condición está acá:

Copy
if (!isGatewayStartupEvent(event)) return;
assistant: Sí, se puede. La forma más limpia es extender `boot-md` para que también escuche los eventos internos `command:new` y `command:reset`, no solo `gateway:startup`.

## Evidencia base

OpenClaw ya emite hooks internos específicos para `/new` y `/reset`.

En `commands-reset-hooks-6u0bgkV_.js`:
```js
const hookEvent = createInternalHookEvent("command", params.action, params.sessionKey ?? "", {
  sessionEntry: params.sessionEntry,
  previousSessionEntry: params.previousSessionEntry,
  commandSource: params.command.surface,
  senderId: params.command.senderId,
  workspaceDir: params.workspaceDir,
  cfg: params.cfg
});
await triggerInternalHook(hookEvent);
```

Y en `session-reset-service-CtEfNV5U.js` también dispara:
```js
await triggerInternalHook(createInternalHookEvent("command", params.reason, target.canonicalKey ?? params.key, {
  sessionEntry: entry,
  previousSessionEntry: entry,
  commandSource: params.commandSource,
  cfg,
  workspaceDir
}));
```

O sea, `/new` y `/reset` ya generan eventos `command:new` y `command:reset`.

---

## Opción recomendada

Modificar el handler de `boot-md` para aceptar:

- `gateway:startup`
- `command:new`
- `command:reset`

### Cambio conceptual
Hoy tenés esto:
```js
if (!isGatewayStartupEvent(event)) return;
```

Lo reemplazarías por una condición más amplia, por ejemplo:
```js
const isBootTrigger =
  isGatewayStartupEvent(event) ||
  (event.type === "command" && (event.action === "new" || event.action === "reset"));

if (!isBootTrigger) return;
```

---

## Qué más hay que adaptar

En startup el código recorre todos los agentes:

```js
const agentIds = listAgentIds(cfg);
for (const agentId of agentIds) {
  const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
  await runBootOnce({ cfg, deps, workspaceDir, agentId });
}
```

Eso tiene sentido para arranque global del gateway.

Pero para `/new` o `/reset` no conviene correrlo para todos los agentes. Conviene correrlo solo para el agente/sesión afectada por ese comando.

### Lógica sugerida
- Si el evento es `gateway:startup`, mantener el comportamiento actual.
- Si el evento es `command:new` o `command:reset`, usar:
  - `event.sessionKey`
  - `event.context.workspaceDir`
  - el `agentId` derivado de `sessionKey`

---

## Implementación sugerida

### 1. Agregar helpers de detección
Podés hacerlo dentro del mismo handler:

```js
function isCommandResetLikeEvent(event) {
  return event?.type === "command" && (event?.action === "new" || event?.action === "reset");
}
```

### 2. Reescribir `runBootChecklist`
Quedaría conceptualmente así:

```js
const runBootChecklist = async (event) => {
  const deps = event.context?.deps ?? createDefaultDeps();
  const cfg = event.context?.cfg;
  if (!cfg) return;

  if (isGatewayStartupEvent(event)) {
    const agentIds = listAgentIds(cfg);
    for (const agentId of agentIds) {
      const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
      await runBootOnce({ cfg, deps, workspaceDir, agentId });
    }
    return;
  }

  if (event.type === "command" && (event.action === "new" || event.action === "reset")) {
    const sessionKey = event.sessionKey;
    const workspaceDir = event.context?.workspaceDir;
    const agentId = sessionKey ? resolveAgentIdFromSessionKey(sessionKey) : undefined;

    if (!workspaceDir) return;

    await runBootOnce({
      cfg,
      deps,
      workspaceDir,
      agentId
    });
  }
};
```

---

## Limitación importante
Esto **no** inyecta automáticamente archivos en el primer turno de `/new`. Lo que hace es ejecutar `BOOT.md` como corrida interna adicional cuando ocurre `/new` o `/reset`, igual que en startup.

Si lo que querés es que el bootstrap quede reflejado en el contexto inicial visible de esa nueva sesión, entonces hay dos caminos distintos:

### A. Hook adicional al evento `/new`
- más simple
- reutiliza `BOOT.md`
- corre como proceso interno
- no garantiza inyección textual del bootstrap en el prompt inicial del primer mensaje

### B. Integrarlo al pipeline de startup context / bootstrap files
- más correcto para “nueva sesión”
- más invasivo
- requiere tocar el mecanismo que arma el contexto inicial de `/new`

---

## Mi recomendación técnica
Si querés un cambio mínimo y seguro: **Opción A**.  
Si querés comportamiento realmente consistente con “cada sesión nueva debe bootstrapease”: **hay que intervenir el pipeline de bootstrap/context injection, no solo el hook**.

## Dónde tocar
Archivo principal:
- `/home/luispicone/.npm-global/lib/node_modules/openclaw/dist/bundled/boot-md/handler.js`

Y si querés hacerlo bien desde fuente TypeScript, habría que ubicar el source equivalente:
- `src/hooks/bundled/boot-md/handler.ts`

## Resumen corto
Sí, se puede.  
El cambio sería:
1. dejar de escuchar solo `gateway:startup`
2. escuchar también `command:new` y `command:reset`
3. en esos casos ejecutar `runBootOnce` solo para la sesión/agente afectado

Si querés, te preparo el patch exacto sobre `handler.js` para que veas cómo quedaría.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:15 UTC] mostrame el cambio para opcion A, pero no lo hagas aun
assistant: Sí. Para la **Opción A**, el cambio mínimo sobre `handler.js` sería este.

## Estado actual
Hoy el handler arranca así:

```js
const runBootChecklist = async (event) => {
	if (!isGatewayStartupEvent(event)) return;
	if (!event.context.cfg) return;
	const cfg = event.context.cfg;
	const deps = event.context.deps ?? createDefaultDeps();
	const agentIds = listAgentIds(cfg);
	for (const agentId of agentIds) {
		const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
		const result = await runBootOnce({
			cfg,
			deps,
			workspaceDir,
			agentId
		});
		if (result.status === "failed") {
			log.warn("boot-md failed for agent startup run", {
				agentId,
				workspaceDir,
				reason: result.reason
			});
			continue;
		}
		if (result.status === "skipped") log.debug("boot-md skipped for agent startup run", {
			agentId,
			workspaceDir,
			reason: result.reason
		});
	}
};
```

---

## Cambio propuesto
Quedaría así:

```js
function isResetLikeCommandEvent(event) {
	return event?.type === "command" && (event?.action === "new" || event?.action === "reset");
}

const runBootChecklist = async (event) => {
	if (!event.context?.cfg) return;
	const cfg = event.context.cfg;
	const deps = event.context.deps ?? createDefaultDeps();

	if (isGatewayStartupEvent(event)) {
		const agentIds = listAgentIds(cfg);
		for (const agentId of agentIds) {
			const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
			const result = await runBootOnce({
				cfg,
				deps,
				workspaceDir,
				agentId
			});
			if (result.status === "failed") {
				log.warn("boot-md failed for agent startup run", {
					agentId,
					workspaceDir,
					reason: result.reason
				});
				continue;
			}
			if (result.status === "skipped") log.debug("boot-md skipped for agent startup run", {
				agentId,
				workspaceDir,
				reason: result.reason
			});
		}
		return;
	}

	if (!isResetLikeCommandEvent(event)) return;

	const sessionKey = typeof event.sessionKey === "string" ? event.sessionKey : "";
	const workspaceDir = typeof event.context.workspaceDir === "string" ? event.context.workspaceDir : "";
	const agentId = sessionKey ? resolveAgentIdFromSessionKey(sessionKey) : void 0;

	if (!workspaceDir) {
		log.debug("boot-md skipped for reset/new event without workspaceDir", {
			action: event.action,
			sessionKey
		});
		return;
	}

	const result = await runBootOnce({
		cfg,
		deps,
		workspaceDir,
		agentId
	});

	if (result.status === "failed") {
		log.warn("boot-md failed for command-triggered run", {
			action: event.action,
			agentId,
			sessionKey,
			workspaceDir,
			reason: result.reason
		});
		return;
	}

	if (result.status === "skipped") log.debug("boot-md skipped for command-triggered run", {
		action: event.action,
		agentId,
		sessionKey,
		workspaceDir,
		reason: result.reason
	});
};
```

---

## Import adicional necesario
Como `agentId` sale de la sesión, habría que agregar este import arriba:

### hoy
```js
import { u as resolveAgentIdFromSessionKey } from "../../session-key-Bh1lMwK5.js";
```

Ese import **ya está presente** en este archivo, así que para esta opción **no hace falta agregar nada más**.

---

## Qué hace exactamente este cambio
- conserva el comportamiento actual en `gateway:startup`
- agrega ejecución también para:
  - `command:new`
  - `command:reset`
- en esos casos:
  - no recorre todos los agentes
  - usa solo el `workspaceDir` del evento
  - deriva el `agentId` desde `sessionKey`
  - ejecuta un único `runBootOnce(...)`

---

## Riesgos / observaciones
1. **Puede correr dos veces** en algunos flujos de reset si OpenClaw dispara más de un punto de hook para el mismo comando.
2. **No inyecta contexto visible** en el primer mensaje de la nueva sesión. Solo ejecuta el boot internamente.
3. Si el comando trae `workspaceDir` vacío o inconsistente, el hook se omite.

---

## Fragmento tipo diff conceptual

```diff
+ function isResetLikeCommandEvent(event) {
+ 	return event?.type === "command" && (event?.action === "new" || event?.action === "reset");
+ }

  const runBootChecklist = async (event) => {
- 	if (!isGatewayStartupEvent(event)) return;
- 	if (!event.context.cfg) return;
+ 	if (!event.context?.cfg) return;
  	const cfg = event.context.cfg;
  	const deps = event.context.deps ?? createDefaultDeps();
- 	const agentIds = listAgentIds(cfg);
- 	for (const agentId of agentIds) {
- 		const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
- 		const result = await runBootOnce({
- 			cfg,
- 			deps,
- 			workspaceDir,
- 			agentId
- 		});
- 		...
- 	}
+
+ 	if (isGatewayStartupEvent(event)) {
+ 		const agentIds = listAgentIds(cfg);
+ 		for (const agentId of agentIds) {
+ 			const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
+ 			const result = await runBootOnce({
+ 				cfg,
+ 				deps,
+ 				workspaceDir,
+ 				agentId
+ 			});
+ 			...
+ 		}
+ 		return;
+ 	}
+
+ 	if (!isResetLikeCommandEvent(event)) return;
+
+ 	const sessionKey = typeof event.sessionKey === "string" ? event.sessionKey : "";
+ 	const workspaceDir = typeof event.context.workspaceDir === "string" ? event.context.workspaceDir : "";
+ 	const agentId = sessionKey ? resolveAgentIdFromSessionKey(sessionKey) : void 0;
+
+ 	if (!workspaceDir) return;
+
+ 	const result = await runBootOnce({
+ 		cfg,
+ 		deps,
+ 		workspaceDir,
+ 		agentId
+ 	});
+ 	...
  };
```

Archivos impactados si después decidís aplicarlo:
- `/home/luispicone/.npm-global/lib/node_modules/openclaw/dist/bundled/boot-md/handler.js`

Sin hacerlo aún, ese sería el cambio.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:20 UTC] si tengo que pedirle a un agente en otra instalacion de openclaw que ya tiene este hook para disparar solo en inicio de gateway y quiero que haga este cambio

como se lo pido?

tambien aplicaria para pedirtelo a vos luego
assistant: Pedíselo así, directo y sin ambigüedad:

> Quiero modificar el hook interno `boot-md` para que, además de ejecutarse en `gateway:startup`, también se ejecute cuando se dispare `/new` y `/reset`.  
> No quiero cambiar todavía el pipeline de inyección de contexto, solo la opción A: reutilizar el mismo `runBootOnce(...)` cuando lleguen eventos internos `command:new` y `command:reset`.  
>  
> Requisitos:
> 1. conservar intacto el comportamiento actual en `gateway:startup`
> 2. para `command:new` y `command:reset`, ejecutar `runBootOnce(...)` solo para la sesión/agente afectado, no para todos los agentes
> 3. tomar `workspaceDir` desde `event.context.workspaceDir`
> 4. derivar `agentId` desde `event.sessionKey`
> 5. si no hay `workspaceDir`, saltear y loguear en debug
> 6. mantener logs diferenciados entre startup y command-triggered run
> 7. mostrarme el diff antes de aplicarlo
> 8. no hagas otros cambios colaterales
>  
> Archivo a tocar:
> `/home/.../openclaw/dist/bundled/boot-md/handler.js`
>  
> Referencia de comportamiento esperada:
> - aceptar `gateway:startup`
> - aceptar también `command:new` y `command:reset`
> - en new/reset correr una sola vez para esa sesión
>  
> Antes de editar, leé el archivo y mostrame el patch propuesto.

Si querés una versión más corta:

> Modificá `boot-md` con opción A: además de `gateway:startup`, que escuche `command:new` y `command:reset`, y en esos casos ejecute `runBootOnce(...)` solo para la sesión afectada usando `event.context.workspaceDir` y `event.sessionKey`. Conservá intacto el comportamiento de startup y mostrame el diff antes de aplicar.

Sí, eso mismo también aplica para pedírmelo a mí luego.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:29 UTC] Quiero modificar el hook interno boot-md para que, además de ejecutarse en gateway:startup, también se ejecute cuando se dispare /new y /reset.
No quiero cambiar todavía el pipeline de inyección de contexto, solo la opción A: reutilizar el mismo runBootOnce(...) cuando lleguen eventos internos command:new y command:reset.

Requisitos:

conservar intacto el comportamiento actual en gateway:startup
para command:new y command:reset, ejecutar runBootOnce(...) solo para la sesión/agente afectado, no para todos los agentes
tomar workspaceDir desde event.context.workspaceDir
derivar agentId desde event.sessionKey
si no hay workspaceDir, saltear y loguear en debug
mantener logs diferenciados entre startup y command-triggered run
mostrarme el diff antes de aplicarlo
no hagas otros cambios colaterales
Archivo a tocar:
/home/.../openclaw/dist/bundled/boot-md/handler.js

Referencia de comportamiento esperada:

aceptar gateway:startup
aceptar también command:new y command:reset
en new/reset correr una sola vez para esa sesión
Antes de editar, leé el archivo y mostrame el patch propuesto.
assistant: Patch propuesto, sin aplicarlo:

```diff
--- a/dist/bundled/boot-md/handler.js
+++ b/dist/bundled/boot-md/handler.js
@@
 //#endregion
 //#region src/hooks/bundled/boot-md/handler.ts
 const log = createSubsystemLogger("hooks/boot-md");
+function isResetLikeCommandEvent(event) {
+	return event?.type === "command" && (event?.action === "new" || event?.action === "reset");
+}
 const runBootChecklist = async (event) => {
-	if (!isGatewayStartupEvent(event)) return;
-	if (!event.context.cfg) return;
+	if (!event.context?.cfg) return;
 	const cfg = event.context.cfg;
 	const deps = event.context.deps ?? createDefaultDeps();
-	const agentIds = listAgentIds(cfg);
-	for (const agentId of agentIds) {
-		const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
-		const result = await runBootOnce({
-			cfg,
-			deps,
-			workspaceDir,
-			agentId
-		});
-		if (result.status === "failed") {
-			log.warn("boot-md failed for agent startup run", {
-				agentId,
-				workspaceDir,
-				reason: result.reason
-			});
-			continue;
-		}
-		if (result.status === "skipped") log.debug("boot-md skipped for agent startup run", {
-			agentId,
-			workspaceDir,
-			reason: result.reason
-		});
+	if (isGatewayStartupEvent(event)) {
+		const agentIds = listAgentIds(cfg);
+		for (const agentId of agentIds) {
+			const workspaceDir = resolveAgentWorkspaceDir(cfg, agentId);
+			const result = await runBootOnce({
+				cfg,
+				deps,
+				workspaceDir,
+				agentId
+			});
+			if (result.status === "failed") {
+				log.warn("boot-md failed for agent startup run", {
+					agentId,
+					workspaceDir,
+					reason: result.reason
+				});
+				continue;
+			}
+			if (result.status === "skipped") log.debug("boot-md skipped for agent startup run", {
+				agentId,
+				workspaceDir,
+				reason: result.reason
+			});
+		}
+		return;
 	}
+
+	if (!isResetLikeCommandEvent(event)) return;
+	const sessionKey = typeof event.sessionKey === "string" ? event.sessionKey : "";
+	const workspaceDir = typeof event.context.workspaceDir === "string" ? event.context.workspaceDir : "";
+	const agentId = sessionKey ? resolveAgentIdFromSessionKey(sessionKey) : void 0;
+	if (!workspaceDir) {
+		log.debug("boot-md skipped for reset/new event without workspaceDir", {
+			action: event.action,
+			sessionKey
+		});
+		return;
+	}
+	const result = await runBootOnce({
+		cfg,
+		deps,
+		workspaceDir,
+		agentId
+	});
+	if (result.status === "failed") {
+		log.warn("boot-md failed for command-triggered run", {
+			action: event.action,
+			agentId,
+			sessionKey,
+			workspaceDir,
+			reason: result.reason
+		});
+		return;
+	}
+	if (result.status === "skipped") log.debug("boot-md skipped for command-triggered run", {
+		action: event.action,
+		agentId,
+		sessionKey,
+		workspaceDir,
+		reason: result.reason
+	});
 };
 //#endregion
 export { runBootChecklist as default };
```

Observación técnica: no requiere imports nuevos, porque `resolveAgentIdFromSessionKey` ya está importado en ese archivo.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:30 UTC] aplicalo
assistant: Aplicado.

Archivo impactado:
- `/home/luispicone/.npm-global/lib/node_modules/openclaw/dist/bundled/boot-md/handler.js`

Qué cambió:
- mantiene intacto `gateway:startup`
- agrega soporte para `command:new` y `command:reset`
- en esos eventos corre `runBootOnce(...)` solo para la sesión afectada
- toma `workspaceDir` desde `event.context.workspaceDir`
- deriva `agentId` desde `event.sessionKey`
- si falta `workspaceDir`, hace skip con log debug
- separa logs entre startup y command-triggered run

Riesgo:
- es un cambio directo sobre `dist/`, así que puede perderse en una reinstalación o actualización de OpenClaw

Validación ejecutada:
- validé lectura previa del bloque real y apliqué un cambio único, acotado, sin tocar otras áreas.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Sat 2026-04-25 21:31 UTC] reinicia el gateway
user: You are running a boot check. Follow BOOT.md instructions exactly.

BOOT.md:
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

If BOOT.md asks you to send a message, use the message tool (action=send with channel + target).
Use the `target` field (not `to`) for message tool destinations.
After sending with the message tool, reply with ONLY: NO_REPLY.
If nothing needs attention, reply with ONLY: NO_REPLY.
assistant: NO_REPLY
