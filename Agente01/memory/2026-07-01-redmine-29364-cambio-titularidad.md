# Memory - 2026-07-01 - Redmine 29364 cambio de titularidad APP

## Contexto
- Interlocutor: Sebastian Rafael Montenegro.
- Canal: Google Chat directo.
- Tema: Redmine `29364`, solicitudes automaticas APP para cambio de titularidad Afilmed.
- Working copy SVN usada: `/home/luispicone/.openclaw/workspace/svn/srmontenegro-Version104-Afilmed-SolicitudesAutomaticas`.
- Rama SVN: `https://srv-infosvn.infomedical.com/svn/Coomeva/branches/Version104-Afilmed-SolicitudesAutomaticas`.
- Carpeta de entregables en la rama: `Redmines/29364`.
- Documento tecnico fuente revisado: `/mnt/Agentes/Sebastian/REDMINE_29364_ANALISIS_FUNCIONAL_TECNICO_CAMBIO_TITULARIDAD_SOLI_AUTO.docx`.
- Presupuesto de horas final dejado en `/mnt/Agentes/Sebastian/REDMINE_29364_PRESUPUESTO_HORAS_4_FASES_FUNCIONAL.docx`.

## Requerimiento funcional resumido
- Implementar cambio de titularidad automatico recibido desde APP.
- Entrada por XML con `soli_moti = 7`.
- Registrar la novedad, generar e impactar solicitud interna, aplicar cambio de titularidad y luego permitir normalizacion economica por AUFACT.
- La trazabilidad debe permitir ver rechazados/procesados, solicitud interna, prefactura, reversas, facturas, importes y errores.

## Convivencia con Redmine 29365 de Gabriel
- Durante el trabajo, Gabriel Pulka commiteo cambios de Redmine `29365`:
  - `r37243`: cambio responsable pagador SOLI_AUTO;
  - `r37244`: contempla RP en exportacion batch solicitudes;
  - `r37245`: normaliza finales de linea objetos SQL.
- Antes de commitear fase 1, SVN marco archivos desactualizados. Se hizo `svn update`, se resolvieron conflictos conservando los cambios de 29365 y se commiteo sobre esa base.
- Antes de fase 3 se hizo otro `svn update`, quedando la working copy en `r37247`.
- Se verifico luego en HEAD que los bloques y objetos de 29365 seguian presentes:
  - `afi_insertar_soli_auto_cambio_resp_pagador`;
  - `SOLI_AUTO_RESP_PAGADOR`;
  - `GMSDEF_RESP_PAGADOR`;
  - `GMSTXT_RESP_PAGADOR`;
  - campos `finalizar_resp_pagador`, `baja_resp_pagador`, `vigen_hasta_resp_pagador`;
  - logica de responsable pagador en `afu_genera_soli_auto_app` y `gms_genera_solicitudes`.
- Conclusion comunicada a Sebastian: no se piso lo de Gabriel; los commits de 29364 quedaron encima de `r37245`.

## Commits SVN realizados para 29364
- `r37246`: `Refs #29364 Fase 1 recepcion cambio titularidad APP`.
- `r37247`: `Refs #29364 Fase 2 genera e impacta cambio titularidad APP`.
- `r37248`: `Refs #29364 Fase 3 normalizacion economica cambio titularidad APP`.
- `r37249`: `Refs #29364 Fase 4 validacion y documentacion cambio titularidad APP`.
- Autor SVN observado: `srmontenegro@INFOMEDICAL`.
- Estado local final: `svn status --ignore-externals` limpio salvo externos `X` habituales:
  - `exe_InfoMailer/pbls/impresion.pbl`;
  - `exe_presmed/entidades.pbl`;
  - `exe_presmed/ficha_afiliado.pbl`.

## Fase 1 - Recepcion y validacion XML
- Se agrego `backend/procedures/afi_insertar_soli_auto_cambio_titularidad.sql`.
- Se modifico `backend/procedures/afi_insertar_soli_auto.sql` para derivar `soli_moti = 7` al nuevo receptor.
- Se modifico `backend/procedures/afs_soli_auto_obligatorios.sql` para validar obligatorios de cambio de titularidad:
  - nuevo titular;
  - indicador de baja del titular anterior;
  - motivo de baja si corresponde;
  - parentesco del titular anterior si no se baja;
  - detalle de parentescos por integrante.
- Se modifico `backend/tables/SOLI_AUTO_CONTRATO.sql` agregando campos:
  - `inte_nuevo_titular`;
  - `baja_titular`;
  - `baja_moti`;
  - `paren_titular_anterior`;
  - `genera_resp_pagador`;
  - `meses_cobertura`.
- Se reutilizo `SOLI_AUTO_PARENTESCOS` para staging de parentescos recibidos por XML.
- Entregables en `Redmines/29364`:
  - `FASE_1_ALCANCE_Y_OBJETOS.md`;
  - `ejemplos_xml_cambio_titularidad_29364.sql`.
- El archivo de ejemplos contiene 5 XMLs con rollback:
  - `293640001`;
  - `293640002`;
  - `293640003`;
  - `293640004`;
  - `293640005`.
- Validacion ejecutada: los 5 XMLs parsearon como XML bien formado con Python.

## Fase 2 - Generacion e impacto de solicitud
- Se modifico `backend/procedures/afu_genera_soli_auto_app.sql`.
- Cambios principales:
  - lectura de campos nuevos de `SOLI_AUTO_CONTRATO`;
  - mapeo de `soli_moti = 7` a transaccion `CT`;
  - inclusion del motivo 7 en armado de cobertura/base;
  - armado de integrantes para cambio de titularidad, usando:
    - nuevo titular como parentesco titular;
    - titular anterior con parentesco informado cuando no se da de baja;
    - parentescos recibidos para el resto.
