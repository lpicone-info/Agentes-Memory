# Memory - 2026-06-20 - Redmine 29362 traslado existente APP

## Contexto operativo
- Interlocutor principal: Sebastian Rafael Montenegro.
- Conversacion en Google Chat directo.
- Tema trabajado: Redmine `29362`, flujo de solicitudes automaticas APP para `soli_moti = 48` traslado a contrato existente.
- Working copy SVN usada: `/home/luispicone/.openclaw/workspace/svn/srmontenegro-Version104-Afilmed-SolicitudesAutomaticas`.
- Revision base actualizada por `svn update`: `r37150`.
- Cambio de Gabriel bajado en `r37150`: `Quita inte del XML de traslado existente`.

## Flujo tecnico vigente identificado
- Fase 1: `afi_insertar_soli_auto` despacha a `afi_insertar_soli_auto_traslado_existente`.
- Fase 2: `afu_genera_soli_auto_app` convierte `SOLI_AUTO_*` a `GMS_CAB / GMSTXT_*`.
- Fase 3: `gms_validar_todo` valida y pasa a `GMSDEF_*`.
- Fase 4: `gms_genera_solicitudes` genera `SOLICITUDES / SOLI_AFILIADOS`.
- Fase 5: impacto destino y copia tecnica de preexistencias, sin auditoria ni certificados automaticos.
- Fase 6: `afi_genera_solis_aut_traslados` genera retiro/baja en contrato origen.
- Fase 7: controles finales de trazabilidad, origen retirado, destino activo, ausencia de auditoria/certificados y sin `GMS_ERR`.

## Punto funcional clave
- Para `soli_moti = 48`, el origen debe venir explicitamente en XML/datos APP con `anter_prepa`, `anter_contra` y `anter_inte`.
- No debe inferirse origen solo por documento porque en APP no existe seleccion manual.
- Desde `r37150`, el `inte` del XML de traslado existente no debe ser tomado como integrante destino real; el backend calcula el `inte`.

## Diagnostico sobre parentesco
- Sebastian aclaro que el problema observado no era el integrante nuevo del destino.
- El caso discutido era el integrante existente en el contrato origen que pasaba de titular-titular a titular-hijo.
- Causa tecnica revisada: en Fase 6, `afi_genera_solis_aut_traslados` puede ejecutar cambio de titularidad del contrato origen si el trasladado era el titular.
- El SP promueve otro integrante activo como titular usando `afu_afi_histo_paren` con `@paren = titular` y `@paren_real = @var_paren_real_ant`.
- Si `@var_paren_real_ant` viene como `H`, el resultado queda `T/H`.
- La validacion pendiente en ese diagnostico era revisar que fila exacta de `AFI_HISTO_PAREN` se toma para `@var_apli_fecha`.

## Error del batch diagnosticado
- Log informado por Sebastian el 2026-06-19: durante Generacion Solicitudes, motivo 48, SQL Server devolvia:
  - `SQLSTATE = 23000`
  - `Violation of PRIMARY KEY constraint 'pk_afiliados'`
  - clave duplicada en `dbo.AFILIADOS`: `(1, 1000050, 02)`.
- Ocurria en procesos `48` y `49`; el proceso `47` contra el mismo contrato destino `1000050` habia generado solicitud.
- Interpretacion confirmada: varios procesos/lote apuntaban al mismo contrato destino `1000050`.
- El primer proceso ocupaba el proximo `inte` destino, por ejemplo `02`; los siguientes volvian a calcular el mismo `02` y fallaban por PK duplicada.

## Fix aplicado
- SP actualizado: `dbo.afu_genera_soli_auto_app`.
- Archivo SVN: `backend/procedures/afu_genera_soli_auto_app.sql`.
- Commit SVN realizado: `r37154`.
- Mensaje de commit: `29362 Evita duplicar inte destino en traslado existente`.
- Alcance del cambio:
  - El calculo del proximo `inte` destino ya no mira solo `AFILIADOS` activos.
  - Ahora toma el maximo `inte` ocupado en `AFILIADOS`, `GMSTXT_INTEGRANTES`, `GMSDEF_INTEGRANTES` y `SOLI_AFILIADOS`.
  - Los anexos usan la misma base calculada, para apuntar al mismo `inte` destino que el integrante.
- No se tocaron para este fix:
  - `gms_genera_solicitudes`.
  - `afi_genera_solis_aut_traslados`.

## Validaciones del commit
- SVN limpio despues del commit, salvo externos `X`.
- Encoding preservado: UTF-8 sin BOM.
- Finales de linea preservados: CRLF.
- Sin `;` ni `RTRIM`.
- Diff revisado y commit confirmado en `r37154`.

## Ejemplo de prueba sugerido
- Para probar el fix, insertar dos solicitudes automaticas `soli_moti = 48` contra el mismo contrato destino `1000050`, con distinta `id_soli_externa`.
- IDs propuestos en chat: `293629048` y `293629049`.
- Origenes de ejemplo:
  - `anter_prepa = 1`, `anter_contra = 9998`, `anter_inte = 02`, `docu_nro = 1114239585`.
  - `anter_prepa = 1`, `anter_contra = 9998`, `anter_inte = 03`, `docu_nro = 29659628`.
- En el XML no mandar `inte` en `<integrante>`; el proceso debe calcularlo.
- Para contactos, se sugirio usar `inte="01"` porque cada XML trae un solo integrante y `afi_insertar_soli_auto_traslado_existente` lo normaliza internamente a `01` en `SOLI_AUTO_*`.
- Antes de probar, validar que las `id_soli_externa` no existan en `SOLI_AUTO_CONTRATO`.
- Despues del batch, validar `SOLI_AUTO_CONTRATO` y `SOLICITUDES` por `nro_formulario`/`id_soli_externa`.

## Preferencia operativa marcada por Sebastian
- Sebastian indico que una respuesta sobre un tema general historico no correspondia al contexto para el que nacio Maxxuel.
- Solicito que Luis cree una o varias reglas para impedir respuestas sobre temas generales fuera del alcance del agente.
- Hasta que exista regla formal en `REGLAS.md` o `AGENTS.md`, conservar como preferencia operativa: priorizar respuestas dentro del rol tecnico de Maxxuel y evitar responder temas generales no vinculados al contexto tecnico/profesional, salvo instruccion explicita superior o necesidad operativa.
