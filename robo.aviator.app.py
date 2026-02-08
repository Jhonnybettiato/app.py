import streamlit as st
from datetime import datetime
import pytz
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.7.1", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; text-transform: uppercase; letter-spacing: 3px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 5px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; }
    
    /* Indicador visual de FOCO ACTIVO */
    input:focus { 
        border: 2px solid #00ff41 !important; 
        box-shadow: 0 0 15px #00ff41 !important;
        background-color: #050505 !important;
    }

    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 475000.0
if 'h_10x' not in st.session_state: st.session_state.h_10x = "00:00"
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"
if 'key_id' not in st.session_state: st.session_state.key_id = 0
if 'cap_ini' not in st.session_state: st.session_state.cap_ini = 475000.0

# --- LÓGICA DE REGISTRO ---
def registrar():
    curr_key = f"input_{st.session_state.key_id}"
    if curr_key in st.session_state:
        raw = st.session_state[curr_key].replace(',', '.')
        if raw:
            try:
                val = float(raw)
                apuesta = st.session_state.in_apuesta
                jugado = st.session_state.in_chk
                gan = (apuesta * 9) if (jugado and val >= 10.0) else (-float(apuesta) if jugado else 0.0)
                
                st.session_state.historial.append(val)
                st.session_state.registro_saldos.append(gan)
                st.session_state.saldo_dinamico += gan
                
                ahora_f = datetime.now(py_tz).strftime("%H:%M")
                if val >= 10.0: st.session_state.h_10x = ahora_f
                if val >= 100.0: st.session_state.h_100x = ahora_f
                
                st.session_state.key_id += 1
            except: pass

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTES")
    st.session_state.cap_ini = st.number_input("Capital Inicial", value=int(st.session_state.cap_ini))
    st.session_state.h_10x = st.text_input("Hora 10x", value=st.session_state.h_10x)
    st.session_state.h_100x = st.text_input("Hora 100x", value=st.session_state.h_100x)
    if st.button("🔄 REINICIAR"):
        st.session_state.clear()
        st.rerun()

# --- INTERFAZ ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE ROBOT v9.7.1</div>', unsafe_allow_html=True)

# Dashboard de métricas
c1, c2, c3, c4 = st.columns(4)
res_ac = st.session_state.saldo_dinamico - st.session_state.cap_ini

c1.markdown(f'<div class="elite-card"><p class="label-elite">💰 SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="elite-card" style="border-color:{"#0f4" if res_ac >=0 else "#f31"};"><p class="label-elite">📈 GANANCIA</p><h2 class="valor-elite">{int(res_ac):,}</h2></div>', unsafe_allow_html=True)

# Tarjeta 10x con avión
c3.markdown(f'<div class="elite-card"><p class="label-elite">✈️ ÚLTIMA 10X</p><h2 class="valor-elite" style="color:#9b59b6 !important;">{st.session_state.h_10x}</h2></div>', unsafe_allow_html=True)

# Tarjeta 100x con avión rosa
c4.markdown(f'<div class="elite-card"><p class="label-elite">🚀 ÚLTIMA 100X</p><h2 class="valor-elite" style="color:#e91e63 !important;">{st.session_state.h_100x}</h2></div>', unsafe_allow_html=True)

# Semáforo de conteo
sin_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10.0: break
    sin_rosa += 1
st.markdown(f'<div style="background-color:#111; padding:15px; border-radius:10px; text-align:center; margin-bottom:15px; border: 1px solid #333;"><h3 style="color:white; margin:0;">⏳ RONDAS SIN ROSA: {sin_rosa}</h3></div>', unsafe_allow_html=True)

# PANEL DE ENTRADA
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns([2, 1, 1, 1])

with r1:
    st.text_input(
        "VALOR DEL VUELO", 
        value="", 
        key=f"input_{st.session_state.key_id}", 
        on_change=registrar,
        placeholder="INGRESE VALOR"
    )

with r2: st.number_input("APUESTA", value=2000, key="in_apuesta")
with r3: st.write("##"); st.checkbox("¿APOSTÉ?", key="in_chk")
with r4: st.write("##"); st.button("REGISTRAR 🚀", on_click=registrar)
st.markdown('</div>', unsafe_allow_html=True)

# --- INYECTOR DE FOCO ---
components.html(f"""
    <script>
    function setFocus() {{
        var inputs = window.parent.document.querySelectorAll('input[placeholder="INGRESE VALOR"]');
        if (inputs.length > 0) {{
            inputs[0].focus();
        }}
    }}
    setFocus();
    setTimeout(setFocus, 300);
    </script>
    """, height=0)

# Historial
if st.session_state.historial:
    h_h = "".join([f'<div class="burbuja" style="background-color:{"#e91e63" if v >= 10 else "#9b59b6" if v >= 2 else "#3498db"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:20px;">{h_h}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.rerun()
