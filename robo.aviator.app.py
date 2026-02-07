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
    /* Reducir márgenes superiores de la página */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    .elite-card { 
        background-color: #121212; padding: 8px; border-radius: 10px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    /* Tamaños de fuente reducidos */
    .label-elite { color: #FFFFFF !important; font-weight: 700; text-transform: uppercase; font-size: 0.65rem; margin-bottom: 0px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.4rem; font-weight: 900; line-height: 1.2; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 0.8rem; margin-top: 2px; }
    
    .semaforo-box { padding: 15px; border-radius: 12px; text-align: center; margin-top: 5px; }
    .semaforo-texto { font-size: 1.2rem; font-weight: 800; color: white; margin: 0; }
    
    .rosa-val-txt { color: #e91e63; font-weight: 900; font-size: 0.9rem; }
    
    /* Burbujas más pequeñas */
    .burbuja { 
        min-width: 45px; height: 42px; border-radius: 20px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 800; color: white; font-size: 0.8rem; margin-right: 4px;
    }
    
    /* Compactar inputs de Streamlit */
    div[data-testid="stTextInput"] input { padding: 5px; font-size: 0.85rem; height: 30px; }
    div[data-testid="stNumberInput"] input { padding: 5px; font-size: 0.85rem; height: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
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

# --- SIDEBAR COMPACTA ---
with st.sidebar:
    st.markdown("### 🦅 CONFIG")
    saldo_in = st.number_input("Saldo Inicial", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia", ["Hueco 10x+", "Cazador (10x)", "Conservadora (1.50x)"])
    if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

# FILA 1: MÉTRICAS (MÁS PEQUEÑAS)
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="elite-card"><p class="label-elite">Saldo</p><p class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="elite-card" style="border-color:#00ff41;"><p class="label-elite">Ganancia</p><p class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="elite-card" style="border-color:#ff3131;"><p class="label-elite">Pérdida</p><p class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)

# FILA 2: RELOJES
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

# HISTORIAL ROSA EDITABLE (COLUMNAS MÁS ESTRECHAS)
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
txt_s, col_s = ("🟢 HUECO", "#27ae60") if sin_rosa >= 25 else ("🟡 ESPERAR", "#f1c40f") if sin_rosa >= 18 else ("🔴 NO", "#c0392b")
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# REGISTRO (UNA SOLA LÍNEA)
with st.form("reg", clear_on_submit=True):
    c_in, c_ap, c_btn = st.columns([2, 2, 1])
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
            st.rerun()
        except: pass

# BURBUJAS Y DESHACER
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-10:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:5px; background:#111; border-radius:10px; margin-top:5px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 BORRAR ÚLTIMA", use_container_width=True):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.rerun()
