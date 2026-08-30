# Memory - 2026-07-02 - Redmine 29983 / M11793 prefacturacion y facturacion

## Contexto
- Interlocutora: Belkis Josefina Garcia Mora.
- Canal: Google Chat directo.
- Tema: Redmine `29983` / Mantis `11793`.
- Caso central: contrato `1093141`, integrante `01`, campania `305`.
- Base usada para validaciones: profile `PruebasCoreINFOMEDICAL`.
- Repositorios involucrados:
  - `bmora-Coomeva-trunk`
  - `bmora-ProyectoCoomeva-Afilmed-01.Documentacion`
- Carpeta documental SVN:
  - `Req y Doc. Complementaria/Facturacion/R29983_M11793`

## Antecedente del 22/06/2026
- Ya existia memoria previa en `memory/2026-06-22.md`.
- Se habia analizado el mensaje de prefacturacion:
  - `Los descuentos de campanas no aplican a tarifas de tipo Parentesco mas Categoria`.
- Causa tecnica:
  - `backend/procedures/afu_fac_camp_comercial_errores.sql`
  - condicion `FAC.tari_tipo = 'Q'`
  - tipo `Q` equivale a `Parentesco mas Categoria` / `Categoria y Parentescos`.
- Conclusion funcional:
  - no era advertencia informativa;
  - el error bloqueaba prefacturacion/facturacion porque terminaba excluyendo movimientos con errores.
- Caso validado:
  - contrato `1093141`
  - integrante `01`
  - campania `305`
  - vigencia original `2025-08-01` a `2026-02-28`
  - origen `soli = 4843445`, `soli_moti_origen = 1 - Venta Nueva`.
- Como la campania nacio por Venta Nueva y no por motivo `54 - Campanas Comerciales`, la pantalla no permitia marcar baja.
- Accion recomendada:
  - cerrar vigencia de `AFI_CAMPANIAS` al `2026-01-31`.
- Documento previo generado y commiteado:
  - `Analisis_prefacturacion_campanias_tarifa_parentesco_categoria.docx`
  - SVN `r3103`
  - mensaje `R29983_M11793 Documenta analisis de prefacturacion por campanas y tarifa parentesco categoria`.

## Trabajo del 01/07/2026 sobre cierre de campania
- En una conversacion con Gabriel se retomo el Redmine `29983`, usuario `gpulka`, rama `gpulka trunk`.
- Se actualizo working copy `gpulka-Coomeva-trunk` a `r37242`.
- Se genero el script:
  - `/mnt/Agentes/Gabriel/REDMINE_29983_UPDATE_CIERRE_CAMPANIA_1093141.sql`
- Version inicial:
  - contenia controles, estado antes/despues, validacion de una unica fila objetivo, ejecucion de `afs_valida_campania_facturada` y `COMMIT` condicionado.
- Version final solicitada:
  - solo el `UPDATE`, sin variables, sin `SELECT`, sin transaccion ni validaciones.
- El `UPDATE` final cerraba:
  - `AFI_CAMPANIAS.vigen_hasta = '20260131'`
  - para `prepaga = 1`, `contra = '1093141'`, `inte = '01'`, `cod_camp_comercial = 305`, `soli = 4843445`, `soli_moti_origen = 1`.
- No se ejecuto el script desde el agente en esa instancia.
- Se valido que el archivo quedo ASCII y que la working copy no quedo con cambios locales propios.

## Retoma con Belkis el 01/07/2026 tarde / 02/07/2026 madrugada
- Belkis pidio explicar el mensaje:
  - `Existen movimientos facturables a la empresa, no se permite la facturacion individual`.
- Repositorios usados:
  - `bmora-Coomeva-trunk`
  - `bmora-ProyectoCoomeva-Afilmed-01.Documentacion`
- Evidencia en codigo:
  - `exe_afilmed/src/wp_facturacion_individual_contratante.srw`
  - la ventana valida `factu_destino = 'E'` antes de facturar individualmente.
- Interpretacion funcional:
  - se esta usando `Facturacion Individual de Contratantes`;
  - dentro de la prefacturacion hay al menos un movimiento con destino Empresa;
  - la pantalla individual solo debe avanzar con movimientos facturables al afiliado/contratante individual;
  - los movimientos `E` deben tratarse por circuito Empresa.
- Tambien se verifico que:
  - `factu_destino = 'E'` corresponde a Empresa;
  - `factu_destino = 'A'` corresponde a Afiliado.

