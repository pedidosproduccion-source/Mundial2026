import streamlit as st
import pandas as pd
import json
import os
import re

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(
    page_title="Polla Mundialista romarco FIFA 2026",
    page_icon="",
    layout="wide"
)

DATA_FILE = "apuestas_mundial2026.json"
CONTRASENA_CORRECTA = "Admin2026"

# ======================================================
# ======================================================
# FUNCIONES MODIFICADAS
# ======================================================
def cargar_datos():
    # 1. Intentar leer el archivo si existe
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = {}
    else:
        datos = {}

    # 2. ASEGURARSE de que las variables de control SIEMPRE existan en el diccionario
    if "_resultados_reales" not in datos:
        datos["_resultados_reales"] = {}
        
    if "_partidos_jugados" not in datos:
        datos["_partidos_jugados"] = {}
        
    if "_bloqueo_pronosticos" not in datos:
        datos["_bloqueo_pronosticos"] = False
        
    if "_bloqueo_matriz" not in datos:
        datos["_bloqueo_matriz"] = True  # Por defecto inicia bloqueada

    return datos


def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)


def calcular_puntos(g_local_real, g_vis_real, g_local_apuesta, g_vis_apuesta):

    if (
        g_local_real is None
        or g_vis_real is None
        or g_local_apuesta is None
        or g_vis_apuesta is None
    ):
        return 0

    glr = int(g_local_real)
    gvr = int(g_vis_real)
    gla = int(g_local_apuesta)
    gva = int(g_vis_apuesta)

    # resultado exacto
    if glr == gla and gvr == gva:
        return 3

    signo_real = 1 if glr > gvr else (-1 if glr < gvr else 0)
    signo_apuesta = 1 if gla > gva else (-1 if gla < gva else 0)

    if signo_real == signo_apuesta:
        return 1

    return 0


def obtener_codigo_equipo(texto):
    patron = r"\((.*?)\)"
    resultado = re.search(patron, texto)

    if resultado:
        return resultado.group(1)

    return texto[:3].upper()


# ======================================================
# PARTIDOS
# ======================================================
PARTIDOS = [
    {"id": 1, "Partido": "1", "local": "Sudáfrica", "visitante": "Canadá", "fecha": "Viernes 12 de Junio - Los Angeles"},
    {"id": 2, "Partido": "2", "local": "Brasil", "visitante": "Japon", "fecha": "Sábado 13 de Junio - Nueva Jersey"},
    {"id": 3, "Partido": "3", "local": "Alemania", "visitante": "Paraguay", "fecha": "Domingo 14 de Junio - Dallas"},
    {"id": 4, "Partido": "4", "local": "Paises Bajos", "visitante": "Marruecos", "fecha": "Lunes 15 de Junio - Miami"},
    {"id": 5, "Partido": "5", "local": "Costa de Marfil", "visitante": "Noruega", "fecha": "Martes 16 de Junio - Nueva Jersey"},
    {"id": 6, "Partido": "6", "local": "Francia", "visitante": "Suecia", "fecha": "Miércoles 17 de Julio - Ciudad de México"},
    {"id": 7, "Partido": "7", "local": "México", "visitante": "Ecuador", "fecha": "Viernes 19 de Junio - San Francisco"}, 
    {"id": 8, "Partido": "8", "local": "Inglaterra", "visitante": "Congo", "fecha": "Sábado 20 de Junio - Kansas City"},
    {"id": 9, "Partido": "9", "local": "Belgica", "visitante": "Senegal", "fecha": "Domingo 21 de Junio - Miami"},
    {"id": 10, "Partido": "10", "local": "EE. UU.", "visitante": "Bosnia", "fecha": "Lunes 22 de Junio - Dallas"},
    {"id": 11, "Partido": "11", "local": "Espña", "visitante": "Austria", "fecha": "Jueves 18 de Junio - Guadalajara"},
    {"id": 12, "Partido": "12", "local": "Portugal", "visitante": "Croacia", "fecha": "Martes 23 de Junio - Guadalajara"},
    {"id": 13, "Partido": "13", "local": "Suiza", "visitante": "Argelia", "fecha": "Miércoles 24 de Junio - Miami"},
    {"id": 14, "Partido": "14", "local": "Australia", "visitante": "Egipto", "fecha": "Jueves 25 de Junio - Nueva Jersey"},
    {"id": 15, "Partido": "15", "local": "Argentina", "visitante": "Cabo Verde", "fecha": "Viernes 26 de Junio - Guadalajara"},
    {"id": 16, "Partido": "16", "local": "Colombia", "visitante": "Ghana", "fecha": "Sábado 27 de Junio - Miami"},
]

