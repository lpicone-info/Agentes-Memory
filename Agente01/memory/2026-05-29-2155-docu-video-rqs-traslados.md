# 2026-05-29 - Docu-video RQs Traslados / Perfilamiento

## Contexto
- Interlocutora por Discord: Belkis.
- Se uso la skill `docu-video` para documentar funcionalmente la reunion grabada `Revision RQs Traslados-20260310_100927-Grabacion de la reunion.mp4`.
- Destino final del entregable: `/mnt/Agentes/Belkis/docu-video-revision-rqs-traslados-20260310-100927`.
- DOCX generado: `/mnt/Agentes/Belkis/docu-video-revision-rqs-traslados-20260310-100927/output/revision-rqs-traslados-20260310-100927-documentacion-funcional.docx`.

## Limitaciones del video
- La validacion de integridad detecto corrupcion parcial al final del MP4.
- Duracion declarada: `01:58:08`.
- Ultimo punto decodificado correctamente: `01:55:30`.
- Perdida estimada final: `00:02:38`.
- Belkis autorizo continuar procesando solo hasta `01:55:30` y dejar la limitacion documentada.

## Contexto usado
- Video principal de reunion.
- Documento contextual en `/mnt/Agentes/Belkis`.
- Repositorio `gpulka-swiss-temp`: usado solo como ejemplo contextual de presupuestacion, no como verdad absoluta.
- Repositorio `bmora-Coomeva-trunk`: repositorio objetivo para ajustar la funcionalidad al aplicativo AFILMED Coomeva.

## Hallazgos funcionales principales del video
- El proceso actual de traslados/cambios de cobertura fue descrito como manual, lento y con quejas de usuarios.
- Se busca una herramienta web que valide desde la entrada: contrato, mora, perfilamiento, reglas de persona/contrato, tipo de traslado y condiciones de cobertura.
- AFILMED debe validar/grabar y devolver numero de solicitud o lista de errores.
- Se propuso separar el flujo online de radicacion/validacion de procesos pesados posteriores.
- Reverso/refacturacion y facturacion electronica no deberian resolverse online; se oriento a batch/nocturno.
- Quedaron pendientes: contrato de integracion, estructura de errores, reglas por tipo de solicitud, datos de auditoria, tablas/campos/SPs y detalle de facturacion por escenario.

## Perfilamiento
- A pedido de Belkis se busco en `bmora-ProyectoCoomeva-Afilmed-01.Documentacion` documentacion sobre perfilamiento.
- Archivos principales encontrados:
  - `P-04-DEF Marcacion Perfilamiento Afiliado_V05.docx`
  - `P-04-DEF Marcacion Perfilamiento Afiliado_V03.docx`
  - `P-04-DEF Marcacion Perfilamiento Afiliado_V02.docx`
  - `A-04-DEF Solicitudes E2 - Marcacion Perfilamiento Afiliado_V04.docx`
  - carpeta `Req y Doc. Complementaria/Solicitudes/R19672 - Mantis 5017 - Marcacion Perfilamiento Afiliado`
- Soportes relevantes dentro de esa carpeta:
  - `requerimiento nuevo v_3_en revision.docx`
  - `REQ/Requerimiento Marcacion Perfilamiento Afiliado-NOTAS INFOMEDICAL*.docx`
  - `REQ/unificado_MI_SAO_NPS_MARCACION.xlsx`
  - `Mantis 6359/P-04-DEF Marcacion Perfilamiento Afiliado_V03.docx`
  - `Mantis 6359/Pendientes a nivel tablas.txt`
  - `Mantis 6359/SQLQuery2.sql`
- Interpretacion funcional: el perfilamiento es una marcacion asociada a una persona, no estrictamente al contrato. Aunque se cargue desde un contrato, impacta en `REGISTRO_UNICO_PERFILAMIENTO` por codigo unico de persona y puede verse en otros contratos de la misma persona.
- Tablas/conceptos mencionados: `PERFILES_TIPO`, `PERFILES_CONFIG`, `PERFILES_CONFIG_SUB`, `SOLI_PERFILAMIENTO`, `SOLI_RESP_PAG_PERFILAMIENTO`, `REGISTRO_UNICO_PERFILAMIENTO`.
- Para el requerimiento de traslados, el perfilamiento se entiende como validacion previa para permitir, bloquear, auditar o rechazar una solicitud.

## Entregable publicado
- El entregable incluye: `input/video_origen.md`, `audio/audio.wav`, `analysis/`, `transcript/transcripcion.md`, `frames/relevantes/`, `logs/` y `output/*.docx`.
- No se publico el MP4 original ni chunks internos.
- La carpeta local de ejecucion de `docu-video` fue eliminada al finalizar.
