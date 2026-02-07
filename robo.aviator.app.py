import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.3.7", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .block-container { padding-top: 1rem; }
    
    /* Título del Robot */
    .robot-title {
        color: #ffffff;
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }

    /* Etiquetas de input en Blanco */
    label { color: white !important; font-weight: bold !important; text-transform: uppercase; font-size: 0.85rem; }
    
    .elite-card { 
        background-color: #121212; padding: 10px; border-radius: 12px; 
        text-align: center; margin-bottom: 8px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 0px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.5rem; font-weight: 900; line-height: 1.2; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 0.9rem; margin-top: 2px; }
    
    .semaforo-box { padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .semaforo-texto { font-size: 1.6rem; font-weight: 900; color: white; margin: 0; }
    
    .rosa-val-txt { color: #e91e63; font-weight: 900; font-size: 1rem; }
    
    .burbuja { 
        min-width: 55px; height: 50px; border-radius: 25px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; font-size: 0.9rem; margin-right: 5px;
    }
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
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "--:--"

# --- FUNCIONES ---
def contar_rondas_sin_rosa():
    count = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        count += 1
    return count

def get_minutos(hora_str):
    if "--" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=100000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Hueco 10x+", "Cazador (10x)", "Espejo Gemelo (10x)", "Conservadora (1.5x)"])
    if st.button("🔄 Reiniciar App"): st.session_state.clear(); st.rerun()

# --- 1. TÍTULO DEL ROBOT (ARRIBA DE TODO) ---
st.markdown('<div class="robot-title">🦅 AVIATOR ELITE V9.3.7</div>', unsafe_allow_html=True)

# --- 2. MÉTRICAS ---
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="elite-card"><p class="label-elite">SALDO ACTUAL</p><p class="valor-elite">{int(st.session_state.saldo_dinamico):,}</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="elite-card" style="border-color:#00ff41;"><p class="label-elite">GANANCIA</p><p class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="elite-card" style="border-color:#ff3131;"><p class="label-elite">PÉRDIDA</p><p class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,}</p></div>', unsafe_allow_html=True)

# --- 3. RELOJES ---
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.session_state.h_10x_input = st.text_input("H10", value=st.session_state.h_10x_input, label_visibility="collapsed", key="h10_main")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.session_state.h_100x_input = st.text_input("H100", value=st.session_state.h_100x_input, label_visibility="collapsed", key="h100_main")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)
with t3:
    sin_rosa = contar_rondas_sin_rosa()
    st.markdown(f'<div class="elite-card" style="border-color:#e91e63;"><p class="label-elite">📊 SIN ROSA</p><p class="valor-elite" style="color:#e91e63!important;">{sin_rosa}</p></div>', unsafe_allow_html=True)

# --- 4. HISTORIAL DE RONDAS (BURBUJAS) ---
if st.session_state.historial:
    b_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-12:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:10px; background:#111; border-radius:10px; margin-bottom:15px; border: 1px solid #333;">{b_html}</div>', unsafe_allow_html=True)

# --- 5. SEMÁFORO ---
txt_s, col_s = ("🟢 ENTRAR", "#27ae60") if sin_rosa >= 25 else ("🟡 ALERTA", "#f1c40f") if sin_rosa >= 18 else ("🔴 NO ENTRAR", "#c0392b")
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# --- 6. REGISTRO DE VUELO (ABAJO) ---
st.markdown("<br>", unsafe_allow_html=True)
with st.form("registro_final", clear_on_submit=True):
    col_v, col_a, col_b = st.columns([2, 1, 1])
    with col_v:
        v_raw = st.text_input("VALOR DEL VUELO", placeholder="Ej: 2.10")
    with col_a:
        ap = st.number_input("APUESTA", value=2000, step=1000)
    with col_b:
        st.write("##")
        btn = st.form_submit_button("REGISTRAR ✈️", use_container_width=True)

    if btn and v_raw:
        try:
            val = float(v_raw.replace(',', '.'))
            target = 10.0 if "10x" in st.session_state.modo_sel else 1.5
            impacto = (ap * (target - 1)) if val >= target else -float(ap)
            st.session_state.historial.append(val)
            st.session_state.registro_saldos.append(impacto)
            st.session_state.saldo_dinamico += impacto
            if val >= 10:
                h_act = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.h_10x_input = h_act
                st.session_state.historial_rosas.append({"valor": val, "hora": h_act})
            st.rerun()
        except: pass

# --- 7. BOTÓN DESHACER ---
if st.button("🔙 BORRAR ÚLTIMA RONDA", use_container_width=True):
    if st.session_state.historial:
        v = st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        if v >= 10: st.session_state.historial_rosas.pop()
        st.rerun()
