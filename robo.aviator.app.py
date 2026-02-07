import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.4", page_icon="🦅", layout="wide")

# (CSS omitido por brevedad, se mantiene igual al anterior)
st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
# ... (otras variables de estado)

# --- FUNCIÓN DE PROCESAMIENTO MÚLTIPLE ---
def procesar_cadena_vuelos(cadena, apuesta_val, apostado_bool):
    # Separa por espacios, comas o guiones
    elementos = re.split(r'[ ,\-]+', cadena)
    for el in elementos:
        try:
            # Limpia el texto (quita 'x', espacios, etc)
            clean_el = re.sub(r'[^0-9.,]', '', el).replace(',', '.')
            if not clean_el: continue
            
            v_val = float(clean_el)
            impacto = 0.0
            
            if apostado_bool:
                est = st.session_state.modo_sel
                t = 10.0 if any(x in est for x in ["Cazador", "Hueco"]) else (1.5 if "1.5" in est else 2.0)
                impacto = (apuesta_val * (t - 1)) if v_val >= t else -float(apuesta_val)
            
            st.session_state.historial.append(v_val)
            st.session_state.saldo_dinamico += impacto
        except:
            continue

# --- INTERFAZ ---
st.title("🦅 AVIATOR ELITE v9.4")

# SEMÁFORO Y MÉTRICAS (Igual al anterior)

with st.form("registro_masivo", clear_on_submit=True):
    st.write("### 📝 REGISTRO RÁPIDO")
    # Aquí puedes escribir: "1.20 5.44 10.20" y registrará los 3 de una vez
    valor_input = st.text_input("Ingresa uno o varios valores (separados por espacio):", placeholder="Ej: 1.50 2.10 0.98")
    
    c1, c2, c3 = st.columns(3)
    with c1: apuesta = st.number_input("Apuesta:", value=2000)
    with c2: apostado = st.checkbox("¿Aposté en estos?")
    with c3: submit = st.form_submit_button("REGISTRAR TODO")

    if submit and valor_input:
        procesar_cadena_vuelos(valor_input, apuesta, apostado)
        st.rerun()

# (HISTORIAL Y BURBUJAS IGUAL AL ANTERIOR)
