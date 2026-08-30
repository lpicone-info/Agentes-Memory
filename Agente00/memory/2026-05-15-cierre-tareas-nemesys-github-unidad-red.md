# 2026-05-15 - Cierre operativo: tareas NemeSys, GitHub y unidad de red

Resumen persistente de la jornada con Luis.

## Lista de tareas de NemeSys

Se creo y ordeno la gestion de tareas de NemeSys en una carpeta documental llamada `tareas_nemesys`.

La grilla principal quedo como `TAREAS.md` y se estructuro con columnas:

- ID
- Tarea
- Estado
- Avance
- Fecha de comienzo
- Fecha de finalizacion
- Comentarios

Estado relevante al cierre:

- Tarea 1: `Terminar Onboarding con Agente IA de Belkis`, en curso, avance 80%.
- Tarea 2: `Implementar uso de Mantis en agentes`, pendiente, 0%.
- Tarea 3: `Montar unidad de red en agente`, analisis en curso, 5%.
- Tarea 4: `Verificar como un agente ve un video de una reunion y lo documenta`, analisis en curso, 5%.
- Tarea 5: `Armar documentacion tecnica Agentes de Infomedical`, pendiente, 0%.
- Tarea 6: `Armar manual de usuarios Agentes de Infomedical`, pendiente, 0%.
- Tarea 7: `Conectar a NemeSys a su Google Drive`, analisis en curso, 5%.
- Tarea 8: `Conectar a NemeSys a su e-mail de Infomedical`, analisis en curso, 5%.

## Analisis documentados

Se lanzaron subagentes para investigar y documentar:

### Tarea 7 - Google Drive

Documento: `tareas_nemesys/tarea-7-google-drive.md`.

Conclusiones principales:

- Recomendado: Service Account con carpeta de Drive compartida explicitamente.
- Evitar cuenta personal y scopes amplios.
- Falta definir proyecto/cuenta Google Cloud, carpeta objetivo, permisos y mecanismo seguro de credenciales.

### Tarea 8 - E-mail Infomedical

Documento: `tareas_nemesys/tarea-8-email-infomedical.md`.

Conclusiones principales:

- El correo de Infomedical apunta a Google Workspace.
- Recomendado: Gmail API con OAuth y scopes minimos.
- Falta confirmacion de IT sobre el metodo autorizado.

### Tarea 3 - Unidad de red Windows

Documento de analisis: `tareas_nemesys/tarea-3-unidad-red-windows.md`.

Conclusiones principales:

- Recomendado: montar recurso SMB/CIFS desde Linux.
- Priorizar SMB 3.x.
- No exponer password en comandos, chat, repo ni documentacion.
- Usar archivo de credenciales protegido del sistema si se implementa.
- Definir IP/host, recurso compartido, usuario/dominio, punto de montaje, permisos y tipo de persistencia.

### Tarea 4 - Video de reunion a documentacion

Documento: `tareas_nemesys/tarea-4-video-reunion-documentacion.md`.

Conclusiones principales:

- Recomendado: pipeline autorizado con ingreso de link/archivo, descarga autorizada, extraccion de audio, transcripcion, diarizacion opcional, extraccion de frames, OCR, analisis visual y documentacion Markdown accionable.
- Debe separar evidencia, inferencias, dudas y recomendaciones.
- Requiere consentimiento y acceso legitimo al video.

## Repositorio GitHub de NemeSys

Luis pidio conectar a NemeSys con un repositorio GitHub propio.

Se genero una clave SSH dedicada para GitHub y Luis incorporo la clave publica en GitHub.

Luego se uso la skill `git-clone` para clonar:

`git@github.com:lpicone-info/NemeSys.git`

El repo quedo clonado y validado como:

`~/.openclaw/workspace/git/lpicone-info-NemeSys`

Identidad Git local configurada:

- `user.name`: `NemeSys`
- `user.email`: `agente00_ia@infomedical.com.ar`

Se registro el repo en `REPOSITORIOS.md`.

## Movimiento de tareas al repo

La carpeta `tareas_nemesys` fue movida al repositorio `lpicone-info-NemeSys`.

Se hizo commit y push a `origin/main` con mensaje:

`Agregar gestion de tareas de NemeSys`

Commit:

`c7a0c41`

Archivos subidos:

- `tareas_nemesys/TAREAS.md`
- `tareas_nemesys/tarea-3-unidad-red-windows.md`
- `tareas_nemesys/tarea-4-video-reunion-documentacion.md`
- `tareas_nemesys/tarea-7-google-drive.md`
- `tareas_nemesys/tarea-8-email-infomedical.md`

## Inicio de implementacion de la tarea 3

Luis pidio avanzar con la tarea 3 paso a paso, con confirmacion antes de cada paso, hasta dejar conectada y persistida una unidad de red Windows en el entorno de NemeSys.

Se creo una bitacora de implementacion:

`tareas_nemesys/tarea-3-implementacion-montaje-red.md`

Regla acordada para esta implementacion:

- un paso por vez;
- documentar antes de avanzar;
- pedir confirmacion humana para cada paso;
- no instalar paquetes, crear credenciales, montar ni persistir configuracion sin confirmacion explicita.

## Pausa por dudas de seguridad y conceptos

Luis pidio pausar antes de seguir y planteo dudas sobre:

### Usuario autorizado / dominio / tipo de usuario

Duda: donde quedarian persistidos si los pasa por chat.

Criterio aclarado:

- usuario, dominio/workgroup y tipo de usuario pueden documentarse como datos operativos no secretos si Luis lo autoriza;
- la password no debe pasarse por chat ni quedar documentada;
- si hace falta password, debe quedar en un archivo protegido del sistema, fuera del repo, con permisos restrictivos y sin exponer el valor.

### Punto de montaje local

Duda: Luis no entendia que era.

Criterio aclarado:

- es la carpeta local Linux donde aparecera el recurso compartido Windows;
- ejemplo conceptual: `\\WINDOWS-PC\Compartido` podria montarse como `/mnt/windows-compartido`.

### Usuario Linux que debe acceder

Luis aclaro que el acceso es para el agente.

Criterio aclarado:

- se debe mapear el montaje al usuario Linux efectivo bajo el que corre NemeSys;
- ese dato puede validarlo NemeSys al retomar la implementacion.

## Estado exacto al cierre

- La implementacion de la tarea 3 quedo pausada en Paso 2.
- No se recibio password.
- No se creo archivo de credenciales.
- No se instalaron paquetes.
- No se probo conectividad SMB.
- No se monto la unidad.
- No se modifico configuracion persistente del sistema.
- La bitacora local fue actualizada con las dudas.
- `TAREAS.md` fue actualizado localmente para referenciar la bitacora y la pausa.
- Quedan cambios locales sin commit/push posteriores al commit `c7a0c41`.

## Proximo paso al retomar

Retomar tarea 3 desde Paso 2:

1. decidir si usuario/dominio se documentan o no;
2. definir punto de montaje local;
3. validar usuario Linux efectivo del agente;
4. definir mecanismo seguro para ingresar/persistir la password sin exponerla;
5. recien despues pedir confirmacion para pruebas de conectividad SMB.