# ======================================================
# SESSION
# ======================================================
if "datos_polla" not in st.session_state:
    st.session_state.datos_polla = cargar_datos()

datos = st.session_state.datos_polla

if "_bloqueo_pronosticos" not in datos:
    datos["_bloqueo_pronosticos"] = False
    
if "_partidos_jugados" not in datos:
    datos["_partidos_jugados"] = {}
    
if "_bloqueo_matriz" not in datos:
    datos["_bloqueo_matriz"] = True

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.header(" Reglamento")

    st.info("""
     Resultado Exacto = 3 puntos
    
     Acertar ganador/empate = 1 punto
     
     Premiacion final: 1er puesto: 80% del total recaudado,
     2do puesto: 20%
     
     Se cierran apuestas el viernes 12 de junio a las 03:00 pm
    """)

# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3, tab5 = st.tabs([
    " Mis Pronósticos",
    "👨‍💼 Panel Administrador",
    "🏆 Tabla de Posiciones",
    " Matriz de Pronósticos"
])

with tab1:

    st.header("Registrar Pronósticos")

    # Solo bloquea esta pestaña, NO toda la app
    if datos["_bloqueo_pronosticos"]:
        st.error("🔒 Los pronósticos están cerrados. El Mundial ya comenzó.")
    else:

        nombre = st.text_input("Nombre").strip().upper()
        cedula = st.text_input("Cédula").strip()

        if nombre and cedula:

            usuario_key = cedula

            if usuario_key in datos:
                st.warning("⚠️ Ya registraste tus pronósticos.")
            else:

                nuevas_apuestas = {}

                for partido in PARTIDOS:

                    pid = str(partido["id"])

                    st.markdown(
                        f"### Partido {partido['Partido']} - "
                        f"{partido['local']} vs {partido['visitante']}"
                    )

                    col1, col2 = st.columns(2)
                     
                    with col1: g_local = st.number_input(
                        partido["local"], 
                        min_value=0, 
                        max_value=20, 
                        key=f"l_{pid}" 
                    ) 
                    
                    with col2: 
                        g_visitante = st.number_input( 
                        partido["visitante"], 
                        min_value=0, 
                        max_value=20, 
                        key=f"v_{pid}" 
                    )

                    nuevas_apuestas[pid] = [g_local, g_visitante]

                if st.button("Guardar Pronósticos"):

                    # 1. EN LUGAR DE USAR SÓLO LA MEMORIA, LEEMOS EL ARCHIVO EN TIEMPO REAL
                    datos_actualizados = cargar_datos()

                    # 2. VERIFICAR DE NUEVO SI LA CÉDULA YA EXISTE EN EL ARCHIVO REAL
                    if usuario_key in datos_actualizados:
                        st.error("⚠️ Error: Esta cédula ya fue registrada mientras llenabas el formulario.")
                    else:
                        # 3. AGREGAMOS EL NUEVO JUGADOR AL DICCIONARIO FRESCO
                        datos_actualizados[usuario_key] = {
                            "nombre": nombre,
                            "cedula": cedula,
                            "apuestas": nuevas_apuestas,
                            "puntos_totales": 0
                        }

                        # 4. GUARDAMOS EL DICCIONARIO ACTUALIZADO
                        guardar_datos(datos_actualizados)
                        
                        # 5. Sincronizamos la memoria de la sesión actual
                        st.session_state.datos_polla = datos_actualizados

                        st.success("✅ Pronósticos registrados correctamente.")
                        st.balloons()

