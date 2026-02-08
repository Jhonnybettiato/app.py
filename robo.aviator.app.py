import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.6.4", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; text-transform: uppercase; letter-spacing: 3px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; height: 100%; }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 5px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; margin: 0; }
    .win-box { background-color: #003311; border: 2px solid #00ff41; padding: 15px; border-radius: 15px; text-align: center; height: 100%; }
    .loss-box { background-color: #330000; border: 2px solid #ff3131; padding: 15px; border-radius: 15px; text-align: center; height: 100%; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #2ecc71; } 50% { box-shadow: 0 0 30px #2ecc71; } 100% { box-shadow: 0 0 5px #2ecc71; } }
    .semaforo { padding: 25px; border-radius: 20px; text-align: center; margin: 15px 0; transition: 0.3s; }
    .fuego { animation: pulse 1s infinite; border: 2px solid #fff; }
    .semaforo-txt { font-size: 1.8rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; flex-shrink: 0; }
    
    /* Forzar foco visual */
    input:focus { border: 2px solid #00ff41 !important; box-shadow: 0 0 10px #00ff41 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'h_10x' not in st.session_state: st.session_state.h_10x = "00:00"
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"
if 'key_id' not in st.session_state: st.session_state.key_id = 0

# --- FUNCIONES DE LÓGICA ---
def get_mins(h_str):
    if "---" in h_str or ":" not in h_str or h_str == "00:00": return "?"
    try:
        ahora = datetime.now(py_tz)
        h_f = py_tz.localize(datetime.strptime(h_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        d = int((ahora - h_f).total_seconds() / 60)
        return d if d >= 0 else (d + 1440)
    except: return "?"

def registrar():
    # Captura el valor del input actual usando la key dinámica
    curr_key = f"input_{st.session_state.key_id}"
    raw_val = st.session_state[curr_key].replace(',', '.')
    
    if raw_val:
        try:
            val = float(raw_val)
            apuesta = st.session_state.in_apuesta
            jugado = st.session_state.in_chk
            
            # Cálculo de impacto económico
            ganancia = (apuesta * 9) if (jugado and val >= 10.0) else (-float(apuesta) if jugado else 0.0)
            
            # Guardar datos
            st.session_state.historial.append(val)
            st.session_state.registro_saldos.append(ganancia)
            st.session_state.saldo_dinamico += ganancia
            
            # Actualizar tiempos
            ahora_f = datetime.now(py_tz).strftime("%H:%M")
            if val >= 10.0: st.session_state.h_10x = ahora_f
            if val >= 100.0: st.session_state.h_100x = ahora_f
            
            # Cambiar key para limpiar y reenfocar
            st.session_state.key_id += 1
        except: pass

# --- CÁLCULO DE ESTRATEGIA ---
sin_rosa = 0
if st.session_state.historial:
    if st.session_state.historial[-1] < 10.0:
        for v in reversed(st.session_state.historial):
            if v >= 10.0: break
            sin_rosa += 1

# --- INTERFAZ GRAFICA ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE ROBOT v9.6.4</div>', unsafe_allow_html=True)

# DASHBOARD SUPERIOR
cols = st.columns(4)
with cols[0]: 
    st.markdown(f'<div class="elite-card"><p class="label-elite">SALDO ACTUAL</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
with cols[1]:
    res = st.session_state.saldo_dinamico - 50000 # Capital base
    cl = "win-box" if res >= 0 else "loss-box"
    st.markdown(f'<div class="{cl}"><p class="label-elite">RESULTADO ACUM.</p><h2 class="valor-elite">{int(res):,}</h2></div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 10X</p><h2 class="valor-elite">{st.session_state.h_10x}</h2><p style="color:#0f4;font-size:0.7rem;margin:0;">⏱️ {get_mins(st.session_state.h_10x)} min</p></div>', unsafe_allow_html=True)
with cols[3]:
    st.markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 100X</p><h2 class="valor-elite">{st.session_state.h_100x}</h2><p style="color:#0f4;font-size:0.7rem;margin:0;">⏱️ {get_mins(st.session_state.h_100x)} min</p></div>', unsafe_allow_html=True)

# SEMÁFORO DE ESTRATEGIA
if sin_rosa >= 40: txt, color, anim = "🛑 STOP LOSS / ESPERAR", "#ff3131", ""
elif sin_rosa >= 30: txt, color, anim = "🔥 ENTRAR AHORA", "#27ae60", "fuego"
elif sin_rosa >= 25: txt, color, anim = "🟡 PREPARAR ENTRADA", "#f39c12", ""
else: txt, color, anim = f"⏳ ESPERAR RONDAS ({sin_rosa}/30)", "#333", ""

st.markdown(f'<div class="semaforo {anim}" style="background-color:{color};"><p class="semaforo-txt">{txt}</p></div>', unsafe_allow_html=True)

# PANEL DE ENTRADA (AQUÍ ESTÁ EL TRUCO DEL FOCO)
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
with r1:
    # autofocus=True hace que al crearse el componente (cada enter), el cursor salte allí solo
    st.text_input("MULTIPLICADOR FINAL", value="", placeholder="Número + Enter", 
                  key=f"input_{st.session_state.key_id}", on_change=registrar)
with r2:
    st.number_input("APUESTA Gs.", value=2000, step=1000, key="in_apuesta")
with r3:
    st.write("##")
    st.checkbox("¿APOSTÉ?", key="in_chk")
with r4:
    st.write("##")
    st.button("REGISTRAR 🚀", on_click=registrar, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# HISTORIAL VISUAL
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:20px;">{h_html}</div>', unsafe_allow_html=True)

# BOTONES DE CONTROL
st.write("---")
c_down1, c_down2 = st.columns(2)
with c_down1:
    if st.button("🔙 DESHACER ÚLTIMA", use_container_width=True):
        if st.session_state.historial:
            st.session_state.historial.pop()
            st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
            st.rerun()
with c_down2:
    if st.button("🔄 REINICIAR TODO", use_container_width=True):
        st.session_state.clear()
        st.rerun()
