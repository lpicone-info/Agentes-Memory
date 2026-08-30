# Tabla de significado de REGLAS

Este documento facilita su lectura, búsqueda e interpretación de REGLAS que se aplican a los sistemas


## Hoja: Reglas

Filas con contenido: 308 (incluyendo encabezado). Columnas: 7.

| Nro. regla | Default | Incidente | Descripción | Opciones | Producto | Opcion de Menu |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 |  | Modelo de impresión | 1 / 2 | Presmed |  |
| 2 | N |  | Importa datos adicionales de productos (Manextra) | S = si / N = no | Subedatos | Farmacia |
| 3 | N |  | Usa concepto de clearing | S = si / N = no | Presmed |  |
| 4 | N |  | Adicion del valor de iva al afililiado si no hay datos | S = si / N = no | Subedatos |  |
| 5 | S |  | Modulo de Farmacias | S/N | Presmed | Farmacia |
| 6 | N |  | Clases terapéuticas de productos como familia | S = si / N = no | Presmed |  |
| 7 | N |  | Sistema de afiliados habilitado | S = si / N = no | Afilmed |  |
| 8 | S |  | Convenio de capitas | S = si / N = no | Presmed | Convenios |
| 9 | N |  | Niveles de autorizacion | S = si / N = no | Presmed | Autorizaciones |
| 10 | S |  | Emite notas de debito / crédito en liquidaciones de forma manual, automatica y automatica con numeracion secuencial con Afilmed. También imprime número de la nota de débito en el resumen de débitos al prestador | S = si (automatica) / N = no (manual) / M = si (automatica secuencial) | Presmed | Liquidacion / Supervisión |
| 11 | S |  | ¿Utiliza boletines protectivos? | S = si / N = no | Presmed / Subedatos | Autorizaciones / Liquidaciones |
| 12 | S |  | Modulo de Odontologia | S/N | Presmed | Odontología |
| 13 | S |  | Modulo de Reintegros | S/N | Presmed | Reintegros |
| 14 | N |  | Exige separacion de dias de internacion en sectores (Autorizaciones) | S = si / N = no | Presmed | Autorizaciones |
| 15 | N |  | Utiliza bonos (Liquidaciones de prestaciones) | S = si / N = no | Presmed | Liquidaciones |
| 16 | A |  | Tipo de importación en farmacia | A = Con Bcp / B = Archivo cabecera + archivo ítem / C = Un archivo / D = Sin importación | Presmed | Farmacia |
| 17 | N |  | Credenciales | S = si / N = no | Presmed | Autorizaciones / Liquidaciones |
| 18 | S |  | Modo manual de localidades | S = si / N = no |  |  |
| 19 | N |  | Carga el valor de la orden en la autorización | S = si / N = no | Presmed | Autorizaciones |
| 20 | N |  | Modulo de abogados | S = si / N = no |  |  |
| 21 | S |  | Topes de autorizaciones | S = si / N = no | Presmed | Autorizaciones |
| 22 | S |  | Considera carencias en liquidacion | S = si / N = no | Presmed | Liquidaciones |
| 23 | N |  | Situacion terapeutica DIBA (Peso + talla + superficie corporal) | S = si / N = no | Presmed | Sit terap |
| 24 | N |  | Autorizaciones por convenios | S = si / N = no | Presmed | Convenios |
| 25 | N |  | Control de altas /mod por sucursal en autorizaciones |  | Presmed | Autorizaciones |
| 26 | N |  | Nivel de autorizacion para internación | 0 / 1 / 2 = si / N = no | Presmed | Autorizaciones |
| 27 | N |  | Reintegros | S = si / N = no | Presmed | Reintegros |
| 28 | N |  | Exportación de copagos | A = opción Britanico / N = no esta habilitada | Presmed | Liquidaciones |
| 29 | N |  | Forma de numeración de reintegros | S = numeracion unica / N = numeracion x sucursal | Presmed | Reintegros |
| 30 | N |  | Obliga a cargar la autorizacion en los expedientes de Honorarios | S = si / N = no | Presmed | Liquidaciones |
| 31 | N |  | Habilita la validacion de convenios para las autorizaciones de Cirugias, cuando el especialista es el Sanatorio | S = Habilitada / N = Deshabilitada | Presmed | Autorizaciones |
| 32 | S |  | Genera los errores de cobertura en los expedientes de Honorarios, que hoy día sólo los informa visualmente y no los carga como error a revisar | S = Habilitada / N = Deshabilitada | Presmed | Liquidaciones |
| 33 | N |  | Carga de Prestadores: para permitir o no duplicación de CUIT en la carga de prestadores | S = Permite duplicados / N = No permite | Presmed | Prestadores / Datos del Prestador |
| 34 | S |  | Carga de Reintegros: Obliga cargar el tipo y numero de comprobante | S = Obligatorio / N = Opcional | Presmed | Reintegros |
| 35 | N |  | Exportación de datos de reintegros | S = Habilitada / N = Deshabilitada | Presmed | Reintegros |
| 36 | N |  | Interfases contables tipo Escribanos | S = Habilitada / N = Deshabilitada |  |  |
| 37 | N |  | Modulo de Empresas en Afilmed | S = Habilitada / N = Deshabilitada | Afilmed | Empresa |
| 38 | N |  | Quita la opción del menú de importación de prestadores e inhabilita determinados campos en la carga de Prestadores en Presmed. | S = Habilitada / N = Deshabilitada | Presmed | Prestadores / Datos del Prestador |
| 39 | N |  | Quita la opción del menú de importación de autorizaciones e inhabilita determinados campos en la carga de Autorizaciones en Presmed | S = Habilitada / N = Deshabilitada | Presmed | Autorizaciones |
| 40 | N |  | Forma de Pago para Afilmed en Carga de Solicitudes | S = Habilitada / N = Deshabilitada | Afilmed | Solicitudes |
| 41 | N |  | Derivación de Aportes para Afilmed en Carga de Solicitudes | S = Habilitada / N = Deshabilitada | Afilmed | Solicitudes |
| 42 | N |  | Codiciones ante el IVA para Afilmed en Carga de Solicutudes | S = Habilitada / N = Deshabilitada | Afilmed | Solicitudes |
| 43 | N |  | Valorización de autorizaciones al momento de la carga (incluye los informes realizados a raiz de dicha valorización) | S = Habilitada / N = Deshabilitada | Presmed | Autorizaciones |
| 44 | N |  | Habilitacion de item de menu: Exportación de padrón de afiliados en Afilmed en el menu de Solicitudes | S = Habilitada / N = Deshabilitada | Afilmed | Solicitudes |
| 45 | N |  | Habilitacion de items de menu: Interfaz de afiliados y Consulta de lotes exportados en Afilmed en el menu de Solicitudes | S = Habilitada / N = Deshabilitada | Afilmed | Solicitudes |
| 46 | 0 |  | Validacion del afiliado mirando boletines_protectivos y abo_saldos (para Abogados) | 0 / 1 | Presmed/Afilmed | Autorizaciones / Liquidaciones |
| 47 | N |  | Habilitacion de consulta de cuenta corriente por integrante | S = Habilitada / N = Deshabilitada |  |  |
| 48 | N |  | En liquidaciones se utiliza el paso de auditoria medica (Para UOCRA) | S = Habilitada / N = Deshabilitada | Presmed | Liquidaciones |
| 49 | N |  | Se carga el numero de receta en la carga de recetas de farmacia | S = si / N = no | Presmed | Farmacia |
| 50 | N |  | Sube los productos farmaceuticos en forma excluida (Solo para DiBA) | S = si / N = no | Presmed | Farmacia |
| 51 | N |  | Recibe copagos en forma automática | S = Habilitada / N = Deshabilitada | Presmed/Afilmed | Liquidaciones / Facturación |
| 52 | N |  | Tiene el modulo de medico de cabecera | S = Habilitada / N = Deshabilitada | Presmed | Prestadores |
| 53 | N |  | Muestra los informes de afiliados consolidados entre Reintegros y Convenios, a su vez toma la fecha de liquidación en vez de la del período al generar el proceso batch de afiliados (impacta solo en el primer proceso), y el de gasto de prestadores. | S = Habilitada / N = Deshabilitada | Informes |  |
| 54 | N |  | Regla para actualizar la deuda de los comprobantes impagos y Generar un Resumen con una ND por los Intereses e incluir el Comprobante del periodo actual. | S = Habilitada / N = Deshabilitada | Afilmed | Cuenta Corriente |
| 55 | N |  | Uso Indebido | N = Inhabilitado / S = Habilitado | Presmed/Afilmed | Liquidaciones / Facturación |
| 56 | N |  | Prioridad en la validación de boletín protectivo (sólo escribanos) | S = si / N = no | Presmed | Autorizaciones |
| 57 | N |  | Hace visible el campo estado de afiliado en Solicitudes y permite visualizar la historia de los mismos en la ventana de Ficha del Afiliado | S = visible / N = no visible | Afilmed | Solicitudes |
| 57 | N |  | Validación de cobertura  (solo BPS) | S = Habilitada / N = Deshabilitada | Presmed | Autorizaciones |
| 58 | N |  | Interfaz con OpenSic para envio de datos de destajistas (solo BPS) | S = Habilitada / N = Deshabilitada | Presmed | Prestadores |
| 59 | N |  | Listados especificos para UOCRA.  También permite cargar en la ventana de Alta de Origenes si el origen importará afiliados con errores en la importación de Afiliados para UOCRA.  Habilita la ventana de Estados de la Documentación y Estados de Validación permitiendo cargar en Solicitudes dichos estados. | S = visible / N = no visible | Afilmed | Solicitudes |
| 59 | N |  | En BPS se usa para habilitar o no la importacion de consultas de prestadores destajistas desde el OpenSic |  | Presmed | Prestadores |
| 60 | N |  | Reporte de pacientes con tratamientos prolongados, que se le hizo a Abogados (farm/consultas/Pacientes con tratamientos prolongados) | S = visible / N = no visible | Presmed | Farmacia |
| 61 | N |  | Nuevo conjunto de indicadores de Farmacias. Ademas también deshabilita los reportes nuevos de tasas de uso y el de Afiliados que utilizaron | S = visible / N = no visible | Informes | Farmacia |
| 62 | N |  | Nuevo reporte de informes, Ranking de consumos de afiliados, se encuentra en Afiliados/Ranking de consumos de afiliados. | S = visible / N = no visible | Informes | Afiliados |
| 63 | N |  | Indica si en la Baja por Morosidad también se cancelan también los comprobantes de debito que aún tenga pendiente el afiliado | S = Si / N = No | Afilmed | Verifica |
| 64 | N |  | Indica si el proceso de verificación de Afiliados realiza el control de Baja por Morosidad | S = Si / N = No | Afilmed | Verifica |
| 65 | N |  | Indica si en el alta de cuentas y subcuentas permite dar de alta una cuenta con datos mínimos(solo cuit, razón social, domicilio,cod. Postal, tel., localidad, provincia). | S = Si / N = No | Afilmed | Empresa |
| 66 | 1 |  | Forma de carga de recetas y ordenamiento de recetas | 1,2 | Presmed | Farmacia |
| 67 | N |  | Envio de Ordenes de Pago de reintegros por email | S = Si / N = No | Presmed | Reintegros |
| 68 | N |  | Habilita para la UOCRA la carga de Grupos de Categorias de Prestadores | S = Si / N = No | Presmed | Prestadores / Datos del Prestador |
| 69 | N |  | Calculo de Intereses con las distintas tasas ingresadas según los dias que corresponda. | S = Si / N = No | Afilmed | Facturación |
| 70 | N |  | Envío de Encuestas a afiliados personalmente, por mail o por correo | S = Si / N = No | Afilmed |  |
| 71 | N |  | Permite anular comprobantes solo para el periodo actual de facturacion. | S = Si / N = No | Afilmed | Facturación |
| 72 | N |  | Habilita un comportamiento HARDCODE para el Británico en el cálculo de los copagos por orden | S = Si / N = No | Presmed | Autorizaciones |
| 73 | N |  | Determina si para la solicitud de Cbio. De Plan/Tarifa se generará credencial para el caso en que se mantenga el mismo plan y misma tarifa pero cambien los planes adicionales. | N=Solo si cambia el plan principal. / T=Si cambia la tarifa que igual genere credencial. / P=Si cambian los planes adicionales que igual que genere credencial. / A=Si cambia la tarifa y/o los planes adicionales que igual genere credencial. | Afilmed | Solicitudes |
| 74 | N |  | Permite administrar origen del afiliado, si no está habilitada se asigna un origen por default. | S = Si / N = No | Afilmed | Solicitudes |
| 75 | N |  | Habilita los dos reportes generados según el presupuesto 177 para escribanos | S = Si / N = No |  |  |
| 76 | N |  | Habilita la consulta por categoria de afiliados | S = Si / N = No |  |  |
| 77 | N |  | Habilita la consulta de expedientes desglosada | S = Si / N = No | Presmed | Liquidaciones |
| 78 | N |  | Habilita reporte de médicos de cabecera en Informes | S = Si / N = No |  |  |
| 79 | N |  | Inhabilita opciones de menú de farmacia para importacion sin auditorias | S = Si / N = No | Presmed | Farmacia |
| 80 | N |  | Habilita la ventana de Exportación de Afiliados y la ventana de Formato de Archivo de Exportación de Afiliados |  | Afilmed |  |
| 81 | N |  | Habilita la facturación por empresas y cobranza a traves del cajero para empresas | S = Si / N = No | Afilmed | Caja Empresas |
| 82 | N |  | Habilita o no la subida de troqueles que empiezan con '99' en el subedatos (en 'N' no habilita) | S = Si / N = No | Subedatos | Farmacia |
| 83 | N |  | Habilita en el ABM de oficinas liquidadoras el manejo de los numeros de expedientes y el formato de OP de liquidacion solicitado | S = Si / N = No | Presmed | Tablas |
| 84 | N |  | Autonumera los integrantes en la subida de afiliados con el SubeDatos | S = Si / N = No | Subedatos | Afiliados |
| 85 | N |  | Obviar el control de estado civil en el SubeDatos de afiliados | S = Obviar / N = No obviar | Subedatos | Afiliados |
| 86 | N |  | Genera una credencial para cada afiliado al subirlos con el SubeDatos. El código de la credencial será distinto de acuerdo al valor que tenga esta regla. | N = No / 1 = Nro. de documento | Subedatos | Afiliados |
| 87 | N |  | Separar el apellido y nombre en el subedatos | N = No / 1 = Apellido, Nombre | Subedatos | Afiliados |
| 88 | N |  | Pone un plan por defecto en el SubeDatos de afiliados | S = Si / N = No | Subedatos | Afiliados |
| 89 | N |  | Importa los datos de la empresa a la que pertenecen los afiliados en el SubeDatos. | N = No / EC = empre_categorías | Subedatos | Afiliados |
| 90 | N |  | Genera los comprobantes con fecha igual al periodo del comprobante | S = Si / N = No | Afilmed | Facturación |
| 91 | N |  | Toma el descuento del lote en vez del descuento del plan | S = Si / N = No | Presmed | Farmacia |
| 92 | N |  | Toma el descuento de la situacion terapeutica en vez del descuento del plan | S = Si / N = No | Presmed | Farmacia |
| 93 | N |  | Muestra la categoría del afiliado en la carga de recetas de farmacia. | S = Si / N = No | Presmed | Farmacia |
| 94 | N |  | Exportación de padrón de afiliados | S = Si / N = No |  |  |
| 95 | N |  | Cálculo de descuentos y topes para los reintegros de medicamentos | S = Si / N = No | Presmed | Reintegros |
| 96 | N |  | Búsqueda del afiliado al cargar 5 caracteres en contrato en las pantallas de carga de autoriz. y expedientes | S = Si / N = No | Presmed | Autorizaciones / Liquidaciones |
| 97 | N |  | Fechas de copagos en comprobantes, toma la fecha de la prestación y no la de prescripción | S = Si / N = No | Presmed | Autorizaciones |
| 98 | N |  |  |  |  |  |
| 99 | N |  | Habilita la opcion de menu de la Importación de cabecera de expedientes | N = No / S = Si / 1 = SI sólo para DIBA | Presmed | Liquidaciones/Carga de expedientes/Importación/Cabeceras de expedientes |
| 100 | N |  | Imprime las autorizaciones rechazadas | S = Si / N = No | Presmed | Autorizaciones |
| 101 | N |  | Permite editar los copagos en la carga de las autorizaciones | S = Si / N = No | Presmed | Autorizaciones |
| 102 | N |  | En la impresión de Autorizaciones, no muestra el diagnóstico, sino el código del mismo. | S = Si / N = No | Presmed | Autorizaciones |
| 103 | N |  | Muestra el menu de importaciones de nomencladores de medicamentos | S = Si / N = No | Subedatos | Farmacia |
| 104 | N |  | Muestra el semaforo con la identificacion del afiliado - Solicitado por Britanico | S = Si / N = No | Afilmed | Solicitudes |
| 105 | N |  | Muestra menú Clearing | S = Si / N = No | Presmed | Clearing |
| 106 | N |  | Imprimir los comprobantes por la descripción del responsable pagador | S = Si / N = No | Afilmed | Facturación |
| 107 | N |  | Muestra menú Carga de cheques y envíos Bank | S = Si / N = No | Afilmed |  |
| 108 | N |  | En autorizaciones, si está en S chequea si la prestacion ingresada ya fue rechazada en una autorización anterior. | S = Si / N = No | Presmed | Autorizaciones |
| 109 | N |  | Opción de contabilización | S = Si / N = No |  |  |
| 110 | N |  | Listados del ANSSAL (Res. 650) | S = Si / N = No |  |  |
| 111 | N |  | Consulta de expedientes exportados | S = Si / N = No | Presmed | Liquidaciones |
| 112 | N |  | Ingreso de sucursal y autorizacion via lector optico de codigo de barras | N = No / 1 = UOCRA | Presmed | Autorizaciones |
| 113 | N |  | Resumen de cobranzas por ente recaudador | S = Si / N = No | Afilmed | Cuenta Corriente |
| 114 | N |  | Reporte de estados de cuenta | S = Si / N = No | Afilmed | Cuenta Corriente |
| 115 | N |  | Exportacion al sist. Contable |  |  |  |
| 116 | N |  | Expedientes Automaticos por X.XX% para Cajas previsionales | S = Si / N = No | Presmed | Prestadores/ Caja Previsional - Liquidacion / Expedientes Liquidados / Consulta entre fechas |
| 117 | N |  | Dar de baja una autorización supervisada | S = Si / N = No | Presmed | Autorizaciones |
| 118 | N |  | Relacion de Grupos Fliares | S = Si / N = No | Afilmed | Solicitudes |
| 119 | N |  | Trae capita a la que pertenece el afiliado | S = Si / N = No | Presmed |  |
| 120 | N |  | Permite la carga de fecha real de baja al mes anterior de la Fecha aplica. En caso de esta regla en N solo permite la fecha real de baja al mismo mes que la de Aplica. | S = Si / N = No | Afilmed | Solicitudes |
| 121 | N |  | En 'S' permite cargar convenios de cápitas a cualquier tipo de prestador, menos circulos medicos (En 'N' sólo deja si son Coordinadores) | S = Si / N = No | Presmed | Convenios |
| 122 | N |  | En 'S' permite editar la cantidad de dias de internacion en ventana wp_expe_sana | S = Si / N = No | Presmed | Liquidaciones |
| 123 | S |  | En 'S' le permite generar intereses a las notas de credito | S = Si / N = No | Afilmed | Facturación |
| 124 | N |  | Aumento de tarifas por Plan | S = Si / N = No | Afilmed | Tarifas |
| 125 | N |  | Valor presupuestado de autorizaciones en Liquidaciones | S = Si / N = No | Presmed | Liquidaciones |
| 126 | N |  | En 'S' permite cargar subprestadores | S = Subprestador / N = No | Presmed | Prestadores / Datos del Prestador |
| 127 | N |  | En 'S' habilita Orden de Pago de Diba | S = si / N = no | Presmed | Liquidaciones |
| 128 | N |  | Hablilita la Caja | S = si / N = no | Afilmed | Caja |
| 129 | N |  | Habilita Interfase sap | S = si / N = no | Afilmed |  |
| 130 | N |  | Realiza autorizaciones múltiples | S = si / N = no | Presmed | Autorizaciones |
| 131 | N |  | Reintegro de Medicamentos por Drogas | S = si / N = no | Presmed | Reintegros |
| 132 | N |  | Resumen de Costo por Prestador por Periodo | S = si / N = no | Informes | Prestadores |
| 133 | N |  | Consumos por afiliado buscar por tipo y nro de documento | S = si / N = no | Presmed |  |
| 134 | N |  | Deshabilitar prestaciones para un convenio | S = si / N = no | Presmed | Convenios |
| 135 | N |  | Informe Costo por DRG por Sucursal | S = si / N = no | Presmed |  |
| 136 | N |  | Habilitacion del Campo Días sin convenio | S = si / N = no | Presmed |  |
| 137 | N |  | Habilita selección de bandeja de impresión de bonos | S = si / N = no | Presmed |  |
| 138 | N |  | Habilita mensaje de Cant.Sesiones ingresadas > autorizadas | S= Informativo / N = no informa / E= Muestra Error y no deja seguir | Presmed | Autorizaciones |
| 139 | N |  | Habilita diagnosticos en expe de ajustes | S= si / N = no | Presmed | Liquidaciones |
| 140 | N |  | Habilita Resumen para Prestador en expe de ajustes | S = si / N = no | Presmed | Liquidaciones |
| 141 | N | 634 | La numeracion de los bonos es por sucursal y por tipo de bono. | S = si / N = no | Presmed | Autorizaciones / Carga de Bonos. |
| 142 | N |  | Importa afiliados sin ceros a la izquierda (importación de liquidaciones) | S = si / N = no | Presmed | Liquidaciones |
| 143 | N |  | Indica si es la instalación de OSPe | S = si / N = no |  |  |
| 144 | N |  | Permite elegir entre mas de una categoria del Prestador en Expe de ordenes | S=si/ N = no | Presmed | Liquidaciones |
| 145 | N |  | Permite aumentar la couta 50% mas por SAC en Julio y diciembre. | S=si/ N = no | Afilmed | Facturación |
| 146 | N |  | Al importar afiliados, toma la fecha de ingreso de afiliados dados de baja. | S=si/ N = no | Subedatos | Afiliados |
| 147 | N |  | Esconder campos Nemonico y factor Apache de ICD | S = si / N = no | Presmed |  |
| 148 | N |  | Documentacion , Entidadades subsidiantes APE | S= si / N = no |  |  |
| 149 | N |  | Accede al menú para generar zz_menues (interno) | S= si / N = no |  |  |
| 150 | N |  | Permite cargar "Convenio Firmado" en la carga de prestadores. | S= si / N = no | Presmed | Prestadores |
| 151 | N |  | En la ventana de Generacion de Padrones para el clearing, muestra solo los coordinadores que pertenecen a la cartilla con el mismo codigo que la filial ingresada. | S= si / N = no | Presmed | Clearing |
| 152 | N |  | En reintegros solo muestra la sucursal a la que está asignado el usuario. | S= si / N = no | Presmed | Reintegros |
| 153 | N |  | Habilita Asociación de Diagnóstico con Situacion Terapeutica ( Se usa para APE) | S=si/ N = no | Presmed | Sit terap |
| 154 | N |  | Habilitacion Esquema Jerarquico (de titulos de capitulos) de ICD 10 | S=si/ N = no | Presmed |  |
| 155 | N |  | Situaciones Terapeuticas con Exigencia de confidencialidad |  | Presmed | Sit terap |
| 156 | N |  | Permitir ingresar expedientes para un período cerrado para estadisticas | S=si/ N = no | Informes |  |
| 157 | N |  | Subedatos: Impide la ejecución del proceso de afiliados no informados si existen afiliados sin procesar del periodo actual. | S=si/ N = no | Subedatos | Afiliados |
| 158 | S |  | Habilita el proceso batch unificado. | S=si/ N = no | Batch | Todas |
| 159 | N |  | Administración de Expediente de subsidios APE | S=si/ N = no | Presmed | Administracion de subsidios |
| 160 | N |  | Numera automaticamente el contrato | S=si/ N = no | Afilmed | Solicitudes |
| 161 | N |  | Oculta importacion de archivos | S=si/ N = no |  |  |
| 162 | N |  | Modulo de historias clínicas | S=si/ N = no | Presmed | Historias clínicas |
| 163 | N |  | Habilita Cajas archivadoras a expedientes | S=si/ N = no | Presmed | Liqudaciones/ Consulta expe liquidados |
| 164 | N |  | Permite modificar la fecha en la ficha del afiliado. | S=si/ N = no | Todos | Ficha Afiliado |
| 165 | N |  | Muestra los errores de la validación del integrante en la ficha del afiliado. | S=si/ N = no / M = nuevo modulo de morosidad | Todos | Ficha Afiliado |
| 166 | N |  | Muestra el campo localidades en el reporte costo por planes | S=si/ N = no | Informes | Afiliados/Costo Por Planes |
| 167 | N |  | Asociacion de Diagnosticos con Prestaciones APE | S=si/ N = no | Presmed | Sit terap |
| 168 | N |  | Muestra el ranking de Prestadores - Prestaciones más facturadas por periodo. | S=si/ N = no / O = Osplad | Informes | Prestaciones / Ranking de Prestadores-Prestaciones Más Facturadas por Periodo |
| 169 | N |  | Recalcula el valor de las recetas y el monto pagado por el afiliado al realizar la importacion. | S=si/ N = no | Presmed | Farmacia |
| 170 | N |  | Autorizaciones de drogas | S=si/ N = no | Presmed | Autorizaciones |
| 171 | N |  | Modulo de ambulancias | S/N | Presmed | Ambulancias |
| 172 | N |  | Ignora los intereses posteriores al último vencimiento del comprobante. | S = si / N = no | Afilmed |  |
| 173 | N |  | Agrupa el informe de Costo por Prestador por Oficina Liquidadora | S = si / N = no | Presmed | Liquidaciones / Informes / Costo por Prestador |
| 174 | N |  | Permite visualizar en el informe Prestacion por Prestador los prestadores efectores. | S = si / N = no | Presmed | Liquidaciones / Informes / Prestacion por prestador |
| 175 | N |  | Cambia en prestadores el label: de 'Abreviatura' a 'Denominación Cartilla' | S=si/ N = no | Presmed | Prestadores / Datos del Prestador |
| 176 | N |  | Valida los porcentajes de aportes por empresa | S=si/ N = no | Afilmed | Empresa |
| 177 | N |  | Genera una autorizacion por cada traslado en ambulancia ingresado. | S=si/ N = no | Presmed | Ambulancias / Ingreso de pedidos |
| 178 | N |  | Utiliza el modulo de autorizaciones remotas y liquidación de expedientes de origen remoto | S = si / N = no | Presmed | Liquidaciones / Expedientes de origen remoto |
| 179 | N |  | Valida el promotor | S = si / N = no | Afilmed | Solicitudes |
| 180 | N |  | Valida cuil | S = todos / N = ninguno / D = deriva / T = titular | Afilmed | Solicitudes |
| 181 | S |  | Permite la modificacion del porcentaje de reintegro de los medicamentos. | S = si / N = no | Presmed | Reintegros |
| 182 | N |  | Carga manualmente el numero de historia clínica externa | S = si / N = no | Presmed | Historias clínicas |
| 183 | N | 2236 | Recalculo automatico de conceptos de prestaciones dentro de un convenio | S=si/ N = no | Presmed | Convenios |
| 184 | N |  | Validación de ingreso de campos Grupo de Pago, CUIT, Cheque a la orden para prestadores Profesionales | S=si/ N = no | Presmed | Prestadores / Datos del Prestador |
| 185 | S |  | Permite Liquidar | S=si/ N = no | Presmed | Liquidaciones |
| 186 | N |  | Prorrateo de los reintegros en varias cuotas cuando se pagan como Debito en Cuenta Corriente del Afiliado | S=si/ N = no | Presmed | Reintegros |
| 187 | S | no | Permite Facturar | S=si/ N = no | Afilmed | Facturación |
| 188 | N | 2197 | Visualiza el logo en la Impresión de la cabecera del expediente de liquidacion.- | S=si/ N = no | Presmed | Liquidaciones |
| 189 | N |  | Permite la carga de historias clinicas para todos los tipos de autorizaciones. | S=si/ N = no | Presmed | Autorizaciones |
| 190 | N | 2431 | Permite cargar prestaciones en autorizaciones de tipo cirugia | S=si/ N = no | Presmed | Autorizaciones |
| 191 | S | 2431 | Muestra el valor de los copagos al imprimir la copia de la autorizacion para el prestador. | S=si/ N = no | Presmed | Autorizaciones |
| 192 | S | 2431 | Muestra el campo medicamentos y descartables en la copia de la autoizacion para el sanatorio. | S=si/ N = no | Presmed | Autorizaciones |
| 193 | N | 2507 | Anexo I: Calcula la jurisdiccion de cada afiliado buscando la localidad del domicilio vigente. | S=si/ N = no | Presmed | Supervision de expedientes de ordenes y sanatorios. |
| 194 | R | 2566 | Autorizaciones: Estado que se asigna a la autorizacion o al item cuando existe un error en la validacion del afialido. | P = Pendiente / R = Rechazada / A = Aceptado | Presmed | Autorizaciones |
| 195 | N | 2537 | No se le calcula el IVA a los afiliados desregulados. | S=si/ N = no | Afilmed / Presmed | Afilmed: Facturacion (Generacion de Comprobantes) / Presmed: Clearing, Liquidacion de expedientes |
| 196 | N | 2111 | Restricciones adicionales en la carga de Prestadores | S=si/ N = no | Presmed | Prestadores / Datos del Prestador |
| 197 | N | 2600 | Genera recibo con el mayor período de/los comprobante/s pagado/s | S=si/ N = no | Presmed |  |
| 198 | N | 2390 | La organización debe emitir facturas electronicas. | S=si/ N = no | Afilmed | Facturación |
| 199 | N | 2390 | Permite la impresión de un comprobante sin que posea el CAE exigido por la AFIP. | S=si/ N = no | Afilmed | Facturación |
| 200 | N | 2204 | No deja cargar dif. Origen al grupo | S=si/ N = no | Afilmed | Solicitudes |
| 201 | N | 2237 | Valida fecha de ingreso con la fecha de aplica | S=si/ N = no | Afilmed | Solicitudes |
| 202 | N | 2674 | Valida cuit repetido en la carga de cuenta | S=si/ N = no | Afilmed | Empresa |
| 203 | S | 2657 | Trae o no el mismo numero de contrato en una reafiliación al cargar el DNI | S=si/ N = no | Afilmed | Solicitudes |
| 204 | N |  | Posibilidad de trabajar conectado a Opensic o no (para BPS) | S=si/ N = no | Presmed | Todo el sistema |
| 205 | N | 2271 | grabar en la tabla aju_cta_subcta para OS | S=si/ N = no | Afilmed | Empresa |
| 206 | N | 2670 | Le pasa la prepaga a la busqueda por tipo y nro de documento | S=si/ N = no | Afilmed | Solicitudes |
| 207 | N | 2652 | Permite la carga de prestadores con matricula duplicada. | S=si/ N = no | Presmed | Prestadores / Datos del Prestador |
| 208 | N | 2459 | Permite obtener la prov. En la factura | S=si/ N = no | Afilmed | Facturación |
| 209 | 2 | 2790 | Nivel minimo para modificar el estado | N, 0, 1 o 2 | Presmed | Autorizaciones |
| 210 | N | 469 | Visualiza ciertos datos en la solicitud para la Superintendencia Salud, y controla que su carga sea obligatoria. |  | Afilmed | Solicitudes |
| 211 | N | 2667 | Se Visualiza el valor de copago x item y copagos x orden. En listado global de autorizaciones. | S=si/ N = no | Presmed | Autorizaciones |
| 212 | N | 2487 | Muestra el Reporte de Utilización de Servicios por Distrito y Afiliado | S=si/ N = no | Informes | Afiliados/Reporte de utilizacion de &Servicios por Distrito y Afiliado |
| 213 | N | 2666 | Se calculan los intereses para los comprobantes vencidos según la última fecha de vencimiento del último comprobante generado | S=si/ N = no | Afilmed | CtaCte y Caja |
| 214 | N | 1495 | Calculo de valores de convenio con instrumentadora | S=si/ N = no | Presmed | Liquidaciones |
| 215 | N | 469 | Opción de Superintendencia | S = Si / N = No | Afilmed | Solicitudes |
| 216 | N | 2642 | En la base de un comprobante pone los copagos como libres para asignarse a otros comprobantes. | S = Si / N = No | Afilmed | Cuenta Corriente / Anulacion de comprobantes. |
| 217 | N | 2334 | Se toma como "fecha desde" para el calculo de los intereses la fecha del 1er vencimiento de los comprobantes | S = Si / N = No | Afilmed | CtaCte y Caja |
| 218 | N |  | Administración de Expediente de subsidios |  | Presmed | Administracion de subsidios |
| 219 | N | 2996 | Permite visualizar una leyenda determinada. | S=si/ N = no | Presmed | Impresión de Notas de Debitos |
| 220 | W | 2390 | Metodo para obtener el CAE de la AFIP. | W= WebServices / R = Aplicativo Rece | Afilmed | Facuturacion / Facturacion Electronica |
| 221 | N |  | Informa que el afiliado pertenece a otra jurisdiccion. | S=si/ N = no | Presmed/Afilmed | Autorizaciones / Liquidaciones |
| 222 | N | 2932 | Oculta el campo Gravado/Exento | S=si/ N = no | Presmed | Liquidacion / Supervision /Clearing / Generacion de Padron |
| 223 | N | no | Es para determinar que comprobantes tomo | S=si/ N = no | Afilmed | cuenta Corriente / Importacion de cobranzas. |
| 224 | N |  | restringir la identificación del prestador mediante la carga de su nro de cuit. | S=si/ N = no | Presmed | Liquidacion/Cabecera de expediente de liquidacion |
| 225 | N | 3059 | Al modificar un expediente en carga permite editar el campo recep_fecha | S=si/ N = no | Presmed | Liquidaciones |
| 226 | N |  | Sin logos en Impresiones de autorizacion | S=si/ N = no | Presmed | Autorizaciones |
| 227 | N | 3067 | Controla si es desregulado con los aportes | S=si/ N = no | Afilmed | Solicitudes |
| 228 | N | 3120 | Lotes de Reintegros: Muestra solo los reitnegros en proceso de carga. | Lotes de Reintegros: Muestra solo los reitnegros en proceso de carga. | Presmed | Reintegros / Lotes de reintegros. |
| 229 | S | 3133 | Reintegro: El número y tipo de documento es obligatorio. | S=si/ N = no | Presmed | Reintegros / Carga de Reintegros |
| 230 | S | 3141 | Nota de Debito: impresión del detalle en el comprobante. | S=si/ N = no | Presmed | Supervision de expedientes / Impresión de nota de debito |
| 231 | N | 2349 | Utiliza el nuevo Modulo de Morosidad. | S = Si / N = No | Afilmed | Instalacion |
| 232 | N | 1846 | ABM de Aportes | S = Si / N = No | Afilmed | Instalacion |
| 234 | N |  |  |  |  |  |
| 235 | N | 3189 | Impedir la consulta de autorizaciones de otras sucursales. | S=si/ N = no | Presmed | Autorizaciones / Carga - Busqueda - Listado Global - Impresión de Censos |
| 236 | N | 2266 | No toma los aportes importados, solamente se los estima atraves de un calculo. Impide ver los aportes | S=si/ N = no | Afilmed | factu - test cuota |
| 237 | N | 1813 | Resta 6 meses los asientos contables | S=si/ N = no | Afilmed | Generacion de asientos contables |
| 238 | N |  | Disposiciones de pago | S=si/ N = no | Presmed |  |
| 239 | N | 3262 | Reintegros: Al imprimir la orden de pago ignora el tipo de domicilio y busca el más reciente. | S=si/ N = no | Presmed | Reintegros |
| 240 | N |  | Nro de Mesa entrada en Autorizaciones | S=si/ N = no | Presmed | Autorizaciones |
| 241 | N | 2271 | Visualiza en el menu empresa\\importacion de archivos de afip\\actualizacion de remuneraciones | S=si/ N = no | Afilmed | Empresa |
| 242 | N | 2829 | Tomo Copagos solo en la facturación masiva | S=si/ N = no | Afilmed | Facturación |
| 243 | N |  | Valida edad tope del plan con la edad de afiliado | S=si/ N = no | Afilmed | Solicitudes |
| 244 | N |  | Prioridad en la validación del convenio (prestador / circulo) | S=si/ N = no | Presmed | Autorizaciones |
| 245 | N | 3361 | Valida tipo y nro de doc | S=si/ N = no | Afilmed | Solicitudes |
| 246 | N | 3384 | Valida que no se vuelva a importar archivo afip | S=si/ N = no | Afilmed | Empresa |
| 247 | S | 3340 | Se pone como Default que se calculen intereses en la pantalla de carga de subcuentas | S=si/ N = no | Afilmed | Empresa |
| 248 | N |  | Configuracion por defecto en carga de prestadores por sector | S=si/ N = no | Presmed | Prestadores / Datos del Prestador |
| 249 | N | 1235 | Permite la supervision de expedientes Globales, Globales Capitados y de Honorarios Fijos sin comprobante. | S=si/ N = no | Presmed | Liquidacion / Supervision |
| 250 | N |  | Cumplido de Autorizaciones | S=si/ N = no | Presmed | Autorizaciones/Cumplido de Autorizaciones |
| 251 | N | 3442 | Que no genere creden para soli_moti = 5 | S=si/ N = no | Afilmed | Pasaje a afliaciones |
| 252 | N | 3421 | Utiliza Lotes de Reintegros | S=si/ N = no | Presmed | Reintegros / Lotes de reintegros. |
| 253 | N | 3421 | Reintegros: Utiliza el modo de Administracion | S=si/ N = no | Presmed | Reintegros / Administracion |
| 254 | N | 2960 | Imprimo el nuevo formato de autorizaciones para MAPFRE | S=si/ N = no | Presmed | Autorizaciones |
| 255 | N | 3153 | Consulta de expedientes altas bajas | S=si/ N = no | Presmed | Autorizaciones |
| 256 | N | 3153 | Posibilidad de ingresar motivo de anulacion de expedientes | S=si/N=no | Presmed/Afilmed | Liquidaciones/Facturacion |
| 257 | N | 3543 | Reintegros: modelo de la orden de pago | N=Normal/P=Con prestaciones y comprobantes. | Presmed | Reintegros |
| 258 | N | 3543 | Reintegros: Imprime los campos del sellos en el modelo de la orden de pago con prestaciones y comprobantes. | S=si/N=no | Presmed | Reintegros |
| 259 | N | 3593 | Solo permite la emisión de bonos para el titular del grupo familiar. | S=si/N=no | Presmed | Autorizaciones / Carga de Bonos. |
| 260 | N | 3087 | la busqueda se realiza por ciut | S=si/N=no | Presmed | liquidacion / carga de expedientes / ingreso |
| 261 | N | 3599 | Cambia la leyenda de subsidios por bonificaciones en el listado de detalle en la facturación por empresa | S=si/N=no | Afilmed | Empresa / Facturacion por empresa |
| 262 | N | 3617 | Permite cargar un reintegro sin items. | S=si/N=no | Presmed | Reintegros |
| 263 | N | 3121 | Permite visualizar los primeros 11 caracteres | S=si/N=no | Afilmed | Solicitudes |
| 264 | N | 3659 | Controla datos en soli de cambio de datos personales | S=si/N=no | Afilmed | Solicitudes |
| 265 | N | 3758 | Deja la baja fecha de los ajustes internos nula | S=si/N=no | Afilmed | CtaCte/Anulacion de comprob. |
| 266 | N | 2846 | Imprime cuadruplicado de nota de débito para Escribanos y 2 copias del Resumen para Contaduría y 2 copias del Resumen del detalle para el prestador. | S=si/N=no | Presmed | Liquidaciones / Supervisión para cierre de liquidación / Sanatorios y Ordenes/ botón Aceptar, al confirmar la supervisión |
| 267 | N | 3554 | relacion entre integrante y genero | S/ N | Afilmed | Instalacion |
| 268 | N | 3829 | cambios en el reporte infromes facturados | S/N | Afilmed | - |
| 269 | N | 3831 | se muetsra en integrante en informe de deudores | S/N | Afilmed | - |
| 270 | N | 2436 | presupuesto 383 estado de cuenta actualizado | S/N | Afilmed | - |
| 271 | N | 3865 | 0003865: Problemas con debitos en expedientes. | S/N | Presmed | Liquidaciones/Carga de expedientes/Circuito de Carga |
| 272 | N | 4029 | 4029: restringir la fecha de del comprobante | S/N | Presmed | Liq. Expedientes |
| 273 | N | 2991 | Se cambie la leyenda de “Débito Global” por “Débitos Globales/ Coseguros”. | S/N | Presmed | Liq. Expedientes |
| 274 | N | 4107 | Regla para carga de solicitudes | S/N | Afilmed | Solicitudes |
| 275 | N | 4157 | En S, permite cargar un valor global capitado aunque el convenio no sea capitado. | S/N | Presmed | Convenios/Carga de Convenios/Valores. |
| 276 | N | 4142 | En S permite restablecer, al salir de la aplicación,  la configuración regional que tenía el equipo antes de iniciar la aplicación. Funciona en Presmed e Informes. Pedido por Diba. | S/N | Presmed / Informes | - |
| 277 | N | 4146 | En S, al cargar un exte. Con errores el sistema asigna x default el total de la orden, y si no existe error calcula la diferencia entre los ingresado y lo convenido. (MBulla) | S/N | Presmed | Liquidaciones / Circuito de carga |
| 278 | N | 4198 | En S permite, en las autorizaciones de "situacion terapeutica" cuando se seleccione la opcion "impresion completa" en la misma aparezca el codigo de la sitaucion terapeutica Pedido por Diba. | S/N | Presmed | Autorizaciones/Carga de Autorizaciones |
| 279 | N | 4243 | En S calcula el IIBB con el importe | S/N | Afilmed | - |
| 280 | S | 4030 | En N no se ve la solapa de valor Cuota y saldo en la ficha del afiliado | S/N | Afilmed |  |
| 281 | N | 4458 | Regla para la ficha del afiliado | S/N | Afilmed | Solicitudes / Ficha del afiliado |
| 282 | N | 3984 | Regla para Reglas de Afiliacion | S/N | Afilmed | Instalacion/Reglas de afiliacion |
| 283 | N | 3725 | Regla para ver por menú pantalla Cancelación de Saldos | S/N | Afilmed | Cuentas Corrientes / Cancelación de Saldos |
| 284 | S | 4594 | Pedido de Celer, no quieren que se generen NC cuando el aporte es superior a la uota | S/N | Afilmed |  |
| 286 | N | 4521 | Pedido de Britanico. | S/N | Afilmed | Solicitudes/Formatos de archivo de exportación de Padrón |
| 287 | N | 4478 | Pedido de Britanico. | S/N | Afilmed |  |
| 288 | N | 4355 | Pedido de Britanico. | S/N | Afilmed | Solicitudes/Carga de Solcitudes |
| 289 | N | 4483 | Pedido de Britanico. Permite la carga y visualización de mails de los afiliados. | S/N | Afilmed | Solicitudes/Carga de Solcitudes  y   Ficha del Afiliado |
| 290 | N | 4419 | Si está en N, existe una sola ventana de Supervisión de Reintegros en la cual se pueden editar datos. Si está en S (pedido por Escribanos), existen dos ventanas: una como la anteriormente mencionada pero denominada "Supervisión con Edición", y otra idéntica, llamada "Supervisión", pero donde sólo se puden modificar datos en la solapa de Supervisión, si el estado del reintegro es "Derivado a Supervisión". | S/N | Presmed | Reintegros/Supervisión    y                                        Reintegros/Supervisión con Edición. |
| 291 | N | 4752 | Pedido de Britanico. | S/N | Presmed | Autorizaciones/Autorizaciones |
| 292 | N | 5165 4600 | Formas de pago para reintegros. | S/N | PresMed | Reintegros |
| 293 | N | 4757 | Cambios en la pantalla de auditoría de Terrenos por "Evolución de Historia Clinica" y ABM de Adecuacion /Inadecuac d epacientes internados | S/N | PresMed | Autorizaciones / Censos / Auditoria de terreno |
| 294 | N | 4756 | Se agrega el campo sala en en censo , pedido por el britanico | S/N | PresMed | Autorizaciones / Censos |
| 295 | N | 5310 | Se agrega un nuevo formato de impresión de bono | S/N | PresMed | Autorizaciones / Censos |
| 296 | N | 5323 | Emision de resumenes de debitos para coordinadores y circulos | S/N | PresMed | Liquidaciones |
| 297 | S | 5581 | Modulo Liquidaciones | S/N | Presmed | Liquidaciones |
| 298 | S | 5581 | Modulo Autorizaciones | S/N | Presmed | Autorizaciones |
| 299 | S | 5581 | Modulo Situacion Terapeutica | S/N | Presmed | Situación Terapéutica |
| 300 | S | 5581 | Modulo Mesa de Entrada | S/N | Presmed | Mesa de Entrada |
| 301 | S | 5581 | Modulo Clinica | S/N | Presmed | Clinica |
| 302 | S | 5581 | Modulo Empresas | S/N | Afilmed | Empresas |
| 303 | S | 5581 | Modulo Facturacion | S/N | Afilmed | Facturación |
| 304 | S | 5581 | Modulo Ctas. Corrientes | S/N | Afilmed | Cuentas Corrientes |
| 305 | S | 5581 | Modulo Tarifas | S/N | Afilmed | Tarifas |
| 306 | S | 5581 | Modulo Cajas | S/N | Afilmed | Caja |
| 307 | S | 5133 | Reintegros | S/N | Presmed | Reintegros Recepcion/ Edicion /Supervicion/Consulta/Administracion |