## Validaciones de cuentas 493 y 616
- En `PruebasCoreINFOMEDICAL`, cuenta `493`:
  - existian `119` comprobantes vigentes en `COMPROBANTES`;
  - rango de emision `2020-07-31` a `2026-06-17`;
  - total acumulado `17.606.820,00`;
  - saldo acumulado `0,00`;
  - todos con `factu_destino = E`;
  - tambien habia `174` registros vigentes en `PREFACTURAS`, todos destino `E`, importe acumulado `8.250.000,00`.
- En `PruebasCoreINFOMEDICAL`, cuenta `616`:
  - existian `57.439` comprobantes vigentes;
  - rango de emision `2020-01-17` a `2026-06-24`;
  - total acumulado `1.608.780.652,80`;
  - saldo acumulado `110.324.165,00`;
  - habia destino `E` y algunos `A`, pero la facturacion principal encontrada era `E`;
  - en `PREFACTURAS` habia `654.186` registros vigentes, todos `factu_destino = E`, importe acumulado `115.091.763.981,00`.

## Estado posterior al cierre de campania
- Belkis indico que la campania ya fue dada de baja/cerrada al `31/01/2026` en `PruebasCoreINFOMEDICAL`.
- Se revalido que la campania `305` del contrato `1093141`, integrante `01`, ya figuraba con `vigen_hasta = 2026-01-31`.
- Tambien se revalido:
  - `EXEC afs_valida_campania_facturada 1, '1093141', '01', 305, '20260131'`
  - resultado `cantidad = 0`.
- Conclusion:
  - el problema de campania quedo resuelto;
  - el bloqueo posterior ya no era por campania, sino por mezcla de movimientos `A` y `E` en prefacturacion/facturacion.

## Prefacturacion mixta detectada
- Belkis habia prefacturado el contrato `1093141` para periodo `06/2026`.
- Al intentar facturar por `Facturacion Individual de Contratantes`, seguia apareciendo:
  - `Existen movimientos facturables a la empresa, no se permite la facturacion individual`.
- Evidencia:
  - `prefac_cab = 1406157`
  - tipo `Facturacion Individual de Contratantes`
  - periodo `06/2026`
  - contrato `1093141`
  - 5 movimientos:
    - 2 movimientos `A` en cuenta `2 / FSMP`, total `559.100`
    - 3 movimientos `E` en cuenta `616 / 6163`, total `739.800`
  - movimientos `E`:
    - `apli_perio 2026-02-01`, `246.600`
    - `apli_perio 2026-03-01`, `246.600`
    - `apli_perio 2026-04-01`, `246.600`
  - sin comprobantes:
    - `COMPROBANTES`: sin filas para `prefac_cab = 1406157`
    - `PREFAC_COMPROBANTES`: sin filas
    - `gene_fecha = NULL`.
- Primer criterio operativo:
  - facturar por circuito Empresa cuenta `616`, subcta `6163`, periodo `06/2026`;
  - luego regenerar prefacturacion individual del contrato `1093141`;
  - finalmente facturar los movimientos `A`.
- Se aclaro que no convenia cambiar manualmente `factu_destino` de `E` a `A`, porque seria incorrecto funcionalmente.

## Intentos por circuito Empresa y ajuste de criterio
- Belkis informo que realizo prefacturacion por circuito Empresa de cuenta `616`, subcta `6163`, generando `prefac_cab = 1406154`, pero el contrato `1093141` no aparecia.
- Se detecto que el contrato estaba atrapado en prefacturacion individual previa no facturada `prefac_cab = 1406157`.
- Mientras esos movimientos siguieran vivos en `1406157`, el circuito Empresa no los tomaba correctamente y la individual seguia bloqueada por movimientos `E`.
- Accion indicada:
  - liberar/anular la prefacturacion individual `1406157` del contrato `1093141`.
- Criterio de liberacion propuesto:
  - eliminar de `PREFACTURAS` los movimientos no facturados del `prefac_cab = 1406157` para el contrato `1093141`;
  - solo si no existian comprobantes ni `PREFAC_COMPROBANTES`, y con `gene_fecha IS NULL`.
- SQL conceptual indicado:
  - `DELETE PREFACTURAS`
  - `WHERE prefac_cab = 1406157`
  - `AND contra = '1093141'`
  - `AND gene_fecha IS NULL`
  - `AND baja_fecha IS NULL`
