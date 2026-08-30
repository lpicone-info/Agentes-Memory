# Session: 2026-04-21 18:37:29 UTC

- **Session Key**: agent:main:main
- **Session ID**: 3ddfb321-8b39-459d-8fd6-47fba936fa70
- **Source**: webchat

## Conversation Summary

user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Tue 2026-04-21 18:30 UTC] esto no es bueno
El archivo ya tenía dos reglas numeradas como Regla 21, no lo corregí porque no me lo pediste.

reenumera y mostrame todas reglas con su titulo
assistant: Voy a reenumerar `REGLAS.md` de forma consistente y después te muestro el listado completo de títulos.
assistant: Reenumerado. Quedó así:

1. Regla 1 - Búsqueda robusta de texto en repositorios
2. Regla 2 - Estructura documental obligatoria por proyecto
3. Regla 3 - Verificación previa antes de afirmar inexistencia
4. Regla 4 - Carga obligatoria de perfiles de base de datos
5. Regla 5 - Prohibición de actuar sobre supuestos
6. Regla 6 - Respuesta estrictamente acotada al pedido humano
7. Regla 7 - Manejo realista de adjuntos y limitaciones del canal
8. Regla 8 - Cambios de configuración solo con evidencia y validación previa
9. Regla 9 - Validación contextual de identificadores operativos
10. Regla 10 - Criterio de vigencia para registros con baja_fecha
11. Regla 11 - Confirmación reforzada para acciones destructivas
12. Regla 12 - Lectura obligatoria antes de editar
13. Regla 13 - Cambios mínimos, auditables y por etapas
14. Regla 14 - Validación antes y después de cambios
15. Regla 15 - Entregables técnicos obligatorios
16. Regla 16 - Separación entre evidencia, hipótesis y recomendación
17. Regla 17 - Verificación de contexto antes de proponer o concluir
18. Regla 18 - Documentación funcional orientada al estado vigente
19. Regla 19 - Alta controlada de nuevas reglas operativas
20. Regla 20 - Verificación previa de repositorios contra REPOSITORIOS.md
21. Regla 21 - Persistencia y publicación solo por pedido explícito
22. Regla 22 - Actualizaciones solo por consola y nunca sugeridas por chat
23. Regla 23 - Alta controlada de entradas en REPOSITORIOS.md

Archivo impactado:
- `/home/luispicone/.openclaw/workspace/REGLAS.md`

Validación ejecutada:
- lectura completa posterior a la edición y control de numeración secuencial 1..23
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Tue 2026-04-21 18:32 UTC] quiero dar de alta un nuevo repositorio en github
assistant: Necesito estos datos para darlo de alta y registrarlo correctamente:

1. nombre lógico de referencia
2. ruta local completa
3. remoto Git del nuevo repo en GitHub
4. propósito
5. stack principal

Y además confirmame el punto operativo:
- el repo local ya existe
o
- querés que lo clone yo en esa ruta
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Tue 2026-04-21 18:34 UTC] acabamos de generar una regla para eso y no la seguiste
como hacemos para que siempre que te pidan el alta de un nuevo repositorio lo hagas basado en la regla?
assistant: Hay que agregar otra regla, más específica, para el disparador del caso.

La regla 23 define **qué datos pedir** al cargar una entrada en `REPOSITORIOS.md`, pero no obliga explícitamente a que, ante frases como “dar de alta un nuevo repositorio”, yo deba ir primero a esa regla y usarla como procedimiento.

Propuesta:

## Regla 24 - Alta de repositorios siempre regida por REPOSITORIOS.md
Cuando un humano pida dar de alta, agregar, conectar, clonar, registrar o incorporar un repositorio nuevo, tratar ese pedido automáticamente como un alta de entrada en `REPOSITORIOS.md` y aplicar sin excepción la `Regla 23` antes de continuar. No improvisar listas de datos distintas ni omitir campos definidos por esa regla. El relevamiento inicial del alta debe basarse en esa regla y la ejecución posterior debe completar únicamente lo que pueda verificarse con evidencia objetiva del entorno.

Si la aprobás, la agrego.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Tue 2026-04-21 18:34 UTC] no puede quedar todo en la misma regla?
assistant: Sí, puede y es mejor.

Conviene reemplazar la regla 23 por una versión más completa, que incluya tanto:
- el disparador del caso
- como los datos a solicitar
- y el modo de completar lo verificable

Versión propuesta:

## Regla 23 - Alta de repositorios regida por REPOSITORIOS.md
Cuando un humano pida dar de alta, agregar, conectar, clonar, registrar o incorporar un repositorio nuevo, tratar ese pedido automáticamente como un alta de entrada en `REPOSITORIOS.md`. Antes de continuar, solicitar explícitamente al humano estos datos: nombre lógico de referencia, ruta local completa, remoto Git, propósito y stack principal. Luego verificar en el entorno la ruta indicada y completar la entrada usando la misma estructura del archivo, determinando con evidencia objetiva los campos restantes: proveedor remoto, estado de referencia, configuración git local (`user.name` y `user.email`) y notas operativas. Si la ruta local no existe o el repositorio todavía no fue clonado, dejarlo expresamente documentado en la entrada y no registrar como verificados datos que no hayan sido validados en el entorno. No improvisar listas de datos distintas ni omitir este procedimiento.

Si querés, reemplazo la regla 23 actual por esta versión.
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Tue 2026-04-21 18:35 UTC] dale
assistant: Actualizo la regla 23 con la versión consolidada y verifico cómo quedó.
assistant: La lectura por offset falló porque el archivo es más corto de lo esperado. Leo el tramo final correctamente.
assistant: Hecho.

La `Regla 23` fue reemplazada por la versión consolidada en:
- `/home/luispicone/.openclaw/workspace/REGLAS.md`

Texto vigente del título:
- `Regla 23 - Alta de repositorios regida por REPOSITORIOS.md`

Validación ejecutada:
- lectura posterior del bloque final del archivo y verificación de la redacción actualizada
user: Sender (untrusted metadata):
```json
{
  "label": "openclaw-control-ui",
  "id": "openclaw-control-ui"
}
```

[Tue 2026-04-21 18:37 UTC] quiero dar de alta un nuevo repositorio de github
assistant: Necesito estos datos:

1. nombre lógico de referencia
2. ruta local completa
3. remoto Git
4. propósito
5. stack principal
