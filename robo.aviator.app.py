import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite v9.4.2", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 12px; border-radius: 15px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 900; line-height: 1.1; }
    .semaforo-box { padding: 25px; border-radius: 15px; text-align: center; margin-top: 10px; border: 3px solid transparent; }
    .semaforo-texto { font-size: 2rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { 
        min-width: 60px; height: 55px; border-radius: 20px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; margin-right: 5px; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = "00:00"

# --- LÓGICA DE ESTRATEGIA CON STOP LOSS ---
def analizar_estrategia_pro(sin_rosa):
    if sin_rosa >= 40:
        return "🛑 STOP LOSS - PARAR APUESTAS", "#ff3131", "0 0 30px #ff3131"
    elif sin_rosa >= 30:
        return "🔥 ¡ENTRAR AHORA! (META 30)", "#27ae60", "0 0 20px #2ecc71"
    elif sin_rosa >= 25:
        return "🟡 PREPARAR (ZONA 25+)", "#f39c12", "none"
    return "🔴 ESPERAR", "#c0392b", "none"

# --- UI SUPERIOR ---
st.title("🦅 ELITE v9.4.2 - ESTRATEGIA 30/40")

def calc_sin_rosa():
    if not st.session_state.historial: return 0
    if st.session_state.historial[-1] >= 10: return 0
    c = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        c += 1
    return c

sin_rosa_actual = calc_sin_rosa()
txt_s, col_s, shadow = analizar_estrategia_pro(sin_rosa_actual)

# Métricas Principales
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card"><p class="label-elite">SIN ROSA</p><h2 class="valor-elite" style="color:#e91e63!important;">{sin_rosa_actual}</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card"><p class="label-elite">ESTADO</p><h2 class="valor-elite" style="color:{col_s};">{sin_rosa_actual}/30</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card"><p class="label-elite">STOP LOSS</p><h2 class="valor-elite" style="color:#ff3131;">40</h2></div>', unsafe_allow_html=True)

# Semáforo con Alerta de Stop Loss
st.markdown(f'''
    <div class="semaforo-box" style="background-color:{col_s}; box-shadow:{shadow}; border-color:{'white' if sin_rosa_actual >= 30 else 'transparent'};">
        <p class="semaforo-texto">{txt_s}</p>
    </div>
    ''', unsafe_allow_html=True)

# --- REGISTRO ---
with st.form("registro_pro", clear_on_submit=True):
    col_v, col_a, col_btn = st.columns([2, 1, 1])
    with col_v: v_vuelo = st.text_input("VALOR DEL VUELO")
    with col_a: a_vuelo = st.number_input("APUESTA", value=2000, step=1000)
    with col_btn: st.write("##"); btn = st.form_submit_button("REGISTRAR")

    if btn and v_vuelo:
        try:
            val = float(v_vuelo.replace(',', '.'))
            st.session_state.historial.append(val)
            if val >= 10:
                st.session_state.h_10x_input = datetime.now(py_tz).strftime("%H:%M")
            st.rerun()
        except: st.error("Dato incorrecto")

# BURBUJAS
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:10px; background:#111; border-radius:15px; border: 1px solid #333; margin-top:5px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 BORRAR ÚLTIMA"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.rerun()