- Se propuso primero validar con `ROLLBACK`, esperando:
  - `ANTES`: 5 filas
  - `filas_eliminadas`: 5
  - `DESPUES`: sin filas.
- El agente no ejecuto el `DELETE`.
- Belkis informo despues que elimino/libero la prefacturacion individual `1406157`.

## Reproceso Empresa posterior
- Luego de liberar `1406157`, Belkis volvio a prefacturar cuenta `616`, subcta `6163`, generando `prefac_cab = 1406159`.
- El contrato `1093141` seguia sin aparecer.
- Nueva conclusion:
  - la liberacion de `1406157` habia salido bien;
  - el contrato ya no aparecia en `VERIF_CONTRA_PREFACTURA` del lote Empresa;
  - el circuito Empresa/Colectivos no lo descartaba por error posterior, sino que no lo consideraba parte del universo cuenta `616` / subcta `6163` para junio `2026`.
- Verificacion individual:
  - para junio, el contrato `1093141` figuraba con cuenta `2`, subcta `FSMP`, `factu_destino = A`.
- Los movimientos `E` anteriores eran retroactivos de aplicacion `02/2026`, `03/2026` y `04/2026`, no movimientos Empresa corrientes de junio.
- Criterio final:
  - no seguir reprocesando cuenta `616 / 6163` para junio esperando que entre el contrato;
  - procesar por circuito Empresa los periodos donde nacieron los movimientos `E`: `02/2026`, `03/2026`, `04/2026`;
  - verificar si entra el contrato `1093141` en cada periodo;
  - facturar esos movimientos Empresa;
  - luego regenerar prefacturacion individual del contrato `1093141` para `06/2026`;
  - confirmar que quede solo con movimientos `A`;
  - facturar por `Facturacion Individual de Contratantes`.
- Alternativa si la pantalla no permitia procesar esos periodos:
  - ajuste/comprobante Empresa controlado por `739.800`;
  - con trazabilidad contra cuenta `616`, subcta `6163`, contrato `1093141`;
  - requiere definicion funcional explicita antes de tocar datos.

## Documentacion Word generada/ampliada el 02/07/2026
- Belkis pidio documentar lo trabajado el 01/07/2026 y commitearlo en:
  - `bmora-ProyectoCoomeva-Afilmed-01.Documentacion/Req y Doc. Complementaria/Facturacion/R29983_M11793`
- Se genero el documento:
  - `Analisis_20260701_cierre_campania_prefacturacion_R29983_M11793.docx`
- Primer commit:
  - SVN `r3120`
  - autor `bmora@INFOMEDICAL`
  - fecha `2026-07-02 15:23:25 +0000`
  - mensaje `R29983_M11793 Documenta analisis cierre campania prefacturacion`
  - incluyo cierre de campania, script operativo y relacion con el analisis previo.
- Segundo pedido:
  - ampliar el mismo documento con todo lo conversado desde las 16:20 del 01/07/2026 sobre el mensaje `Existen movimientos facturables a la empresa...` y la resolucion Empresa/Individual.
- Segundo commit:
  - SVN `r3121`
  - autor `bmora@INFOMEDICAL`
  - fecha `2026-07-02 15:38:20 +0000`
  - mensaje `R29983_M11793 Amplia analisis facturacion empresa individual`
  - se agrego seccion sobre:
    - significado del mensaje;
    - cuenta 493;
    - cuenta 616;
    - prefactura mixta `1406157`;
    - liberacion/anulacion;
    - reproceso Empresa `1406159`;
    - criterio final para Empresa e Individual.
- Validaciones sobre el Word:
  - `.docx` identificado como Microsoft Word 2007+;
  - `unzip -t` sin errores;
  - texto interno revisado;
  - SVN status limpio luego de cada commit.

## Estado final del tema
- Tema cerrado por Belkis por el momento.
- No quedaron cambios pendientes en la documentacion SVN para el archivo trabajado.
- Pendiente funcional solo si se retoma:
  - confirmar en base si los movimientos Empresa retroactivos `02/2026`, `03/2026`, `04/2026` fueron finalmente facturados;
  - luego validar que la prefacturacion individual `06/2026` del contrato `1093141` quede solo con movimientos `A`;
  - no ejecutar `UPDATE`/`DELETE` sin confirmacion explicita del SQL exacto.

## Nota operativa
- La busqueda semantica de memoria estaba pausada porque el indice fue generado con otro modelo de embeddings.
- Para reindexar, correr desde consola:
  - `openclaw memory index --force`