- Se modifico `backend/procedures/gms_genera_solicitudes.sql`.
- Cambios principales:
  - inclusion de `soli_moti = 7` en condiciones de GMS usadas por automaticas;
  - reutilizacion de staging `SOLI_AUTO_PARENTESCOS`;
  - llamada a `dbo.afu_impacta_cambio_titutar` para impactar el cambio de titularidad.
- Entregable en `Redmines/29364`: `FASE_2_ALCANCE_Y_OBJETOS.md`.
- Validaciones estaticas ejecutadas:
  - sin marcadores de conflicto;
  - sin `RTRIM` ni punto y coma agregados en diffs SQL;
  - se preservo codificacion de `gms_genera_solicitudes.sql` al editarlo con metodo binario por ser archivo no UTF-8.

## Fase 3 - Normalizacion economica y traza de facturacion
- Se modifico `exe_afilmed/src/wp_main_super_batch.srw`.
- Cambio aplicado:
  - en `wf_proceso_facturacion_app_au`, si `li_soli_moti = 7`, el comentario de prefacturacion queda como `Facturacion por Novedad de Cambio de Titularidad - solicitud externa ...`;
  - para el resto de motivos se conserva el comentario anterior de traslados.
- No se agregaron ni modificaron SPs en esta fase.
- Se reutilizan:
  - `afs_soli_auto_app_fact_pendientes`;
  - `afu_soli_auto_app_fact_traza`;
  - `afu_soli_auto_fact_audit`;
  - `afs_soli_auto_app_trazabilidad`.
- Se verifico que `wp_main_super_batch.srw` conservara UTF-8 con BOM y CRLF.
- Entregable en `Redmines/29364`: `FASE_3_ALCANCE_Y_OBJETOS.md`.

## Fase 4 - Validacion y documentacion de entrega
- No se modificaron objetos productivos.
- Se agregaron entregables:
  - `Redmines/29364/FASE_4_ALCANCE_Y_OBJETOS.md`;
  - `Redmines/29364/RESUMEN_FASES_OBJETOS_SP_29364.md`;
  - `Redmines/29364/fase4_validacion_integral_29364.sql`.
- `fase4_validacion_integral_29364.sql` consulta por `@id_soli_externa`:
  - recepcion en `SOLI_AUTO_CONTRATO`;
  - parentescos en `SOLI_AUTO_PARENTESCOS`;
  - cabecera `GMS_CAB`;
  - solicitud interna en `SOLICITUDES`;
  - salida de `afs_soli_auto_app_trazabilidad` con debug.
- Validaciones estaticas ejecutadas:
  - archivos ASCII;
  - sin marcadores de conflicto;
  - sin `RTRIM` ni punto y coma agregados en SQL nuevo.

## Objetos productivos agregados o modificados
- Agregado:
  - `backend/procedures/afi_insertar_soli_auto_cambio_titularidad.sql`.
- Modificados:
  - `backend/procedures/afi_insertar_soli_auto.sql`;
  - `backend/procedures/afs_soli_auto_obligatorios.sql`;
  - `backend/tables/SOLI_AUTO_CONTRATO.sql`;
  - `backend/procedures/afu_genera_soli_auto_app.sql`;
  - `backend/procedures/gms_genera_solicitudes.sql`;
  - `exe_afilmed/src/wp_main_super_batch.srw`.
- Reutilizados sin cambios productivos:
  - `SOLI_AUTO_PARENTESCOS.sql` creado/ajustado por 29365 y usado por 29364;
  - `afs_soli_auto_app_fact_pendientes`;
  - `afu_soli_auto_app_fact_traza`;
  - `afu_soli_auto_fact_audit`;
  - `afs_soli_auto_app_trazabilidad`;
  - `afu_impacta_cambio_titutar`.

## Validaciones realizadas
- `svn status --ignore-externals` final limpio salvo externos `X`.
- `svn log -r 37243:37249 -v` revisado con config SVN autenticado.
- Se confirmo que los commits de 29365 de Gabriel seguian presentes en HEAD.
- Los 5 XMLs de `ejemplos_xml_cambio_titularidad_29364.sql` parsearon OK como XML.
- Se hicieron controles de conflicto con `rg`.
- Se hicieron controles de diffs SQL para no agregar `RTRIM` ni `;`.
- No se ejecuto prueba real contra base durante este cierre porque no se corrio conexion SQL desde el entorno en esta etapa.

## Para retomar manana
- Objetivo: comenzar compilaciones y pruebas de Redmine 29364.
- Primero actualizar working copy y verificar que no haya nuevos commits posteriores a `r37249`.
- Compilar/aplicar en ambiente de prueba los objetos productivos listados arriba.
- Cuidar especialmente la convivencia con 29365, porque hay objetos compartidos:
  - `afi_insertar_soli_auto.sql`;
  - `afs_soli_auto_obligatorios.sql`;
  - `SOLI_AUTO_CONTRATO.sql`;
  - `afu_genera_soli_auto_app.sql`;
  - `gms_genera_solicitudes.sql`.
- Luego probar con uno de los XMLs de `Redmines/29364/ejemplos_xml_cambio_titularidad_29364.sql`.
- Usar `Redmines/29364/fase4_validacion_integral_29364.sql` para revisar recepcion, GMS, solicitud interna y trazabilidad.
- Si se necesita prueba end to end, ejecutar secuencia esperada:
  - `afi_insertar_soli_auto`;
  - `afu_genera_soli_auto_app`;
  - validacion GMS correspondiente;
  - `gms_genera_solicitudes`;
  - proceso AUFACT desde `wp_main_super_batch.srw` o flujo batch equivalente;
  - `afs_soli_auto_app_trazabilidad`.
