# 2026-07-02 - Redmine 29876 / Mantis 11760 - Asesor poblacion 61

## Contexto

Belkis solicito analizar el Redmine 29876 usando:

- Repositorio documentacion: `bmora-ProyectoCoomeva-Afilmed-01.Documentacion`.
- Repositorio codigo: `bmora-Coomeva-trunk`.
- Profile DB: `PruebasCoreINFOMEDICAL`.
- Credencial Redmine: `bmora` registrada localmente.

Redmine 29876:

- Asunto: `Solicitudes => INCONSISTENCIA_AL_IMPACTAR_ CONTRATOS_EN_AFILMED`.
- Mantis asociado: 11760.
- Problema: Afilmed asigna `Asesor Poblacion` codigo `61 - UGA Coomeva` cuando el esperado funcionalmente es `20 - Administracion CMP`.
- El asesor 61 esta inactivo, pero aun asi aparece en solicitudes y contratos.

## Caso reproducido por Belkis

Belkis genero desde Afilmed:

- Solicitud: `5513992`.
- Contrato generado: `1191733`.
- Resultado observado: `asesor_poblacion = 61`.

Datos verificados en `PruebasCoreINFOMEDICAL`:

- `SOLICITUDES.soli = 5513992`
  - `soli_moti = 1`.
  - `fecha_recep = 2026-07-02`.
  - `apli_fecha = 2026-05-01`.
  - `contra = 1191733`.
  - `estado = F`.
  - `asesor_gestion = 4507`.
  - `asesor_gestion_canal_vta = INT`.
  - `asesor_poblacion = 61`.
  - `suc_comercializable = 76001`.
- `SOLI_AFILIADOS` para la solicitud:
  - `novedad_sistema = 1`, por lo tanto no entra por logica de reactivacion.
- `AFI_CLASE` para contrato `1191733`:
  - `cuenta = 2`, `subcta = FSMP`, vigente desde `2026-05-01`.
- `AFI_PLANES`:
  - `plan_codi = PREFF`, `tari = FPREFTE`.
- `AFI_DATOS_CONTRATO_GRAL`:
  - `asesor_poblacion = 61`, copiado desde `SOLICITUDES`.

## Estado de asesores relevantes

- Asesor `20 - PREPAGADA COOMEVA MEDICINA`:
  - Activo.
  - `Aprobado = 1`.
  - `baja_fecha = NULL`.
  - `dbo.afn_estado_asesor(20) = 1`.
  - Tiene `AsesorPlan` activo/principal en `Admon Coomeva`, area `ADMINISTRATIVO`.

- Asesor `61 - UGA COOMEVA`:
  - Inactivo.
  - `Aprobado = 0`.
  - `baja_fecha = 2026-05-13`.
  - `dbo.afn_estado_asesor(61) = 0`.
  - Pero mantiene `AsesorPlan.Activo = 1`, `EsPrincipal = 1`, tipo `Admon Coomeva`, area `ADMINISTRATIVO`.

- Asesor gestion `4507`:
  - Activo.
  - Canal `INT`.

## Codigo y flujo analizado

Archivos/procedimientos revisados en `bmora-Coomeva-trunk`:

- `backend/procedures/gms_genera_solicitudes.sql`
  - Para `soli_moti = 1`, ejecuta `afu_actualiza_asesor_poblacion @soli, 'N'` antes de insertar datos generales del contrato.
  - Mas adelante ejecuta `afu_afi_datos_contrato_gral @soli`.

- `backend/procedures/afu_actualiza_asesor_poblacion.sql`
  - Calcula y actualiza `SOLICITUDES.asesor_poblacion`.
  - Para solicitudes individuales o acuerdos corporativos:
    - Si es individual, primero ejecuta `afs_busca_asesor_pob_contratante`.
    - Si no obtiene asesor y el asesor gestion es de canal `INT`, selecciona un asesor del area administracion.
  - La seleccion administrativa filtra:
    - `AsesorPlan.Activo = 1`.
    - `AsesorPlan.EsPrincipal = 1`.
    - `TipoAsesor.Activo = 1`.
    - `AreaCat.Activo = 1`.
  - No valida:
    - `Asesor.Aprobado = 1`.
    - `Asesor.baja_fecha IS NULL`.
    - `dbo.afn_estado_asesor(A.IdAsesor) = 1`.
  - Tampoco tiene `ORDER BY` ni prioridad explicita por asesor 20.

- `backend/procedures/afu_afi_datos_contrato_gral.sql`
  - Inserta `AFI_DATOS_CONTRATO_GRAL.asesor_poblacion = S.asesor_poblacion`.
  - Por eso el contrato hereda el valor de la solicitud.

- `backend/procedures/afs_get_asesor_poblacion_historico.sql`
  - Aplica a reactivaciones.
  - Si no encuentra asesor activo o externo valido, fuerza `20`.
  - No aplica al caso `5513992` porque la novedad es `1`, venta nueva.

- `backend/procedures/afs_busca_asesor_pob_contratante.sql`
  - Busca asesor poblacion historico por contratante para ventas individuales.
  - Al reejecutarlo despues del impacto puede devolver el mismo contrato actual, por lo que se debe evitar interpretar ese resultado como causa original si el contrato ya fue generado.

- `nvo_alta_total.sru` y `wp_alta_parcial.srw`
  - Revisados para entender carga/validacion de asesor gestion y asesor poblacion.

