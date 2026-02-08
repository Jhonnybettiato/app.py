import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.5.9", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; text-transform: uppercase; letter-spacing: 3px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; }
    .win-box { background-color: #003311; border: 2px solid #00ff41; padding: 15px; border-radius: 15px; text-align: center; }
    .loss-box { background-color: #330000; border: 2px solid #ff3131; padding: 15px; border-radius: 15px; text-align: center; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #2ecc71; } 50% { box-shadow: 0 0 30px #2ecc71; } 100% { box-shadow: 0 0 5px #2ecc71; } }
    .semaforo { padding: 30px; border-radius: 20px; text-align: center; margin-top: 10px; transition: 0.3s; }
    .fuego { animation: pulse 1s infinite; border: 2px solid #fff; }
    .semaforo-txt { font-size: 2rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
ahora_inicial = datetime.now(py_tz).strftime("%H:%M")

if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x' not in st.session_state: st.session_state.h_10x = ahora_inicial
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"
# Key dinámica para resetear el input
if 'input_key' not in st.session_state: st.session_state.input_key = 0

# --- FUNCIÓN DE REGISTRO CON AUTO-RESET ---
def registrar_vuelo():
    # Obtener el valor actual antes del reset
    v_vuelo = st.session_state[f"input_vuelo_{st.session_state.input_key}"]
    a_vuelo = st.session_state.input_apuesta
    chk_ap = st.session_state.input_chk
    
    # Solo procesar si el valor es razonable (evita registros accidentales de 1.00 si no se cambió)
    imp = (a_vuelo * 9) if (chk_ap and v_vuelo >= 10.0) else (-float(a_vuelo) if chk_ap else 0.0)
    
    st.session_state.historial.append(v_vuelo)
    st.session_state.registro_saldos.append(imp)
    st.session_state.saldo_dinamico += imp
    
    if v_vuelo >= 10.0:
        ahora_f = datetime.now(py_tz).strftime("%H:%M")
        st.session_state.h_10x = ahora_f
        if v_vuelo >= 100.0: st.session_state.h_100x = ahora_f
    
    # EL SECRETO: Cambiamos la key para que Streamlit cree un componente nuevo y vacío
    st.session_state.input_key += 1

# --- LÓGICA DE TIEMPO ---
def get_mins(h_str):
    if "---" in h_str or ":" not in h_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_f = py_tz.localize(datetime.strptime(h_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        d = int((ahora - h_f).total_seconds() / 60)
        return d if d >= 0 else (d + 1440)
    except: return "?"

def get_sin_rosa():
    if not st.session_state.historial: return 0
    if float(st.session_state.historial[-1]) >= 10.0: return 0
    c = 0
    for v in reversed(st.session_state.historial):
        if float(v) >= 10.0: break
        c += 1
    return c

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTES PRO")
    s_ini = st.number_input("Capital Inicial", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(s_ini)
        st.session_state.primer_inicio = False
    
    st.divider()
    st.markdown("### 🕒 EDITAR HORARIOS")
    new_h10 = st.text_input("Editar Última 10x", value=st.session_state.h_10x)
    new_h100 = st.text_input("Editar Última 100x", value=st.session_state.h_100x)
    
    if st.button("✅ APLICAR HORARIOS"):
        st.session_state.h_10x = new_h10
        st.session_state.h_100x = new_h100
        st.rerun()

    st.divider()
    if st.button("🔄 RESET COMPLETO"): st.session_state.clear(); st.rerun()

# --- APP ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE ROBOT v9.5.9</div>', unsafe_allow_html=True)

sin_rosa = get_sin_rosa()
ganancia = st.session_state.saldo_dinamico - s_ini

# DASHBOARD
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="elite-card"><p class="label-elite">SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
with c2:
    cl_gan = "win-box" if ganancia >= 0 else "loss-box"
    st.markdown(f'<div class="{cl_gan}"><p class="label-elite">RESULTADO</p><h2 class="valor-elite">{int(ganancia):,}</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 10X</p><h2 class="valor-elite">{st.session_state.h_10x}</h2><p style="color:#0f4;font-size:0.8rem;">⏱️ {get_mins(st.session_state.h_10x)} min</p></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 100X</p><h2 class="valor-elite">{st.session_state.h_100x}</h2><p style="color:#0f4;font-size:0.8rem;">⏱️ {get_mins(st.session_state.h_100x)} min</p></div>', unsafe_allow_html=True)

# SEMÁFORO
if sin_rosa >= 40: t, col, anim = "🛑 STOP LOSS", "#ff3131", ""
elif sin_rosa >= 30: t, col, anim = "🔥 ENTRAR AHORA", "#27ae60", "fuego"
elif sin_rosa >= 25: t, col, anim = "🟡 PREPARAR", "#f39c12", ""
else: t, col, anim = f"⏳ ESPERAR ({sin_rosa}/30)", "#333", ""

st.markdown(f'<div class="semaforo {anim}" style="background-color:{col};"><p class="semaforo-txt">{t}</p></div>', unsafe_allow_html=True)

# --- PANEL DE REGISTRO CON AUTO-LIMPIEZA ---
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns([2, 1, 1, 1])

with r1: 
    # Usamos una key dinámica para que el input se "resetee" solo tras registrar
    st.number_input("MULTIPLICADOR FINAL", min_value=1.0, step=0.01, format="%.2f", 
                    key=f"input_vuelo_{st.session_state.input_key}", 
                    on_change=registrar_vuelo)
with r2: st.number_input("APUESTA Gs.", value=2000, step=1000, key="input_apuesta")
with r3: st.write("##"); st.checkbox("¿APOSTADO?", key="input_chk")
with r4: st.write("##"); st.button("REGISTRAR 🚀", on_click=registrar_vuelo)
st.markdown('</div>', unsafe_allow_html=True)

# HISTORIAL
if st.session_state.historial:
    h_h = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:10px;">{h_h}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER ÚLTIMO", use_container_width=True):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.rerun()
