# Memory - 2026-06-29 - Redmine 29363 pruebas traslado a contrato nuevo

## Contexto
- Interlocutor: Sebastian Rafael Montenegro.
- Canal: Google Chat directo.
- Tema: Redmine `29363`, solicitudes automaticas APP para traslado a contrato nuevo (`soli_moti = 47`) y posterior facturacion AUFACT.
- Continuacion directa de la memoria `/home/luispicone/.openclaw/workspace/memory/2026-06-26-redmine-29363-traslado-contrato-nuevo-facturacion.md`.
- Working copy SVN usada: `/home/luispicone/.openclaw/workspace/svn/srmontenegro-Version104-Afilmed-SolicitudesAutomaticas`.
- Rama SVN: `https://srv-infosvn.infomedical.com/svn/Coomeva/branches/Version104-Afilmed-SolicitudesAutomaticas`.
- Profile DB usado para validaciones: `InstallQA_89`.

## Redmine 29363 - contexto cargado
- Redmine `29363`: proyecto `COOMEVA - Desarrollos Facturable`, tracker `Tarea`, estado `En Desarrollo`, asignado a Sebastian Rafael Montenegro.
- Asunto: `Implementar proceso de grabacion automatica traslado a contrato nuevo`.
- Adjuntos relevantes leidos:
  - `REDMINE_29363_DOCUMENTACION_FUNCIONAL.docx`;
  - `ejemplos_xml_traslado_contrato_nuevo_29363.sql`;
  - documentos funcionales `A-04-DEF Solicitudes E1`;
  - adjuntos locales en `Redmines/29363`.
- Restriccion funcional clave: no trasladar titular/titular del contrato origen. El integrante trasladado puede convertirse en titular/titular del contrato destino.

## Facturacion AUFACT aplicada
- Se verifico en `InstallQA_89` que el proceso de facturacion automatica para traslados APP esta aplicado:
  - existe `dbo.afs_soli_auto_app_fact_pendientes`, modificado `2026-06-23 13:28:40`;
  - existe `dbo.afu_soli_auto_fact_audit`;
  - existe tabla `dbo.SOLI_AUTO_FACT_AUDIT`;
  - `SOLI_AUTO_CONTRATO` tiene `proce_fecha_fact`, `prefac_cab`, `lote_reverso`;
  - existe configuracion vigente `AUFACT` en `FAC_CONFIG_BATCH`;
  - existe `AUFACT` en `TIPO_PROCESO_AGENDA`.
- Se verifico en la definicion aplicada de `dbo.afs_soli_auto_app_fact_pendientes` que para `soli_moti = 47`:
  - contrato origen sale desde `SOLI_AUTO_INTEGRANTES.anter_prepa / anter_contra`;
  - origen con comprobantes futuros requiere reversa y facturacion;
  - contrato destino `tipo_contrato = 'D'` requiere facturacion y no reversa;
  - destino sin comprobantes previos igual entra para facturacion.
- En `PruebasCoreINFOMEDICAL` esos objetos/configuracion no estaban aplicados al momento de la verificacion.

## Pruebas generadas y commits SVN
- Se intento inicialmente usar contrato origen `808859` con fecha de aplicacion `2026-05-01`, pero en ese momento solo tenia integrante `01` vigente y era titular `T`. No se genero prueba valida en ese punto.
- Luego se genero una prueba alternativa con contrato origen `298320`, integrante `02`, fecha de aplicacion `2026-05-01`, `id_soli_externa = 293630204`.
  - Archivo: `Redmines/29363/ejecucion_real_soli_auto_traslado_nuevo_contrato_298320.sql`.
  - Validacion ejecutada en `InstallQA_89` dentro de transaccion con rollback: inserto `SOLI_AUTO_CONTRATO` y `SOLI_AUTO_INTEGRANTES`; rollback dejo `0` registros persistidos.
  - Commit SVN: `r37219`, mensaje `Redmine 29363 agrega prueba traslado contrato nuevo 298320`.
- Despues Sebastian informo que agregaron un segundo integrante al contrato `808859`.
- Se genero la prueba solicitada para contrato origen `808859`, integrante `02`, fecha de aplicacion `2026-05-01`, `id_soli_externa = 293630205`.
  - Archivo: `Redmines/29363/ejecucion_real_soli_auto_traslado_nuevo_contrato_808859.sql`.
  - Commit SVN: `r37220`, mensaje `Redmine 29363 agrega prueba traslado contrato nuevo 808859`.
  - Autor SVN confirmado: `srmontenegro@INFOMEDICAL`.

