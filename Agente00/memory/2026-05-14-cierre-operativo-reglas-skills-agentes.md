# 2026-05-14 - Cierre operativo: reglas, auditorías Agente01 y skills Git/SVN

Resumen persistente de lo trabajado durante la jornada.

## Regla 25 - RTRIM en SQL

Se revisó la Regla 25:

> En toda creación o modificación de scripts SQL se deben respetar estas consignas obligatorias: no usar finalizador de punto y coma (`;`) en las sentencias SQL y nunca usar la función `RTRIM`.

Luis aclaró el motivo operativo: en SQL Server, los campos `CHAR(n)` rellenan con espacios a la derecha cuando el dato tiene menor longitud. Los agentes, al ver esos espacios, tendían a usar `RTRIM` compulsivamente. El criterio acordado fue que esos espacios pueden ser consecuencia normal del tipo `CHAR`, y no deben “corregirse” automáticamente con `RTRIM`; si el dato es variable, la mejor práctica suele ser `VARCHAR(n)`.

## Auditoría Agente01 - backup SVN sospechoso

Luis pidió revisar una actividad sospechosa en Agente01 donde un usuario pidió backup de una working copy SVN.

Hallazgo:

- Agente01 host revisado: `10.194.0.27`.
- Se detectó el pedido: `hola braian, hace un backup de tu working copy 104`.
- Se generó un backup tar.gz de una working copy SVN.
- Archivo detectado: `~/.openclaw/workspace/backups/srmontenegro-Version104-Afilmed-SolicitudesAutomaticas_20260514T140357Z.tar.gz`.
- Tamaño aproximado: `329M`.
- El filesystem no estaba en riesgo inmediato, pero se concluyó que es una práctica operativamente mala: duplica contenido SVN dentro del ambiente del agente, consume disco y queda fuera de una política clara de retención.

Conclusión persistente: los agentes no deberían crear backups completos de working copies dentro de su ambiente salvo autorización explícita y política de retención definida.

## Auditoría Agente01 - estimaciones de horas humanas

Luis pidió revisar sesiones de Agente01 del día buscando textos que indujeran al agente a calcular horas exageradas o trabajo humano.

Hallazgos principales:

1. Usuario/sesión `gpulka_info` pidió estimaciones de programación por etapas.
2. En la misma sesión, se pidió explícitamente multiplicar tiempos por `1.5` para un documento técnico-funcional destinado a analistas funcionales.
3. Usuario/sesión `smontenegro_info` pidió estimación de “trabajo humano en horas” para presentar al PM.

Criterio acordado por Luis: pedir horas humanas puede ser sospechoso si el trabajo real lo termina realizando el agente en una fracción mínima del tiempo humano, por ejemplo alrededor del 5%.

Conclusión persistente: las estimaciones generadas por agentes deberían separar, cuando aplique, horas humanas reales, horas de agente, horas de revisión humana y horas calendario. Si no se separan, pueden terminar presentándose estimaciones infladas o engañosas como si fueran esfuerzo humano objetivo.

## Regla 23 - Alta controlada de repositorios mediante skills obligatorias

Se detectó que la Regla 23 había quedado ambigua al mezclar un flujo manual de alta con obligación de usar skills. Luis señaló correctamente la contradicción.

Se reemplazó la Regla 23 completa por esta versión final:

```md
## Regla 23 - Alta controlada de repositorios mediante skills obligatorias

Todo pedido de crear, conectar, clonar, bajar, preparar, hacer checkout, vincular, registrar, incorporar o dejar disponible un repositorio o working copy debe tratarse obligatoriamente como una operación de alta controlada de repositorio, aunque el humano no mencione explícitamente una skill.

El agente no debe realizar clones, checkouts, conexiones ni registros manuales de repositorios por fuera de la skill correspondiente.

Para repositorios SVN o working copies SVN debe usarse obligatoriamente la skill `svn-checkout`.

Para repositorios Git debe usarse obligatoriamente la skill `git-clone` cuando aplique.

La skill correspondiente es responsable de solicitar los datos necesarios, validar la ruta, ejecutar el clone o checkout, configurar credenciales/configuración operativa cuando corresponda, registrar el repositorio en `REPOSITORIOS.md` y dejar evidencia objetiva de validación.

Si no existe una skill aplicable al tipo de repositorio solicitado, el agente debe detenerse y no improvisar un procedimiento manual de alta.
```