## Causa raiz

La causa raiz es doble:

1. Configuracion inconsistente:
   - El asesor 61 esta inactivo como asesor, pero conserva `AsesorPlan` activo/principal para area administrativa.

2. Defecto de validacion en `afu_actualiza_asesor_poblacion`:
   - La busqueda de asesor administrativo toma asesores con plan activo/principal sin validar estado real del asesor.
   - Por eso puede seleccionar `61` aunque `dbo.afn_estado_asesor(61) = 0`.

## Alcance cuantificado

Consulta de candidatos desde la baja del asesor 61 (`2026-05-13`) en `PruebasCoreINFOMEDICAL`:

- Solicitudes `soli_moti = 1`, `asesor_poblacion = 61`, `baja_fecha IS NULL`, `alta_fecha >= 20260513`: `3073`.
- Contratos distintos: `3073`.
- Con `AFI_DATOS_CONTRATO_GRAL` vigente en `61`: `3061`.
- Sin registro general asociado al momento de consulta: `10`.
- Con registro general en otro asesor: `2`.
- Por tipo:
  - `IN` individual: `2730`.
  - `CO` acuerdo corporativo: `343`.

Ejemplos recientes:

- `5513992` / `1191733`, alta `2026-07-02 14:33:44`, tipo `IN`, cuenta/subcta `2/FSMP`, asesor gestion `4507`, asesor poblacion `61`.
- `5513743` / `1191732`, alta `2026-06-27 11:02:40`, tipo `IN`, cuenta/subcta `2/FCEMN`, asesor gestion `4679`, asesor poblacion `61`.
- `5513719` / `1191731`, alta `2026-06-27 10:47:03`, tipo `IN`, cuenta/subcta `2/FCEMN`, asesor gestion `2082`, asesor poblacion `61`.

## Correccion recomendada

Prevencion:

- Inactivar/corregir el `AsesorPlan` activo/principal del asesor 61 y de otros asesores administrativos inactivos.
- Corregir `afu_actualiza_asesor_poblacion` para que la busqueda administrativa filtre asesores activos:
  - `A.Aprobado = 1`.
  - `A.baja_fecha IS NULL`.
  - `dbo.afn_estado_asesor(A.IdAsesor) = 1`.
- Definir un criterio deterministico. Si funcionalmente el default administrativo debe ser 20, priorizarlo explicitamente.

Correccion de datos propuesta, no ejecutada:

```sql
BEGIN TRAN;

SELECT
    S.soli,
    S.prepaga,
    S.contra,
    S.apli_fecha,
    G.vigen_desde,
    asesor_poblacion_soli = S.asesor_poblacion,
    asesor_poblacion_gral = G.asesor_poblacion
INTO TMP_R29876_ASESOR61_BACKUP
FROM SOLICITUDES S
INNER JOIN AFI_DATOS_CONTRATO_GRAL G
    ON G.prepaga = S.prepaga
   AND G.contra  = S.contra
   AND G.asesor_poblacion = 61
   AND G.baja_fecha IS NULL
WHERE S.asesor_poblacion = 61
  AND S.soli_moti = 1
  AND S.baja_fecha IS NULL
  AND S.alta_fecha >= '20260513';

UPDATE S
SET asesor_poblacion = 20,
    modi_fecha = GETDATE()
FROM SOLICITUDES S
INNER JOIN TMP_R29876_ASESOR61_BACKUP B
    ON B.soli = S.soli
WHERE S.asesor_poblacion = 61;

UPDATE G
SET asesor_poblacion = 20,
    modi_fecha = GETDATE()
FROM AFI_DATOS_CONTRATO_GRAL G
INNER JOIN TMP_R29876_ASESOR61_BACKUP B
    ON B.prepaga = G.prepaga
   AND B.contra = G.contra
   AND B.vigen_desde = G.vigen_desde
WHERE G.asesor_poblacion = 61;

SELECT COUNT(*) AS registros_respaldados
FROM TMP_R29876_ASESOR61_BACKUP;

-- COMMIT;
-- ROLLBACK;
```

Observaciones:

- No ejecutar correccion masiva sin confirmar alcance funcional exacto.
- Corregir datos sin corregir configuracion/codigo permite que el problema se repita.
- Las 10 solicitudes sin `AFI_DATOS_CONTRATO_GRAL` y los 2 casos con contrato en otro asesor requieren revision puntual.
- Si se requiere auditoria funcional, complementar la correccion SQL con registro de auditoria o procedimiento equivalente.

## Documentacion generada y commit

Documento Word creado:

- `Req y Doc. Complementaria/Solicitudes/R29876 - Mantis 11760/Analisis_R29876_M11760_asesor_poblacion_61.docx`

Repositorio:

- `bmora-ProyectoCoomeva-Afilmed-01.Documentacion`

Commit SVN:

- Revision: `3124`.
- Mensaje: `Documenta analisis Redmine 29876 asesor poblacion 61`.

Notas operativas:

- Primero fallo el commit por certificado SSL y luego por falta de credenciales SVN.
- Belkis indico credencial SVN `bmora`; se uso para completar el commit.
- Durante el commit se detecto que la carpeta remota `R29876 - Mantis 11760` ya existia; se resolvio conflicto de arbol tomando la carpeta remota y agregando solo el documento.
- Estado final de la carpeta: limpio.