# ======================================================
# TAB 2 - ADMIN
# ======================================================
with tab2:

    st.header("Panel Administrador")

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if password == CONTRASENA_CORRECTA:

        st.success("Acceso concedido")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🔒 Bloquear Pronósticos"):
                    datos["_bloqueo_pronosticos"] = True
                    guardar_datos(datos)
                    st.success("Pronósticos bloqueados")

        with col2:
            if st.button("🔓 Habilitar Pronósticos"):
                    datos["_bloqueo_pronosticos"] = False
                    guardar_datos(datos)
                    st.success("Pronósticos habilitados")

        with col3:
            if st.button("🔒 Bloquear Matriz"):
                    datos["_bloqueo_matriz"] = True
                    guardar_datos(datos)
                    st.success("Matriz bloqueada")

        with col4:
            if st.button("🔓 Habilitar Matriz"):
                    datos["_bloqueo_matriz"] = False
                    guardar_datos(datos)
                    st.success("Matriz habilitada")

        st.divider()

        st.subheader("Resultados Reales")

        if "_resultados_reales" not in datos:
            datos["_resultados_reales"] = {}

        if "_partidos_jugados" not in datos:
            datos["_partidos_jugados"] = {}

        nuevos_resultados = {}
        partidos_jugados = {}

        for partido in PARTIDOS:

            pid = str(partido["id"])

            st.markdown(
                f"### {partido['local']} vs {partido['visitante']}"
            )

            valor_actual = datos["_resultados_reales"].get(pid, [0, 0])
            jugado_actual = datos["_partidos_jugados"].get(pid, False)

            col1, col2, col3 = st.columns([1, 1, 1.5])

            with col1:
                rl = st.number_input(
                    "Local",
                    min_value=0,
                    max_value=20,
                    value=int(valor_actual[0]),
                    key=f"rl_{pid}"
                )

            with col2:
                rv = st.number_input(
                    "Visitante",
                    min_value=0,
                    max_value=20,
                    value=int(valor_actual[1]),
                    key=f"rv_{pid}"
                )

            with col3:
                jugado = st.checkbox(
                    "✅ Partido jugado",
                    value=jugado_actual,
                    key=f"jugado_{pid}"
                )

            nuevos_resultados[pid] = [rl, rv]
            partidos_jugados[pid] = jugado

        if st.button("Calcular Puntajes"):

            datos["_resultados_reales"] = nuevos_resultados
            datos["_partidos_jugados"] = partidos_jugados

            for jugador, info in datos.items():

                if jugador.startswith("_"):
                    continue

                puntos = 0

                apuestas = info.get("apuestas", {})

                for partido in PARTIDOS:

                    pid = str(partido["id"])

                    # Solo contar partidos marcados como jugados
                    if not partidos_jugados.get(pid, False):
                        continue

                    # Obtener resultado real
                    res_real = nuevos_resultados.get(pid)

                    if not res_real:
                        continue

                    # Obtener pronóstico del jugador
                    apuesta = apuestas.get(pid)

                    if apuesta:

                        puntos += calcular_puntos(
                            res_real[0],
                            res_real[1],
                            apuesta[0],
                            apuesta[1]
                        )

                datos[jugador]["puntos_totales"] = puntos

            guardar_datos(datos)

            st.success("✅ Puntajes actualizados correctamente")
# ======================================================
# TAB 3 - TABLA
# ======================================================
with tab3:

    filas = []

    for jugador, info in datos.items():

        if jugador.startswith("_"):
            continue

        filas.append({
            "Nombre": info["nombre"],
            "Cédula": info["cedula"],
            "Puntos": info["puntos_totales"]
        })

    if filas:

        df = pd.DataFrame(filas)
        df = df.sort_values(
            by="Puntos",
            ascending=False
        ).reset_index(drop=True)

        df.index += 1

        st.dataframe(df, use_container_width=True)


# ======================================================
# TAB 5 - MATRIZ
# ======================================================
with tab5:

    st.header("Matriz General de Pronósticos")

    if datos.get("_bloqueo_matriz", True):
        st.error(
            "🔒 La matriz de pronósticos aún no está disponible."
        )

    else:

        matriz = []

        resultados_reales = datos.get(
            "_resultados_reales", {}
        )

        partidos_jugados = datos.get(
            "_partidos_jugados", {}
        )

        for jugador, info in datos.items():

            if jugador.startswith("_"):
                continue

            fila = {
                "Nombre": info["nombre"],
                "Cédula": info["cedula"]
            }

            apuestas = info["apuestas"]

            for partido in PARTIDOS:

                pid = str(partido["id"])

                local = obtener_codigo_equipo(
                    partido["local"]
                )

                visitante = obtener_codigo_equipo(
                    partido["visitante"]
                )

                columna = f"{local} vs {visitante}"

                res = apuestas.get(pid)

                fila[columna] = (
                    f"{res[0]}-{res[1]}"
                    if res else "-"
                )

                columna_real = f"REAL {pid}"

                if partidos_jugados.get(pid, False):

                    resultado_real = resultados_reales.get(pid)

                    fila[columna_real] = (
                        f"{resultado_real[0]}-{resultado_real[1]}"
                        if resultado_real else "-"
                    )
                else:
                    fila[columna_real] = "-"

            matriz.append(fila)

        if matriz:

            df_matriz = pd.DataFrame(matriz)

            st.dataframe(
                df_matriz,
                use_container_width=True
            )