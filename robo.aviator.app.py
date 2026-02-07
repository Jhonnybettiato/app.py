import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.3.3", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 12px; border-radius: 15px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 2px; }
    .valor-elite { color: #FFFFFF !important; font-size: 2rem; font-weight: 900; line-height: 1.1; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 1rem; margin-top: 2px; }
    .semaforo-box { padding: 20px; border-radius: 15px; text-align: center; margin-top: 5px; margin-bottom: 5px; }
    .semaforo-texto { font-size: 1.8rem; font-weight: 900; color: white; margin: 0; }
    
    .burbuja { 
        min-width: 60px; height: 55px; border-radius: 25px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; padding: 0 10px; margin-right: 5px; font-size: 0.9rem;
    }
    /* Títulos de inputs en blanco */
    label { color: white !important; font-size: 0.8rem !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
for key, val in {
    'historial': [], 'registro_saldos': [], 'historial_rosas': [],
    'saldo_dinamico': 0.0, 'primer_inicio': True,
    'h_10x_input': "00:00", 'h_100x_input': "---"
}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- FUNCIONES ---
def calcular_sin_rosa():
    if not st.session_state.historial: return 0
    if st.session_state.historial[-1] >= 10: return 0
    count = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        count += 1
    return count

def get_minutos(hora_str):
    if "---" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🦅 CONFIG")
    saldo_in = st.number_input("Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Hueco 10x+", "Cazador (10x)"])
    if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

# --- INTERFAZ SUPERIOR ---
st.title("🦅 AVIATOR ELITE v9.3.3")

ganancia_neta = st.session_state.saldo_dinamico - saldo_in
sin_rosa_actual = calcular_sin_rosa()

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card" style="border:1px solid #fff;"><p class="label-elite">SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card" style="border:1px solid #00ff41;"><p class="label-elite">GANANCIA</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,}</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card" style="border:1px solid #ff3131;"><p class="label-elite">SIN ROSA</p><h2 class="valor-elite" style="color:#e91e63!important;">{sin_rosa_actual}</h2></div>', unsafe_allow_html=True)

t1, t2 = st.columns(2)
with t1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.session_state.h_10x_input = st.text_input("H10", value=st.session_state.h_10x_input, label_visibility="collapsed", key="h10")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.session_state.h_100x_input = st.text_input("H100", value=st.session_state.h_100x_input, label_visibility="collapsed", key="h100")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)

# SEMÁFORO
txt_s, col_s = ("🟢 HUECO ACTIVO", "#27ae60") if sin_rosa_actual >= 25 else ("🔴 NO ENTRAR", "#c0392b")
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# --- 🚀 ZONA DE ACCIÓN: REGISTRO PEGADO AL HISTORIAL ---

with st.container():
    with st.form("registro_form", clear_on_submit=True):
        col_v, col_a, col_ap, col_btn = st.columns([2, 1, 1, 1])
        with col_v: v_input = st.text_input("VALOR DEL VUELO")
        with col_a: a_input = st.number_input("APUESTA", value=2000, step=1000)
        with col_ap: st.write("##"); check_ap = st.checkbox("¿APOSTÉ?")
        with col_btn: st.write("##"); submit_btn = st.form_submit_button("REGISTRAR")

        if submit_btn and v_input:
            try:
                # 1. Limpiar y convertir valor
                val = float(re.sub(r'[^0-9.,]', '', v_input).replace(',', '.'))
                
                # 2. Calcular impacto en saldo
                impacto = 0.0
                if check_ap:
                    meta = 10.0 if "10x" in st.session_state.modo_sel else 1.5
                    impacto = (a_input * (meta - 1)) if val >= meta else -float(a_input)
                
                # 3. Guardar en historial (Esto ocurre ANTES del rerun)
                st.session_state.historial.append(val)
                st.session_state.registro_saldos.append(impacto)
                st.session_state.saldo_dinamico += impacto
                
                # 4. Lógica de Rosa
                if val >= 10:
                    ahora = datetime.now(py_tz).strftime("%H:%M")
                    st.session_state.h_10x_input = ahora
                    st.session_state.historial_rosas.append({"valor": val, "hora": ahora})
                    if val >= 100: st.session_state.h_100x_input = ahora
                
                st.rerun() # Reinicio forzado para ver cambios
            except:
                st.error("Error en formato")

# HISTORIAL DE BURBUJAS (Inmediatamente debajo del registro)
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-14:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:10px; background:#111; border-radius:15px; border: 1px solid #333; margin-top:2px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER ÚLTIMA", use_container_width=True):
    if st.session_state.historial:
        v = st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        if v >= 10: st.session_state.historial_rosas.pop()
        st.rerun()
