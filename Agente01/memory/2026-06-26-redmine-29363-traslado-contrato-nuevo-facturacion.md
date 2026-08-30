# Memory - 2026-06-26 - Redmine 29363 traslado a contrato nuevo y facturacion

## Contexto operativo
- Interlocutor principal: Sebastian Rafael Montenegro.
- Conversacion en Google Chat directo.
- Tema trabajado: Redmine `29363`, flujo de solicitudes automaticas APP para traslado a contrato nuevo con recorrido completo hasta facturacion.
- Working copy SVN usada: `/home/luispicone/.openclaw/workspace/svn/srmontenegro-Version104-Afilmed-SolicitudesAutomaticas`.
- Rama SVN: `https://srv-infosvn.infomedical.com/svn/Coomeva/branches/Version104-Afilmed-SolicitudesAutomaticas`.
- El lunes siguiente se retoma con pruebas de facturacion.

## Objetivo funcional vigente
- Completar y validar el flujo de traslado a contrato nuevo desde APP hasta facturacion automatica.
- El flujo esperado es:
  - ingreso de solicitud automatica APP;
  - conversion a estructuras GMS/SOLICITUDES;
  - impacto del traslado;
  - creacion del contrato destino;
  - retiro/baja del integrante en el contrato origen;
  - ejecucion de AUFACT en SuperBatch;
  - reversa de comprobantes futuros del contrato origen;
  - refacturacion del contrato origen;
  - facturacion del contrato destino.
- Restriccion funcional documentada: no se puede trasladar un integrante titular/titular desde el contrato origen.

## Codigo ajustado
- Archivo principal modificado: `exe_afilmed/src/wp_main_super_batch.srw`.
- Commit SVN inicial: `r37200`.
- Commit SVN correctivo: `r37201`.
- Motivo del correctivo: el primer cambio usaba `lib.afs_afilmed_params(...)`, pero `lib` no pertenece al target del `superbatch` y PowerBuilder reporto `C0015: Undefined variable: lib`.
- Correccion aplicada y commiteada:
  - usar `this.wf_afs_busca_afilmed_params('SuperBatch','soli_auto.facturacion.usuario', ls_usuario_facturacion, ls_mensaje)`.
- Observaciones funcionales ajustadas en SuperBatch:
  - reversa: `Automatico Proceso Traslados`;
  - facturacion: `Facturacion por Novedad de Traslados - solicitud externa <id>`.
- Usuario de facturacion parametrizado con `SuperBatch / soli_auto.facturacion.usuario`, con fallback a `gs_codusu`.

## Documentacion funcional
- Archivos actualizados y commiteados en `r37204`:
  - `Redmines/29363/REDMINE_29363_DOCUMENTACION_FUNCIONAL.md`;
  - `Redmines/29363/REDMINE_29363_DOCUMENTACION_FUNCIONAL.docx`;
  - `Redmines/29363/ejemplos_xml_traslado_contrato_nuevo_29363.sql`.
- La documentacion funcional describe el recorrido completo hasta facturacion.
- Los ejemplos XML fueron quitados de la documentacion funcional y movidos a SQL separado.
- El SQL de ejemplos debe mantenerse sin consultas extra: contiene solo los ejemplos XML como variables, sin `SELECT`, `EXEC`, `INSERT`, `UPDATE`, `DELETE`, `RTRIM` ni `;`.

## Texto sugerido para adjuntar al Redmine
- Se preparo texto para subir dos archivos al Redmine:
  - `REDMINE_29363_DOCUMENTACION_FUNCIONAL.docx`: documento funcional actualizado con recorrido completo hasta AUFACT, reversa/refacturacion del origen y facturacion del destino, incluyendo la restriccion de no trasladar titular/titular.
  - `ejemplos_xml_traslado_contrato_nuevo_29363.sql`: archivo separado con ejemplos XML del caso, fuera del documento funcional.

## Pruebas pendientes para el lunes
- Compilar/regenerar en PowerBuilder 2022 el target del SuperBatch:
  - target: `exe_afilmed/src/superbatch.pbt`;
  - PBG: `exe_afilmed/src/superbatch.pbg`;
  - PBL destino: `superbatch.pbl`;
  - objeto: `wp_main_super_batch`.
- No hace falta hacer `Get Latest Version` masivo desde PB si SVN ya actualizo fuentes; PB necesita importar/regenerar el `.srw` dentro de la `.pbl`.
- Primer foco de compilacion: confirmar que ya no aparece `C0015: Undefined variable: lib`.
- Para pruebas funcionales de facturacion, revisar pendientes con:
  - `EXEC dbo.afs_soli_auto_app_fact_pendientes`
- En un caso impactado de traslado a contrato nuevo, el esperado de pendientes es:
  - fila `D`: contrato destino nuevo, `requiere_reversion = N`, `requiere_facturacion = S`;
  - fila `O`: contrato origen, `requiere_reversion = S`, `requiere_facturacion = S` si tiene comprobantes futuros.
- Despues de correr AUFACT/SuperBatch, validar:
  - `SOLI_AUTO_CONTRATO.proce_fecha_fact` cargada para la `id_soli_externa`;
  - `SOLI_AUTO_FACT_AUDIT` con registros `R` para reversos del origen, si habia comprobantes futuros;
  - `SOLI_AUTO_FACT_AUDIT` con registros `F` para refacturacion del origen;
  - `SOLI_AUTO_FACT_AUDIT` con registros `F` para facturacion del destino nuevo.

## Validaciones realizadas durante el trabajo
- Commits SVN confirmados:
  - `r37200`: ajuste inicial de SuperBatch para facturacion;
  - `r37201`: correccion de llamada a parametros dentro del target SuperBatch;
  - `r37204`: documentacion funcional y SQL de ejemplos.
- En los cambios de codigo se valido preservacion de UTF-8 con BOM y CRLF.
- En documentacion/SQL se valido separacion de ejemplos, docx regenerado y SQL sin consultas extra.

