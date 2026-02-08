import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.5.2", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-title { color: #FFFFFF; font-size: 2.5rem; font-weight: 900; text-align: center; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }
    .elite-card { 
        background-color: #121212; padding: 15px; border-radius: 15px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.75rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2rem; font-weight: 900; line-height: 1.1; }
    
    /* Ventanas de Saldo Dinámicas */
    .win-card { background-color: #003311; border: 2px solid #00ff41; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 0 15px rgba(0,255,65,0.2); }
    .loss-card { background-color: #330000; border: 2px solid #ff3131; padding: 15px; border-radius: 15px; text-align: center; box-shadow: 0 0 15px rgba(255,49,49,0.2); }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px #2ecc71; }
        50% { box-shadow: 0 0 35px #2ecc71; border-color: #fff; }
        100% { box-shadow: 0 0 5px #2ecc71; }
    }
    .semaforo-box { padding: 35px; border-radius: 25px; text-align: center; margin-top: 15px; border: 3px solid transparent; transition: 0.4s; }
    .glow-active { animation: glow 1s infinite; }
    .semaforo-texto { font-size: 2.5rem; font-weight: 900; color: white; margin: 0; text-shadow: 2px 2px 5px rgba(0,0,0,0.7); }
    
    .burbuja { 
        min-width: 65px; height: 60px; border-radius: 30px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; margin-right: 6px; font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x' not in st.session_state: st.session_state.h_10x = "00:00"
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"

# --- FUNCIONES CORE ---
def get_minutos(hora_str):
    if "---" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

def calc_sin_rosa():
    """Calcula las rondas sin rosas con reset instantáneo"""
    if not st.session_state.historial: return 0
    # Si la última burbuja registrada es rosa, el contador DEBE ser 0
    if float(st.session_state.historial[-1]) >= 10.0: return 0
    count = 0
    for v in reversed(st.session_state.historial):
        if float(v) >= 10.0: break
        count += 1
    return count

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🦅 CONFIG")
    saldo_in = st.number_input("Capital Inicial (Gs.)", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    if st.button("🔄 REINICIAR ROBOT"): st.session_state.clear(); st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="main-title">🦅 AVIATOR ELITE ROBOT v9.5.2</h1>', unsafe_allow_html=True)

sin_rosa_actual = calc_sin_rosa()
ganancia_neta = st.session_state.saldo_dinamico - saldo_in

# DASHBOARD SUPERIOR
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="elite-card"><p class="label-elite">SALDO ACTUAL</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)

with m2:
    if ganancia_neta >= 0:
        st.markdown(f'<div class="win-card"><p class="label-elite" style="color:#00ff41!important;">GANANCIA ACUMULADA</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(ganancia_neta):,}</h2></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="loss-card"><p class="label-elite" style="color:#ff3131!important;">PÉRDIDA ACTUAL</p><h2 class="valor-elite" style="color:#ff3131!important;">{int(ganancia_neta):,}</h2></div>', unsafe_allow_html=True)

with m3:
    st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 10X</p><h2 class="valor-elite">{st.session_state.h_10x}</h2><p style="color:#00ff41; font-size:0.9rem; margin:0; font-weight:bold;">⏱️ {get_minutos(st.session_state.h_10x)} min</p></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 100X</p><h2 class="valor-elite">{st.session_state.h_100x}</h2><p style="color:#00ff41; font-size:0.9rem; margin:0; font-weight:bold;">⏱️ {get_minutos(st.session_state.h_100x)} min</p></div>', unsafe_allow_html=True)

# SEMÁFORO DE ESTRATEGIA
if sin_rosa_actual >= 40:
    txt, col, clase = "🛑 STOP LOSS: PARAR AHORA", "#ff3131", ""
elif sin_rosa_actual >= 30:
    txt, col, clase = "🔥 ¡ENTRAR AHORA! (META 30)", "#27ae60", "glow-active"
elif sin_rosa_actual >= 25:
    txt, col, clase = "🟡 PREPARAR (ZONA 25+)", "#f39c12", ""
else:
    txt, col, clase = f"⏳ ESPERAR ({sin_rosa_actual}/30)", "#333", ""

st.markdown(f'<div class="semaforo-box {clase}" style="background-color:{col};"><p class="semaforo-texto">{txt}</p></div>', unsafe_allow_html=True)

# --- PANEL DE REGISTRO ---
with st.container():
    with st.form("registro_pro_v2", clear_on_submit=True):
        f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
        with f1: v_v = st.text_input("VALOR DEL VUELO (Ej: 10.50)")
        with f2: a_v = st.number_input("APUESTA Gs.", value=2000, step=1000)
        with f3: st.write("##"); chk = st.checkbox("¿APOSTÉ?")
        with f4: st.write("##"); btn = st.form_submit_button("REGISTRAR 🚀")

        if btn and v_v:
            try:
                val = float(v_v.replace(',', '.'))
                # Cálculo de saldo: Si es rosa y aposté, gano 9 veces la apuesta (10x total)
                impacto = (a_v * 9) if (chk and val >= 10) else (-float(a_v) if chk else 0.0)
                
                st.session_state.historial.append(val)
                st.session_state.registro_saldos.append(impacto)
                st.session_state.saldo_dinamico += impacto
                
                if val >= 10:
                    ahora = datetime.now(py_tz).strftime("%H:%M")
                    st.session_state.h_10x = ahora
                    if val >= 100: st.session_state.h_100x = ahora
                
                st.rerun()
            except: st.error("Formato de número inválido")

# BURBUJAS HISTÓRICAS
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:10px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER ÚLTIMO REGISTRO", use_container_width=True):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.rerun()
