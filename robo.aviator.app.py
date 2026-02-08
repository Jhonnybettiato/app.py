import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite v9.5.1 - PROFESIONAL", page_icon="🦅", layout="wide")

# --- DISEÑO CSS AVANZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 12px; border-radius: 15px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; line-height: 1.1; }
    
    /* Ventanas de Saldo Específicas */
    .win-card { background-color: #002b11; border: 2px solid #00ff41; padding: 10px; border-radius: 12px; text-align: center; }
    .loss-card { background-color: #2b0000; border: 2px solid #ff3131; padding: 10px; border-radius: 12px; text-align: center; }
    
    /* Animación de Parpadeo para la Ronda 30 */
    @keyframes glow {
        0% { box-shadow: 0 0 5px #2ecc71; }
        50% { box-shadow: 0 0 30px #2ecc71; }
        100% { box-shadow: 0 0 5px #2ecc71; }
    }
    .semaforo-box { padding: 30px; border-radius: 20px; text-align: center; margin-top: 10px; border: 3px solid transparent; }
    .glow-active { animation: glow 1.5s infinite; border-color: #fff !important; }
    
    .semaforo-texto { font-size: 2.2rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { 
        min-width: 60px; height: 55px; border-radius: 25px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; margin-right: 5px; font-size: 0.9rem;
    }
    label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = "00:00"
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- FUNCIONES ---
def get_minutos(hora_str):
    if "---" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

def calc_sin_rosa():
    if not st.session_state.historial: return 0
    if st.session_state.historial[-1] >= 10: return 0
    c = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        c += 1
    return c

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🦅 CONFIGURACIÓN")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    if st.button("🔄 REINICIAR SISTEMA"): st.session_state.clear(); st.rerun()

# --- UI PRINCIPAL ---
sin_rosa_actual = calc_sin_rosa()
ganancia_neta = st.session_state.saldo_dinamico - saldo_in

# FILA 1: VENTANAS DE SALDO (Verde y Rojo)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="elite-card"><p class="label-elite">SALDO ACTUAL</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)

with m2:
    if ganancia_neta >= 0:
        st.markdown(f'<div class="win-card"><p class="label-elite" style="color:#00ff41 !important;">GANANCIA ACUMULADA</p><h2 class="valor-elite" style="color:#00ff41 !important;">+{int(ganancia_neta):,}</h2></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="loss-card"><p class="label-elite" style="color:#ff3131 !important;">PÉRDIDA ACTUAL</p><h2 class="valor-elite" style="color:#ff3131 !important;">{int(ganancia_neta):,}</h2></div>', unsafe_allow_html=True)

with m3:
    st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 10X</p><h2 class="valor-elite">{st.session_state.h_10x_input}</h2><p style="color:#00ff41; font-size:0.8rem; margin:0;">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 100X</p><h2 class="valor-elite">{st.session_state.h_100x_input}</h2><p style="color:#00ff41; font-size:0.8rem; margin:0;">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)

# SEMÁFORO CON ANIMACIÓN
if sin_rosa_actual >= 40:
    txt, col, clase = "🛑 STOP LOSS: PARAR AHORA", "#ff3131", ""
elif sin_rosa_actual >= 30:
    txt, col, clase = "🔥 ¡ENTRAR AHORA! (META 30)", "#27ae60", "glow-active"
elif sin_rosa_actual >= 25:
    txt, col, clase = "🟡 PREPARAR (ZONA 25+)", "#f39c12", ""
else:
    txt, col, clase = f"⏳ ESPERAR ({sin_rosa_actual}/30)", "#333", ""

st.markdown(f'<div class="semaforo-box {clase}" style="background-color:{col};"><p class="semaforo-texto">{txt}</p></div>', unsafe_allow_html=True)

# --- REGISTRO ---
with st.container():
    with st.form("form_v951", clear_on_submit=True):
        f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
        with f1: v_v = st.text_input("VALOR DEL VUELO")
        with f2: a_v = st.number_input("APUESTA", value=2000, step=1000)
        with f3: st.write("##"); chk = st.checkbox("¿APOSTÉ?")
        with f4: st.write("##"); btn = st.form_submit_button("REGISTRAR")

        if btn and v_v:
            try:
                val = float(v_v.replace(',', '.'))
                impacto = (a_v * 9) if (chk and val >= 10) else (-float(a_v) if chk else 0.0)
                st.session_state.historial.append(val)
                st.session_state.registro_saldos.append(impacto)
                st.session_state.saldo_dinamico += impacto
                if val >= 10:
                    st.session_state.h_10x_input = datetime.now(py_tz).strftime("%H:%M")
                    if val >= 100: st.session_state.h_100x_input = datetime.now(py_tz).strftime("%H:%M")
                st.rerun()
            except: pass

# HISTORIAL DE BURBUJAS
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:12px; background:#111; border-radius:15px; border: 1px solid #333; margin-top:5px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER ÚLTIMA", use_container_width=True):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.rerun()
