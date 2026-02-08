import streamlit as st
from datetime import datetime
import pytz

# ————— ZONA HORARIA —————
py_tz = pytz.timezone("America/Asuncion")

# ————— INICIALIZACIÓN DEL ESTADO —————
if "key_id" not in st.session_state:
    st.session_state.key_id = 0

if "historial" not in st.session_state:
    st.session_state.historial = []

if "registro_saldos" not in st.session_state:
    st.session_state.registro_saldos = []

if "saldo_dinamico" not in st.session_state:
    st.session_state.saldo_dinamico = 0.0

if "in_apuesta" not in st.session_state:
    st.session_state.in_apuesta = 0.0

if "in_chk" not in st.session_state:
    st.session_state.in_chk = False

# ————— FUNCIÓN DE REGISTRO —————
def registrar():
    curr_key = f"input_{st.session_state.key_id}"

    raw = st.session_state.get(curr_key, "").replace(",", ".")
    if raw.strip() == "":
        return

    try:
        val = float(raw)

        apuesta = st.session_state.in_apuesta
        jugado = st.session_state.in_chk

        # Cálculo de ganancia/perdida
        if jugado:
            if val >= 10.0:
                gan = apuesta * 9
            else:
                gan = -apuesta
        else:
            gan = 0.0

        # Guardar datos
        st.session_state.historial.append(val)
        st.session_state.registro_saldos.append(gan)
        st.session_state.saldo_dinamico += gan

        ahora_f = datetime.now(py_tz).strftime("%H:%M")

        # Puedes guardar los timestamps si lo deseas
        if val >= 10.0:
            st.session_state.h_10x = ahora_f
        if val >= 100.0:
            st.session_state.h_100x = ahora_f

        # Avanzar clave para nueva ronda
        st.session_state.key_id += 1

    except Exception as e:
        st.error(f"Valor inválido: {raw}")
        print("Error en registrar:", e)

# ————— CONTROLES DE APOSTA —————
st.session_state.in_apuesta = st.number_input(
    "Apuesta (Gs):",
    min_value=0.0,
    step=0.5,
    value=st.session_state.in_apuesta
)

st.session_state.in_chk = st.checkbox(
    "Jugado",
    value=st.session_state.in_chk
)

# ————— INPUT PRINCIPAL —————
st.text_input(
    "Ingresa resultado de ronda y presiona ENTER:",
    key=f"input_{st.session_state.key_id}",
    on_change=registrar
)

# ————— MOSTRAR RESULTADOS —————
st.subheader("📊 Historial de valores")
st.write(st.session_state.historial)

st.subheader("💰 Registro de saldos")
st.write(st.session_state.registro_saldos)

st.subheader("🔢 Saldo total acumulado")
st.write(st.session_state.saldo_dinamico)
