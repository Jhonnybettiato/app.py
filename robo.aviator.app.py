import streamlit as st
from datetime import datetime
import pytz
import streamlit.components.v1 as components
import pandas as pd
import io

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.9.0", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; text-transform: uppercase; letter-spacing: 3px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; height: 100%; }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 5px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; margin-bottom: 0px; }
    .cronometro { color: #00ff41; font-family: monospace; font-size: 0.9rem; font-weight: bold; margin-top: 5px; }
    
    input:focus { 
        border: 2px solid #00ff41 !important; 
        box-shadow: 0 0 15px #00ff41 !important;
        background-color: #050505 !important;
    }

    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; }
    .intervalo-tag { background: #222; color: #e91e63; border: 1px solid #e91e63; padding: 2px 8px; border-radius: 5px; font-weight: bold; margin: 2px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')

if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'registro_tiempos' not in st.session_state: st.session_state.registro_tiempos = []
if 'intervalos_rosas' not in st.session_state: st.session_state.intervalos_rosas = [] # Nueva lista
if 'rondas_desde_ultima' not in st.session_state: st.session_state.rondas_desde_ultima = 0
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 475000.0
if 'h_10x' not in st.session_state: st.session_state.h_10x = "00:00"
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"
if 'key_id' not in st.session_state: st.session_state.key_id = 0
if 'cap_ini' not in st.session_state: st.session_state.cap_ini = 475000.0

# --- FUNCIONES ---
def calcular_cronometro(hora_str):
    if hora_str == "---" or hora_str == "00:00": return "00m 00s"
    try:
        ahora = datetime.now(py_tz)
        hora_obj = datetime.strptime(hora_str, "%H:%M")
        hora_final = ahora.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0, microsecond=0)
        diff = ahora - hora_final
        ts = int(diff.total_seconds())
        if ts < 0: ts += 86400
        return f"{ts // 60:02d}m {ts % 60:02d}s"
    except: return "00m 00s"

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
                ahora_f = datetime.now(py_tz).strftime("%H:%M")
                
                # Lógica de Intervalos
                if val >= 10.0:
                    st.session_state.intervalos_rosas.append(st.session_state.rondas_desde_ultima)
                    st.session_state.rondas_desde_ultima = 0 # Reset
                    st.session_state.h_10x = ahora_f
                    if val >= 100.0: st.session_state.h_100x = ahora_f
                else:
                    st.session_state.rondas_desde_ultima += 1
                
                st.session_state.historial.append(val)
                st.session_state.registro_saldos.append(gan)
                st.session_state.registro_tiempos.append(ahora_f)
                st.session_state.saldo_dinamico += gan
                st.session_state.key_id += 1
            except: pass

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTES")
    nuevo_cap = st.number_input("Capital Inicial", value=float(st.session_state.cap_ini))
    if nuevo_cap != st.session_state.cap_ini:
        st.session_state.saldo_dinamico += (nuevo_cap - st.session_state.cap_ini)
        st.session_state.cap_ini = nuevo_cap
        st.rerun()

    st.markdown("---")
    # VENTANA DE INTERVALOS (Tu idea)
    st.markdown("### 📊 DISTANCIA ENTRE ROSAS")
    if st.session_state.intervalos_rosas:
        for i, dist in enumerate(reversed(st.session_state.intervalos_rosas[-10:])):
            st.markdown(f"Rosa {len(st.session_state.intervalos_rosas)-i}: **{dist} rondas de espera**")
    else:
        st.write("Esperando primera rosa...")

    if st.button("🔄 REINICIAR TODO"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE ROBOT v9.9.0</div>', unsafe_allow_html=True)

# Dashboard
c1, c2, c3, c4 = st.columns(4)
res_ac = st.session_state.saldo_dinamico - st.session_state.cap_ini
c1.markdown(f'<div class="elite-card"><p class="label-elite">💰 SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="elite-card" style="border-color:{"#0f4" if res_ac >=0 else "#f31"};"><p class="label-elite">📈 GANANCIA</p><h2 class="valor-elite">{int(res_ac):,}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="elite-card"><p class="label-elite">✈️ ÚLTIMA 10X</p><h2 class="valor-elite" style="color:#9b59b6 !important;">{st.session_state.h_10x}</h2><p class="cronometro">⏱️ hace {calcular_cronometro(st.session_state.h_10x)}</p></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="elite-card"><p class="label-elite">🚀 ÚLTIMA 100X</p><h2 class="valor-elite" style="color:#e91e63 !important;">{st.session_state.h_100x}</h2><p class="cronometro">⏱️ hace {calcular_cronometro(st.session_state.h_100x)}</p></div>', unsafe_allow_html=True)

# Semáforo
sin_rosa = st.session_state.rondas_desde_ultima
col_sem, msg = ("#ff4b4b", "🚫 RIESGO") if sin_rosa <= 20 else ("#ffeb3b", "⚠️ ESPERAR") if sin_rosa <= 30 else ("#00ff41", "🚀 ENTRADA") if sin_rosa <= 40 else ("#9b59b6", "🔥 ALERTA")
st.markdown(f'<div style="background-color:{col_sem}; padding:20px; border-radius:15px; text-align:center; margin-bottom:15px; border:2px solid rgba(255,255,255,0.2);"><h2 style="color:{"black" if sin_rosa in range(21,41) else "white"}; margin:0; font-weight:900;">RONDAS SIN ROSA: {sin_rosa}</h2><h4 style="color:{"black" if sin_rosa in range(21,41) else "white"}; margin:5px 0 0 0;">{msg}</h4></div>', unsafe_allow_html=True)

# Entrada
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
with r1: st.text_input("VALOR DEL VUELO", value="", key=f"input_{st.session_state.key_id}", on_change=registrar, placeholder="INGRESE VALOR")
with r2: st.number_input("APUESTA", value=2000, key="in_apuesta")
with r3: st.write("##"); st.checkbox("¿APOSTÉ?", key="in_chk")
with r4: st.write("##"); st.button("REGISTRAR 🚀", on_click=registrar)
st.markdown('</div>', unsafe_allow_html=True)

# Foco y Historial
components.html(f"""<script>function setFocus(){{var inputs = window.parent.document.querySelectorAll('input[placeholder="INGRESE VALOR"]');if (inputs.length > 0) inputs[0].focus();}}setFocus();setTimeout(setFocus, 300);</script>""", height=0)

if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#e91e63" if v >= 10 else "#9b59b6" if v >= 2 else "#3498db"}; border:{"3px solid gold" if v >= 100 else "none"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:20px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER"):
    if st.session_state.historial:
        last_val = st.session_state.historial.pop()
        st.session_state.registro_tiempos.pop()
        st.session_state.registro_saldos.pop()
        if last_val >= 10.0 and st.session_state.intervalos_rosas:
            st.session_state.rondas_desde_ultima = st.session_state.intervalos_rosas.pop()
        else:
            st.session_state.rondas_desde_ultima -= 1
        st.rerun()
