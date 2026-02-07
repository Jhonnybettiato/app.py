import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página - Modo Ultra Compacto
st.set_page_config(page_title="Aviator Elite v9.3", page_icon="🦅", layout="wide")

# --- DISEÑO CSS COMPACTO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    
    /* Tarjetas de métricas pequeñas */
    .elite-card { 
        background-color: #121212; padding: 5px; border-radius: 8px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 700; text-transform: uppercase; font-size: 0.6rem; margin-bottom: 0px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.1rem; font-weight: 900; line-height: 1; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 0.7rem; margin-top: 2px; }
    
    /* Semáforo compacto */
    .semaforo-box { padding: 8px; border-radius: 8px; text-align: center; margin-top: 5px; }
    .semaforo-texto { font-size: 1rem; font-weight: 800; color: white; margin: 0; }
    
    /* Historial Rosa */
    .rosa-val-txt { color: #e91e63; font-weight: 900; font-size: 0.8rem; }
    
    /* Burbujas pequeñas */
    .burbuja { 
        min-width: 38px; height: 35px; border-radius: 15px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 800; color: white; font-size: 0.7rem; margin-right: 3px;
    }
    
    /* Inputs minúsculos para ahorrar espacio vertical */
    div[data-testid="stTextInput"] input { padding: 2px 5px; font-size: 0.8rem; height: 25px; }
    div[data-testid="stNumberInput"] input { padding: 2px 5px; font-size: 0.8rem; height: 25px; }
    div[data-testid="stForm"] { padding: 5px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'historial_rosas' not in st.session_state: st.session_state.historial_rosas = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = "00:00"
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

def get_minutos(hora_str):
    if "---" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

# --- BARRA LATERAL (LOGO AQUÍ) ---
with st.sidebar:
    st.markdown("## 🦅 AVIATOR ELITE") # Logo movido aquí para visibilidad total
    st.divider()
    saldo_in = st.number_input("Saldo Inicial", value=100000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia", ["Hueco 10x+", "Cazador (10x)", "Espejo (10x)"])
    if st.button("🔄 Reiniciar App"): st.session_state.clear(); st.rerun()

# MÉTRICAS SUPERIORES
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="elite-card"><p class="label-elite">SALDO</p><p class="valor-elite">{int(st.session_state.saldo_dinamico):,}</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="elite-card" style="border-color:#00ff41;"><p class="label-elite">GANANCIA</p><p class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="elite-card" style="border-color:#ff3131;"><p class="label-elite">PÉRDIDA</p><p class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)

# RELOJES EDITABLES
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.session_state.h_10x_input = st.text_input("H10", value=st.session_state.h_10x_input, label_visibility="collapsed", key="h10_top")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.session_state.h_100x_input = st.text_input("H100", value=st.session_state.h_100x_input, label_visibility="collapsed", key="h100_top")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)
with t3:
    sin_rosa = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        sin_rosa += 1
    st.markdown(f'<div class="elite-card" style="border-color:#e91e63;"><p class="label-elite">📊 SIN ROSA</p><p class="valor-elite" style="color:#e91e63!important;">{sin_rosa}</p></div>', unsafe_allow_html=True)

# HISTORIAL ROSA EDITABLE
with st.expander("📊 HISTORIAL ROSA", expanded=True):
    if st.session_state.historial_rosas:
        for idx, rosa in enumerate(reversed(st.session_state.historial_rosas[-4:])):
            r_idx = len(st.session_state.historial_rosas) - 1 - idx
            cv, ct = st.columns([1, 1.2])
            cv.markdown(f'<div style="padding-top:5px;"><span class="rosa-val-txt">🌸 {rosa["valor"]}x</span></div>', unsafe_allow_html=True)
            nueva_h = ct.text_input(f"edit_{r_idx}", value=rosa["hora"], key=f"hist_{r_idx}", label_visibility="collapsed")
            st.session_state.historial_rosas[r_idx]["hora"] = nueva_h
    else: st.write("Esperando...")

# SEMÁFORO
txt_s, col_s = ("🟢 ENTRAR", "#27ae60") if sin_rosa >= 25 else ("🟡 ALERTA", "#f1c40f") if sin_rosa >= 18 else ("🔴 NO", "#c0392b")
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# REGISTRO ULTRA COMPACTO
with st.form("registro", clear_on_submit=True):
    c1, c2, c3 = st.columns([1.5, 1.2, 0.8])
    v_in = c1.text_input("VUELO", placeholder="0.00", label_visibility="collapsed")
    a_in = c2.number_input("AP", value=2000, step=1000, label_visibility="collapsed")
    if c3.form_submit_button("OK"):
        if v_in:
            try:
                val = float(v_in.replace(',', '.'))
                st.session_state.historial.append(val)
                if val >= 10:
                    now = datetime.now(py_tz).strftime("%H:%M")
                    st.session_state.h_10x_input = now
                    st.session_state.historial_rosas.append({"valor": val, "hora": now})
                    if val >= 100: st.session_state.h_100x_input = now
                st.rerun()
            except: pass

# BURBUJAS
if st.session_state.historial:
    b_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-10:])])
    st.markdown(f'<div style="display:flex; padding:4px; background:#111; border-radius:10px; margin-bottom:5px;">{b_html}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER", use_container_width=True):
    if st.session_state.historial:
        v = st.session_state.historial.pop()
        if v >= 10: st.session_state.historial_rosas.pop()
        st.rerun()
    
