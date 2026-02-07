import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página - Forzamos el modo compacto
st.set_page_config(page_title="Aviator Elite Compact", page_icon="🦅", layout="wide")

# --- DISEÑO CSS PARA DISMINUIR TAMAÑOS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    
    /* Logo / Título Compacto */
    .logo-elite {
        color: #FFFFFF; font-size: 1.1rem; font-weight: 900;
        text-align: center; margin-bottom: 10px; border-bottom: 1px solid #333;
    }

    .elite-card { 
        background-color: #121212; padding: 6px; border-radius: 10px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 700; text-transform: uppercase; font-size: 0.6rem; margin-bottom: 0px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.3rem; font-weight: 900; line-height: 1.1; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 0.75rem; margin-top: 2px; }
    
    .semaforo-box { padding: 10px; border-radius: 10px; text-align: center; margin-top: 5px; }
    .semaforo-texto { font-size: 1.1rem; font-weight: 800; color: white; margin: 0; }
    
    .rosa-val-txt { color: #e91e63; font-weight: 900; font-size: 0.85rem; }
    
    .burbuja { 
        min-width: 42px; height: 38px; border-radius: 18px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 800; color: white; font-size: 0.75rem; margin-right: 3px;
    }
    
    /* Inputs más pequeños */
    div[data-testid="stTextInput"] input { padding: 4px; font-size: 0.8rem; height: 28px; }
    div[data-testid="stNumberInput"] input { padding: 4px; font-size: 0.8rem; height: 28px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'historial_rosas' not in st.session_state: st.session_state.historial_rosas = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = "00:00"
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

def contar_rondas_desde_rosa():
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

# TÍTULO LOGO RESTAURADO
st.markdown('<div class="logo-elite">🦅 AVIATOR ELITE v9.2.9</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🦅 CONFIG")
    saldo_in = st.number_input("Saldo Inicial", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia", ["Hueco 10x+", "Cazador (10x)", "Espejo (10x)"])
    if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

# MÉTRICAS
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="elite-card"><p class="label-elite">Saldo</p><p class="valor-elite">{int(st.session_state.saldo_dinamico):,}</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="elite-card" style="border-color:#00ff41;"><p class="label-elite">Ganancia</p><p class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="elite-card" style="border-color:#ff3131;"><p class="label-elite">Pérdida</p><p class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)

# RELOJES
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.session_state.h_10x_input = st.text_input("H10", value=st.session_state.h_10x_input, label_visibility="collapsed", key="top_h10")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.session_state.h_100x_input = st.text_input("H100", value=st.session_state.h_100x_input, label_visibility="collapsed", key="top_h100")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="elite-card" style="border-color:#e91e63;"><p class="label-elite">📊 SIN ROSA</p><p class="valor-elite" style="color:#e91e63!important;">{contar_rondas_desde_rosa()}</p></div>', unsafe_allow_html=True)

# HISTORIAL ROSA
with st.expander("📊 HISTORIAL ROSA", expanded=True):
    if st.session_state.historial_rosas:
        for idx, rosa in enumerate(reversed(st.session_state.historial_rosas[-4:])):
            real_idx = len(st.session_state.historial_rosas) - 1 - idx
            c_val, c_time = st.columns([1, 1])
            with c_val: st.markdown(f'<span class="rosa-val-txt">🌸 {rosa["valor"]}x</span>', unsafe_allow_html=True)
            with c_time:
                nueva_hora = st.text_input(f"h_{real_idx}", value=rosa["hora"], key=f"hist_{real_idx}", label_visibility="collapsed")
                st.session_state.historial_rosas[real_idx]["hora"] = nueva_hora
    else: st.write("Sin datos")

# SEMÁFORO
sin_rosa = contar_rondas_desde_rosa()
txt_s, col_s = ("🟢 HUECO", "#27ae60") if sin_rosa >= 25 else ("🟡 ANALIZANDO", "#f1c40f") if sin_rosa >= 18 else ("🔴 NO", "#c0392b")
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# REGISTRO
with st.form("reg", clear_on_submit=True):
    c_in, c_ap, c_btn = st.columns([2, 1.5, 1])
    with c_in: v_raw = st.text_input("VUELO", placeholder="0.00", label_visibility="collapsed")
    with c_ap: ap_m = st.number_input("AP", value=2000, step=1000, label_visibility="collapsed")
    with c_btn: sub = st.form_submit_button("OK")
    
    if sub and v_raw:
        try:
            val = float(v_raw.replace(',', '.'))
            st.session_state.historial.append(val)
            if val >= 10:
                ahora = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.h_10x_input = ahora
                st.session_state.historial_rosas.append({"valor": val, "hora": ahora})
                if val >= 100: st.session_state.h_100x_input = ahora
            st.rerun()
        except: pass

# BURBUJAS Y BORRAR
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-10:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:5px; background:#111; border-radius:10px; margin-top:5px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 BORRAR ÚLTIMA", use_container_width=True):
    if st.session_state.historial:
        v = st.session_state.historial.pop()
        if v >= 10: st.session_state.historial_rosas.pop()
        st.rerun()
