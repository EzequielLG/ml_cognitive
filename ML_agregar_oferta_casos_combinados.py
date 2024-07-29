def agregar_oferta_casos_combinados(entrada, campus, generacion):
    """
    Esta función se encarga de agregar oferta nueva de programas a nivel entrada-campus-generacion.
    Requiere la creación de la vista AGREGAR_OFERTA para la generación actual.
    Parámetros:
    -entrada: string con la entrada que se va a trabajar
    -campus: string con el nombre del campus a trabajar
    -generacion: string con la generación donde comienza la oferta 
    """
    # Duda 6
    # ¿SUM(A.TOTAL_AGRUPACION) es el total de la agrupación actual para cada programa dentro
    # de un mismo semestre de avance en la entrada y generación donde se desea agregar oferta?, 
    # agrupándose además por el parámetro que indica si es un programa de clínica o no

    # Duda 7
    # ¿B.TOTAL_INICIAL es el total de la agrupación inicial para cada programa en la entrada
    # y generación donde se desea agregar oferta?, agrupándose además por el parámetro que 
    # indica si es un programa de clínica o no
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW TASAS_PROGRAMAS AS
        SELECT SUM(A.TOTAL_AGRUPACION) AS TOTAL_AGRUPACION_PROGRAMAS,
        SUM(A.TOTAL_AGRUPACION) / FIRST(B.TOTAL_INICIAL) AS TASAXPIN_PROGRAMAS,
        A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMATERM, A.ES_CLINICA
        FROM (
            SELECT * 
            FROM {2}
            WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND GENERACION = '{1}') A 
        CROSS JOIN (
            SELECT SUM(TOTAL_AGRUPACION) AS TOTAL_INICIAL
            FROM {2}
            WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND GENERACION = '{1}' AND SEMESTRE_AVANCE_GENERACION = 1) B 
        GROUP BY A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMATERM, A.ES_CLINICA
    """.format(entrada, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Duda 8
    # ¿Si se debe borrar "total_inicial" y "total_agrupacion" entonces de qué manera se debería
    # obtener la TASAxPIN de los programas existentes?, ¿se deben borrar dichos campos o solo
    # no se deben utilizar en este módulo?

    # Se obtienen los factores de los programas nuevos que aplican para este campus-entrada-generacion
    df_factores_programa_campus = df_factores_programas_nuevos.where(
        (col('CAMPUS') == campus) & 
        (col('GENERACION') == generacion) & 
        (col('ENTRADA') == entrada)
    )
    df_factores_programa_campus.createOrReplaceTempView("FACTORES_TEMP")
    
    # Duda 9
    # ¿Por qué se utiliza la tabla de tasas en vez de la vista temporal "TASAS_PROGRAMAS" para
    # obtener los factores de los programas de los que NO se tiene información histórica de tasas?

    # Se obtienen solo los factores de programas de los que NO se tiene información histórica de tasas
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW FACTORES AS
        SELECT * FROM FACTORES_TEMP WHERE PROGRAMA NOT IN (
            SELECT PROGRAMATERM 
            FROM {2}
            WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND GENERACION = '{1}')
    """.format(entrada, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Si solo se añaden programas nuevos, entonces usamos el promedio de
    # tasas para programas dentro del campus en lugar del nacional,
    # es decir, se remplaza la vista de TASAS_PROGRAMAS

    # Duda 10
    # ¿La consulta regresa el conteo de los programas que SÍ existen ya históricamente?, por lo que, si la cantidad de programas
    # que sí existen ya, es igual a cero, ¿entonces solo hay programas completamente nuevos a añadir?
    if spark.sql("""
        SELECT * 
        FROM AGREGAR_OFERTA 
        WHERE CAMPUS = '{0}' AND ENTRADA = '{1}' AND OFERTA > ANTERIOR AND PROGRAMA NOT IN (
            SELECT PROGRAMA 
            FROM FACTORES 
            WHERE PROGRAMA IS NOT NULL)
    """.format(campus, entrada)).count() == 0:
        
        print('\tSolo programas nuevos')
        # Duda 11
        # ¿Es necesario utilizar la función "FIRST(x)"?, ya que, la tabla B tiene un único registro y, por ende,
        # al hacer el "CROSS JOIN" se añade un único valor en una nueva columna a la tabla A
        spark.sql("""
            CREATE OR REPLACE TEMP VIEW TASAS_PROGRAMAS AS
            SELECT SUM(A.TOTAL_AGRUPACION) AS TOTAL_AGRUPACION_PROGRAMAS,
            SUM(A.TOTAL_AGRUPACION) / FIRST(B.TOTAL_INICIAL) AS TASAXPIN_PROGRAMAS,
            A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMATERM, A.ES_CLINICA
            FROM (
                SELECT * 
                FROM {3}
                WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND GENERACION = '{1}' AND CAMPUS_PIN = '{2}') A 
            CROSS JOIN (
                SELECT SUM(TOTAL_AGRUPACION) AS TOTAL_INICIAL
                FROM {3}
                WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND GENERACION = '{1}' AND CAMPUS_PIN = '{2}' AND SEMESTRE_AVANCE_GENERACION = 1) B 
            GROUP BY A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMATERM, A.ES_CLINICA
        """.format(entrada, generacion, campus, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Se suman los factores de los programas nuevos (no se tiene información histórica) 
    # a añadir en la entrada
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW SUMARIZADO_FACTORES AS 
        SELECT ENTRADA, SUM(FACTOR) AS FACTOR
        FROM FACTORES
        GROUP BY ENTRADA
    """)

    # En caso de que se añadan programas nuevos (Sin información histórica)
    # Se recalculan las tasas_programa añadiendo los programas y tomando los factores en cuenta
    if spark.sql("""
        SELECT * 
        FROM FACTORES
    """).count() > 0:

        semestre_maximo = spark.sql("""
            SELECT MAX(SEMESTRE_AVANCE_GENERACION) as maximo 
            FROM TASAS_PROGRAMAS
        """).first().maximo
        # Duda 12
        # ¿Por qué en una de las subconsultas el "SELECT" incluye la entrada, si este campo no se utiliza
        # para la creación del posterior dataframe?

        # Duda 13
        # ¿Por qué en una de las subconsultas se suman los factores?, ya que, los registros en la tabla temporal 
        # "FACTORES" son únicos para cada entrada-programa en un campus y generación específicos, por lo que, al usar
        # la suma solo se están obteniendo los valores originales de los factores

        # Duda 14
        # ¿Una de las subconsultas sirve para crear los datos históricos de los nuevos programas en cada uno de los 
        # semestres de la oferta "actual", tomando como base el semestre máximo de oferta en un campus-entrada-generación 
        # dados, siendo los factores de absorción la materia prima de dicho proceso?

        # Duda 15
        # En caso de que sí, ¿por qué se toma como base el semestre máximo de oferta en el campus-entrada-generación, 
        # sin tomar en cuenta la oferta que se desea en el archivo de entrada de Excel?, es decir, se podría desear 
        # que un nuevo programa "X" se oferte hasta el semestre 3, pero debido a que un programa "Y" (existente)
        # de la misma entrada que "X" se ofrece hasta el semestre 7, entonces se estarían creando registros sobrantes

        # Duda 16
        # ¿Esta operación "A.TASAXPIN_PROGRAMAS * B.SUMA_TASAXPIN_PROGRAMAS" cómo funciona?, ¿cuál es la importancia 
        # a detalle de dicha operación?, ¿obtener la TASAXPIN de adopción de un programa respecto a la TASAXPIN total, en 
        # determinado campus-entrada-generación?

        # Duda 17
        # ¿Qué pasa con los campos "A.PROGRAMATERM" y "A.PROGRAMA" al hacer el "UNION ALL"?, ¿esta discrepancia 
        # qué genera?

        # Duda 18
        # ¿Al término de esta consulta el valor de "TOTAL_AGRUPACION_PROGRAMAS" para los nuevos programas es de cero?, 
        # en caso de que sí, ¿por qué esto es así?, ¿no se podría multiplicar la "TASAXPIN_PROGRAMAS" por cien?
        spark.sql("""
            --Se actualizan las tasas históricas para remover la población que pasará a formar parte
            --de los nuevos programas
            CREATE OR REPLACE TEMP VIEW TASAS_PROGRAMAS_AJUSTADAS AS (
                SELECT A.TOTAL_AGRUPACION_PROGRAMAS * (1 - B.FACTOR) AS TOTAL_AGRUPACION_PROGRAMAS, 
                A.TASAXPIN_PROGRAMAS * (1 - B.FACTOR) AS TASAXPIN_PROGRAMAS,
                A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMATERM, A.ES_CLINICA
                FROM TASAS_PROGRAMAS A 
                CROSS JOIN SUMARIZADO_FACTORES B
            )

            --Se calcula el valor que le corresponde a las tasas de los nuevos programas
            UNION ALL (
                SELECT A.TOTAL_AGRUPACION_PROGRAMAS, 
                A.TASAXPIN_PROGRAMAS * B.SUMA_TASAXPIN_PROGRAMAS AS TASAXPIN_PROGRAMAS, 
                A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMA, A.ES_CLINICA
                FROM ((
                    SELECT 0 AS TOTAL_AGRUPACION_PROGRAMAS, A.FACTOR AS TASAXPIN_PROGRAMAS,
                    B.SEMESTRE_AVANCE_GENERACION, A.PROGRAMA, FALSE AS ES_CLINICA
                    FROM (
                        SELECT ENTRADA, PROGRAMA, SUM(FACTOR) AS FACTOR
                        FROM FACTORES
                        WHERE ENTRADA = '{0}' AND CAMPUS = '{1}' AND GENERACION = '{2}'
                        GROUP BY ENTRADA, PROGRAMA) A 
                    --Se generan los registros para todos los semestres
                    CROSS JOIN (
                        SELECT A.ID AS SEMESTRE_AVANCE_GENERACION 
                        FROM RANGE(1, {3} + 1) A
                    ) B
                )) A 
                --Se unen los factores de programas nuevos con los de los promedios nacionales
                --para hacer los cálculos de tasas
                LEFT JOIN (
                    SELECT SUM(TASAXPIN_PROGRAMAS) AS SUMA_TASAXPIN_PROGRAMAS, SEMESTRE_AVANCE_GENERACION 
                    FROM TASAS_PROGRAMAS
                    GROUP BY SEMESTRE_AVANCE_GENERACION) B
                ON A.SEMESTRE_AVANCE_GENERACION = B.SEMESTRE_AVANCE_GENERACION
            )
        """.format(entrada, campus, generacion, semestre_maximo))
    else:
        # En caso de no haber programas nuevos, se usan los promedios nacionales como se tenían en un inicio
        spark.sql("""
            CREATE OR REPLACE TEMP VIEW TASAS_PROGRAMAS_AJUSTADAS AS
            SELECT * 
            FROM TASAS_PROGRAMAS
        """)
    # Se obtienen las tasas de transferencia del campus

    # Duda 19
    # ¿Por qué se obtienen las tasas de transferencias por generación-campus y no por 
    # generación-campus-entrada?, ¿esto es porque los alumnos a lo largo del tiempo 
    # pueden cambiar de entrada y por ende filtrar dicha entrada es en términos de 
    # reglas de negocio incorrecto?
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW TASAS_TRANSFERENCIAS AS
        SELECT SUM(A.TOTAL_AGRUPACION) AS TOTAL_AGRUPACION_TRANSFERENCIAS,
        SUM(A.TOTAL_AGRUPACION) / FIRST(B.TOTAL_INICIAL) AS TASAXPIN_TRANSFERENCIAS,
        A.SEMESTRE_AVANCE_GENERACION, A.CAMPUS_INDICADOR, A.CAMPUS_INSCRIPCION, 
        A.TRANSFERENCIA, A.TRANSFERENCIA_TEMPORAL
        FROM (
            SELECT * 
            FROM {2}
            WHERE CAMPUS_PIN = '{0}' AND GENERACION = '{1}') A 
        CROSS JOIN (
            SELECT SUM(TOTAL_AGRUPACION) AS TOTAL_INICIAL
            FROM {2}
            WHERE CAMPUS_PIN = '{0}' AND GENERACION = '{1}' AND SEMESTRE_AVANCE_GENERACION = 1) B 
        GROUP BY A.SEMESTRE_AVANCE_GENERACION, A.CAMPUS_INDICADOR, A.CAMPUS_INSCRIPCION, A.TRANSFERENCIA, A.TRANSFERENCIA_TEMPORAL
    """.format(campus, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Nos aseguramos de borrar las tasas anteriores para insertar las nuevas
    spark.sql("""
        DELETE FROM {3}_temp 
        WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND CAMPUS_PIN = '{1}' AND GENERACION = '{2}';
    """.format(entrada, campus, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Finalmente se insertan los nuevos registros haciendo un join de:
    # 1. Las tasas calculadas para los programas del campus
    # 2. Las tasas calculadas de las transferencias
    # 3. La oferta disponible para esta generación.
    #    Así, solo mantenemos las transferencias válidas. Si hay una
    #    Transferencia al campus A de un programa X en el semestre N, 
    #    con la oferta disponible nos aseguramos de que solo se incluya 
    #    la transferencia si el campus A tiene disponible el programa 
    #    X en el semestre N.

    # Duda 20
    # ¿Por qué se eliminan y se insertan de nuevo todos los registros en vez de actualizar 
    # los que ya existen?

    # Duda 21
    # ¿Cuál es la estructura y función de la ventana "WIN"?

    # Duda 22
    # ¿Cómo funcionan los "'{x}'" en el SELECT?

    # Duda 23
    # ¿Qué significan los valores constantes "1", "0" y "0" en el SELECT?

    # Duda 24
    # ¿En qué casos el cálculo de la TASAxPIN es nulo?, ¿en caso de que dicho cálculo sea nulo por 
    # qué su valor debe ser cero?, ¿esto cómo afecta los registros?

    # Duda 25
    # ¿Cómo sirve la función "DOUBLE(NULL)"?, ¿la tasa proporcional qué valor inicial está 
    # adquiriendo?

    # Duda 26
    # ¿Por qué se usa "FIRST(OFERTA)" si cada registro programa-campus-entrada debería ser único 
    # para cada generación?

    # Duda 27
    # ¿Cuál es la lógica detrás de las siguientes condiciones del JOIN?
    # (A.SEMESTRE_AVANCE_GENERACION<= C.oferta OR C.oferta>=8 OR (A.PROGRAMATERM = C.ENTRADA AND C.oferta>=3))

    # Duda 28
    # ¿Por qué el semestre de avance de generación no debe estar entre los semestres de avance 
    # de generación de los registros entrada-campus-generación eliminados anteriormente?
    spark.sql("""
        INSERT INTO {3}_temp
        SELECT '{0}', 1, '{1}', A.SEMESTRE_AVANCE_GENERACION, B.CAMPUS_INDICADOR, B.CAMPUS_INSCRIPCION, 
        A.PROGRAMATERM, B.TRANSFERENCIA, B.TRANSFERENCIA_TEMPORAL, A.ES_CLINICA, 0, 
            CASE WHEN 
            TASAXPIN_PROGRAMAS * 
            (TASAXPIN_TRANSFERENCIAS / SUM(TASAXPIN_TRANSFERENCIAS) OVER WIN) IS NULL
                THEN 0 
            ELSE 
                TASAXPIN_PROGRAMAS * 
                (TASAXPIN_TRANSFERENCIAS / SUM(TASAXPIN_TRANSFERENCIAS) OVER WIN) 
            END AS TASAXPIN,
        DOUBLE(NULL) AS TASA_PROPORCIONAL, 0, '{2}'
        FROM TASAS_PROGRAMAS_AJUSTADAS A 
        JOIN TASAS_TRANSFERENCIAS B 
        ON A.SEMESTRE_AVANCE_GENERACION = B.SEMESTRE_AVANCE_GENERACION
        JOIN (
            SELECT PROGRAMA, CAMPUS, ENTRADA, FIRST(OFERTA) AS OFERTA 
            FROM AGREGAR_OFERTA 
            GROUP BY PROGRAMA, CAMPUS, ENTRADA) C 
        ON A.PROGRAMATERM = C.PROGRAMA AND B.CAMPUS_INSCRIPCION = C.CAMPUS 
        AND (A.SEMESTRE_AVANCE_GENERACION <= C.oferta OR C.oferta >= 8 OR (A.PROGRAMATERM = C.ENTRADA AND C.oferta >= 3)) ----------------
        WHERE A.SEMESTRE_AVANCE_GENERACION NOT IN (
            SELECT DISTINCT SEMESTRE_AVANCE_GENERACION 
            FROM {3}_temp
            WHERE PROGRAMA_ENTRADA_PIN = '{0}' AND CAMPUS_PIN = '{1}' AND GENERACION = '{2}')
        WINDOW WIN AS (
            PARTITION BY A.SEMESTRE_AVANCE_GENERACION, A.PROGRAMATERM, A.ES_CLINICA)
    """.format(entrada, campus, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Después de insertarlo, se calcula la tasa_proporcional usando la tasaxpin
    
    # Duda 29
    # ¿Por qué se seleccionan todas las columnas excepto "SEMESTRE_AVANCE_GENERACION"?

    # Duda 30
    # ¿Cuál es el uso de LEAD(SEMESTRE_AVANCE_GENERACION) en esta consulta?

    # Duda 31
    # ¿Por qué se crean particiones por las siguientes columnas "PROGRAMA_ENTRADA_PIN, CAMPUS_PIN, 
    # TEC21_PIN y GENERACION"?

    # Duda 32
    # ¿Por qué se selecciona la fila "SEMESTRE_AVANCE_GENERACION" y se le da un alias con su 
    # mismo nombre?

    # Duda 33
    # ¿Cuál es la intención de la siguiente condición:
    # CASE WHEN SUM(TASAXPIN)=0 THEN 1 ELSE SUM(TASAXPIN) END AS TOTAL_TASAXPIN FROM {3}_temp?

    # Duda 34
    # ¿Cuál es la intención de las tablas creadas en las subconsultas?
    spark.sql("""
        MERGE INTO {3}_temp AS A USING (
            SELECT * EXCEPT (SEMESTRE_AVANCE_GENERACION), LEAD(SEMESTRE_AVANCE_GENERACION) OVER (
                PARTITION BY PROGRAMA_ENTRADA_PIN, CAMPUS_PIN, TEC21_PIN, GENERACION 
                ORDER BY SEMESTRE_AVANCE_GENERACION
            ) AS SEMESTRE_AVANCE_GENERACION
            FROM (
                SELECT PROGRAMA_ENTRADA_PIN, CAMPUS_PIN, TEC21_PIN, GENERACION, SEMESTRE_AVANCE_GENERACION AS SEMESTRE_AVANCE_GENERACION, 
                    CASE WHEN SUM(TASAXPIN) = 0 
                        THEN 1 
                    ELSE 
                        SUM(TASAXPIN) 
                    END AS TOTAL_TASAXPIN
                FROM {3}_temp 
                GROUP BY PROGRAMA_ENTRADA_PIN, CAMPUS_PIN, TEC21_PIN, GENERACION, SEMESTRE_AVANCE_GENERACION)
        ) B ON 
        A.SEMESTRE_AVANCE_GENERACION > 1 AND A.GENERACION = B.GENERACION AND A.PROGRAMA_ENTRADA_PIN = B.PROGRAMA_ENTRADA_PIN AND A.CAMPUS_PIN = B.CAMPUS_PIN AND A.TEC21_PIN = B.TEC21_PIN AND A.SEMESTRE_AVANCE_GENERACION = B.SEMESTRE_AVANCE_GENERACION AND A.PROGRAMA_ENTRADA_PIN = '{0}' AND A.CAMPUS_PIN = '{1}' AND A.GENERACION = '{2}'
        WHEN MATCHED THEN UPDATE SET 
            A.TASA_PROPORCIONAL = A.TASAXPIN / B.TOTAL_TASAXPIN;
    """.format(entrada, campus, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))
    # Para los semestres 1 la tasa_proporcional = tasaxpin 
    
    # Duda 35
    # ¿Por qué la tasa proporcional es igual a la tasaxpin en los semestres 1?
    spark.sql("""
        UPDATE {3}_temp 
        SET TASA_PROPORCIONAL = TASAXPIN
        WHERE SEMESTRE_AVANCE_GENERACION = 1 AND PROGRAMA_ENTRADA_PIN = '{0}' AND CAMPUS_PIN = '{1}' AND GENERACION = '{2}';
    """.format(entrada, campus, generacion, NOMBRE_TABLA_TASAS_TEC_21_EJERCICIO))