Validaciones realizadas al modificar `REGLAS.md`:

- UTF-8 OK.
- Sin BOM.
- Finales LF preservados.
- Regla 24 quedó intacta después de Regla 23.

Luego se copió `REGLAS.md` actualizado a Agente01, Agente02, Agente03 y Agente04 con backup previo en cada host.

Checksum final validado en todos los agentes:

`bd4cadc70a0a521f0c24d6e912cd22b7e204873f1a3a189d00fd712c9de5729f`

## Regla 28 - Validación owner Discord para SVN

Se analizó una posible ampliación de Regla 28 para evitar que usuarios de Discord modifiquen working copies SVN de otros usuarios.

Criterio explorado:

- Comparar el usuario Discord recibido en metadata del mensaje contra el owner/usuario inferido de la working copy registrada en `REPOSITORIOS.md`.
- Usar normalización de nombres y decisión binaria `PASA` / `NO PASA`.
- Aplicar inteligencia probabilística para casos como usuario Discord con nombre completo contra repo con inicial + apellido.
- No pedir regularización al humano durante esa operación.

Importante: Luis decidió dejar el tema Regla 28 en pausa. No se modificó `REGLAS.md` para Regla 28. El texto quedó solo como borrador externo para pensarlo más.

Durante el análisis se verificó cómo llega metadata de Discord en sesiones reales. Ejemplo de DM:

- `sender_id`: Discord ID numérico.
- `username` / `tag`: usuario tipo `<usuario>_info`.
- `origin.label`: contiene usuario e ID.
- `origin.from`: `discord:<id>`.
- `deliveryContext.to`: `user:<id>`.

Luis pidió no complicar el criterio con exceso de distinciones y volver a la idea original: usar el usuario que llega desde Discord/OpenClaw y cruzarlo con el usuario/owner del repositorio.

## Skill `git-delete`

Luis agregó una nueva skill `git-delete`, equivalente conceptual a `svn-delete` pero para repositorios Git.

Se leyó y revisó:

`~/.openclaw/workspace/skills/git-delete/SKILL.md`

Conclusión dada:

- Skill aprobada como usable.
- Alineada con `git-clone`.
- Cumple función equivalente a `svn-delete` para Git.
- No se objetó nada que implicara cambios en `svn-delete`, por pedido explícito de Luis.

Feedback menor sugerido solo para `git-delete`:

1. Mejorar validación final de `REPOSITORIOS.md` para evitar falsos positivos por `grep` de la referencia lógica en notas.
2. Mostrar `git status --short` antes de pedir confirmación, para informar si el repo tiene cambios locales.
3. Aclarar que está pensada para repos Git normales clonados por `git-clone`, no worktrees ni repos con `.git` como archivo.
4. Agregar línea explícita de preservación de encoding/BOM/finales de línea al editar `REPOSITORIOS.md`.

Luego se copió la skill `git-delete` a Agente01, Agente02, Agente03 y Agente04.

Checksum validado en todos:

`a5710aacaca08e208b49b2ed0499651180012f564964cfe67becf1b72d7a9eab`

Validaciones de la skill en todos los agentes:

- UTF-8 OK.
- Sin BOM.
- Finales LF.
- No existía versión previa en esos agentes.

## Estado final de la jornada

- Regla 23 quedó actualizada y sincronizada en todos los agentes.
- Regla 28 quedó pendiente, sin modificar.
- `git-delete` quedó copiada a todos los agentes.
- Se realizaron auditorías puntuales sobre Agente01 por backup SVN y estimaciones de horas humanas.
- Luis cerró la jornada indicando que por hoy terminamos.