## Datos validados para la prueba final 808859
- Contrato origen: prepaga `1`, contrato `808859`.
- Fecha de aplicacion: `2026-05-01`.
- Titular remanente en origen:
  - integrante `01`;
  - parentesco `T`;
  - documento `RC 1022008503`;
  - nombre `LUCCA PEREZ SALAZAR`;
  - vigente sin `baja_fecha`.
- Integrante trasladado:
  - integrante origen `02`;
  - parentesco origen `F`;
  - documento `CC 1193455906`;
  - nombre `JULIAN ANDRES MONTENEGRO PARRA`;
  - sexo `M`;
  - nacimiento `2001-01-31`;
  - nacionalidad `CO`;
  - estado civil `S`;
  - profesion `952`;
  - cargo `0`;
  - ocupacion `8`;
  - estrato social `0`;
  - rango salarial `0`;
  - red Coomeva `N`;
  - obra social `43`;
  - antiguedad `2024-12-06`;
  - ingreso `2026-04-01` en origen;
  - ingreso destino informado en XML `2026-05-01`.

## Validaciones ejecutadas sobre la prueba final 808859
- Antes de probar, se verifico que no habia pendientes ajenos sin `GMS_CAB` para `afu_genera_soli_auto_app`.
- Se verifico que `id_soli_externa = 293630205` estaba libre en `SOLI_AUTO_CONTRATO` y `GMS_CAB`.
- Validacion completa ejecutada en `InstallQA_89` dentro de transaccion con rollback:
  - `dbo.afi_insertar_soli_auto`;
  - `dbo.afu_genera_soli_auto_app`;
  - `dbo.gms_validar_todo`;
  - `dbo.gms_genera_solicitudes`.
- Resultado de validacion completa:
  - `GMS_CAB.canti_errores = 0`;
  - `GMS_CAB.puede_procesarse = 'S'`;
  - `gms_genera_solicitudes` genero solicitud `4677042` dentro del rollback;
  - rollback confirmado con `0` registros persistidos para `id_soli_externa = 293630205`.
- Validacion final del archivo real `ejecucion_real_soli_auto_traslado_nuevo_contrato_808859.sql`:
  - ejecutado dentro de `BEGIN TRAN` + `ROLLBACK`;
  - inserto `SOLI_AUTO_CONTRATO` con `id_proceso = 74`, `soli_moti = 47`, `contra = '1'`, `fecha_aplicacion = 2026-05-01`, `proce_fecha = NULL`;
  - inserto `SOLI_AUTO_INTEGRANTES` con `anter_prepa = 1`, `anter_contra = '808859'`, `anter_inte = '02'`, `paren_destino = 'T'`, `paren_real_destino = 'T'`;
  - rollback dejo `0` registros persistidos para `293630205`.
- Archivo validado como ASCII, CRLF, sin BOM y sin punto y coma.

## Estado local final
- Luego del commit `r37220`, la working copy quedo sin cambios pendientes.
- `svn status` solo mostro externals `X` existentes:
  - `exe_InfoMailer/pbls/impresion.pbl`;
  - `exe_presmed/entidades.pbl`;
  - `exe_presmed/ficha_afiliado.pbl`.

## Para retomar manana
- Sebastian dijo: `ok, manana lo pruebo`.
- Archivo recomendado para la prueba manual: `Redmines/29363/ejecucion_real_soli_auto_traslado_nuevo_contrato_808859.sql`.
- El script real solo inserta la solicitud automatica y deja pendiente `proce_fecha = NULL`; no ejecuta `afu_genera_soli_auto_app`, `gms_validar_todo` ni `gms_genera_solicitudes`.
- Despues de insertar con el script, el batch AU deberia procesar sin errores DEF segun la validacion con rollback.
- Si se prueba AUFACT luego del impacto:
  - contrato origen `808859` deberia reversar/refacturar si tiene comprobantes futuros desde `2026-05-01`;
  - contrato destino nuevo deberia solo facturarse, sin reversa.
