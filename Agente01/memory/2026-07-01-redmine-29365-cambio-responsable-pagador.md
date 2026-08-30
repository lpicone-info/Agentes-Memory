# Memory - 2026-07-01 - Redmine 29365 cambio responsable pagador APP

## Contexto
- Interlocutor: Gabriel Pulka.
- Canal: Google Chat directo.
- Tema: Redmine `29365`, solicitudes automaticas APP para cambio de responsable pagador en Afilmed.
- Working copy SVN usada: `/home/luispicone/.openclaw/workspace/svn/gpulka-Version104-Afilmed-SolicitudesAutomaticas`.
- Rama SVN: `https://srv-infosvn.infomedical.com/svn/Coomeva/branches/Version104-Afilmed-SolicitudesAutomaticas`.
- Base usada para validaciones SQL y datos de ejemplo: `InstallQA_89`.

## Commits SVN realizados
- `r37243`: `Redmine 29365 - SOLI_AUTO cambio responsable pagador`.
- `r37244`: `Redmine 29365 - contempla RP en exportacion batch solicitudes`.
- `r37245`: `Redmine 29365 - normaliza finales de linea objetos SQL`.

## Implementacion principal - r37243
- Se agrego parser `afi_insertar_soli_auto_cambio_resp_pagador`.
- Se agrego dispatcher para `soli_moti = 22`.
- Se agregaron validaciones XML para cambio de responsable pagador.
- Se agrego staging `SOLI_AUTO_PARENTESCOS`.
- Se amplio `SOLI_AUTO_CONTRATO`.
- Se amplio `SOLI_AUTO_RESP_PAGADOR`.
- Se genero flujo GMS para transaccion `RP`.
- Se paso `moti_ret_resp_pag` por `GMSTXT_RESP_PAGADOR` y `GMSDEF_RESP_PAGADOR`.
- Se impacto parentescos antes de `afu_afi_resp_pagador`.
- Se contemplaron contactos RP con `tipo_reg/domi_tipo = R`, usando Registro Unico cuando existe.

## Objetos Power - r37244
- Gabriel pregunto si habia que tocar objetos Power, en especial el batch de solicitudes con DataWindows para exportar CSV.
- Se reviso `exe_afilmed/src/wp_main_solicitudes.srw`.
- Se agrego `CASE 'RP'` para usar el DataWindow existente `d_alta_mas_solis_generadas`.
- Sin este cambio, la generacion podia existir, pero la exportacion CSV caia en el `CASE ELSE` con mensaje de falta de DataObject de exportacion.
- Se reviso el batch de facturacion:
  - entra por `afs_soli_auto_app_fact_pendientes` y `afu_soli_auto_app_fact_rev_incluir`;
  - el flujo trabaja genericamente sobre solicitudes APP y `SOLI_AUTO_CONTRATO`;
  - no se detecto necesidad de agregar un case Power especifico para `soli_moti = 22`.

## Correccion tecnica - r37245
- Gabriel pidio revisar que paso con los objetos de base del commit `r37243`.
- Problema detectado:
  - varios objetos SQL quedaron con finales de linea mezclados `CRLF + LF`;
  - los dos archivos nuevos quedaron solo `LF`;
  - esto incumplio la regla operativa de preservacion de encoding, BOM y finales de linea.
- Correccion aplicada:
  - se normalizaron los 13 objetos de base impactados por `r37243` a `CRLF`;
  - no se cambio contenido SQL ni propiedades SVN.
- Validaciones de la correccion:
  - los 13 archivos quedaron `bom=no`, `lf=0`, `cr=0`, solo `CRLF`;
  - comparacion contra BASE SVN ignorando EOL dio contenido identico;
  - la working copy quedo sin modificaciones versionadas pendientes, salvo `.docx` no versionados y externos SVN previos.

## Regla incumplida y aprendizaje operativo
- Gabriel marco que ya existia una regla sobre encoding/BOM/finales de linea.
- Regla aplicable: `REGLAS.md`, Regla 26.
- Incumplimiento reconocido:
  - en `r37243` se valido sintaxis SQL y logica funcional, pero no se hizo la validacion tecnica obligatoria de EOL/encoding antes del commit;
  - al crear/editar objetos SQL nuevos se asumio el formato por defecto de la herramienta en vez de tomar la convencion objetiva del directorio.
- Criterio obligatorio para futuros cambios:
  - antes de editar y antes de commitear objetos SQL, PowerBuilder o recursos textuales, verificar y reportar BOM, encoding y finales de linea;
  - si hay cambio no solicitado o mezcla nueva de EOL, detener el commit y corregir antes de entregar.

## Archivos y entregables relevantes
- Ejemplo SQL dejado para pruebas:
  - `/mnt/Agentes/Gabriel/REDMINE_29365_EJEMPLO_XML_EXEC_SOLI_AUTO_RP.sql`.
- Datos reales usados en el ejemplo de `InstallQA_89`:
  - contrato `1 / 1000050`;
  - responsable actual `CC 70042944 - HENRY PUERTA`;
  - nuevo responsable RU `CC 23776800 - JOSE GOMEZ`;
  - `id_soli_externa = 29365001`, verificado libre al momento de generarlo.

## Validaciones recordadas
- `SET PARSEONLY ON` en `InstallQA_89` sobre SQL modificados y ejemplo.
- Revisión de PowerBuilder para exportacion CSV.
- Revisión del batch de facturacion sin cambios adicionales requeridos para `soli_moti = 22`.
- Revisión posterior de EOL/BOM tras `r37245`.
