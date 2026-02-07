import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.2", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ORIGINAL ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 15px; border-radius: 15px; 
        text-align: center; margin-bottom: 10px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.8rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 900; }
    .semaforo-box { padding: 30px; border-radius: 20px; text-align: center; margin-top: 10px; }
    .semaforo-texto { font-size: 2rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { 
        min-width: 65px; height: 60px; border-radius: 30px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; padding: 0 10px; margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = datetime.now(py_tz).strftime("%H:%M")
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- FUNCIONES ---
def contar_rondas_desde_rosa():
    count = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        count += 1
    return count

def obtener_semaforo():
    if len(st.session_state.historial) < 1: return "ESPERANDO DATOS...", "#333"
    sin_rosa = contar_rondas_desde_rosa()
    if sin_rosa >= 25: return "🟢 HUECO ACTIVO", "#27ae60"
    if sin_rosa >= 18: return "🟡 ANALIZANDO...", "#f1c40f"
    return "🔴 NO ENTRAR", "#c0392b"

# --- INTERFAZ ---
with st.sidebar:
    st.header("🦅 CONFIG")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=100000, step=10000)
    if not st.session_state.historial and st.session_state.saldo_dinamico == 0:
        st.session_state.saldo_dinamico = float(saldo_in)
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Hueco 10x+", "Cazador (10x)"])
    if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

st.title("🦅 AVIATOR ELITE v9.2")

# MÉTRICAS
ganancia = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card" style="border:1px solid #00ff41;"><p class="label-elite">Ganancia</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card" style="border:1px solid #ff3131;"><p class="label-elite">Rondas sin Rosa</p><h2 class="valor-elite" style="color:#e91e63!important;">{contar_rondas_desde_rosa()}</h2></div>', unsafe_allow_html=True)

# SEMÁFORO
txt_s, col_s = obtener_semaforo()
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# --- FORMULARIO CORREGIDO ---
st.markdown("<br>", unsafe_allow_html=True)
with st.form("registro_manual", clear_on_submit=True):
    col_in, col_ap, col_ck, col_btn = st.columns([2, 1, 1, 1])
    with col_in:
        # Placeholder más claro
        valor_raw = st.text_input("VUELO (Escriba y Enter):", key="input_vuelo")
    with col_ap:
        apuesta_val = st.number_input("APUESTA:", value=2000, step=1000)
    with col_ck:
        st.write("##")
        apostado = st.checkbox("¿APOSTÉ?")
    with col_btn:
        st.write("##")
        submit = st.form_submit_button("REGISTRAR")

    if submit:
        if valor_raw:
            try:
                # LIMPIEZA TOTAL: Quita letras, espacios y traduce comas a puntos
                dato_limpio = re.sub(r'[^0-9.,]', '', valor_raw).replace(',', '.')
                v_val = float(dato_limpio)
                
                impacto = 0.0
                if apostado:
                    # Cálculo de ganancia/pérdida
                    target = 10.0 if "10x" in st.session_state.modo_sel else 2.0
                    impacto = (apuesta_val * (target - 1)) if v_val >= target else -float(apuesta_val)
                
                st.session_state.historial.append(v_val)
                st.session_state.registro_saldos.append(impacto)
                st.session_state.saldo_dinamico += impacto
                st.rerun()
            except ValueError:
                # Si el dato es basura, simplemente no hace nada y no muestra error feo
                pass

# BOTÓN DESHACER
if st.button("🔙 DESHACER ÚLTIMA"):
    if st.session_state.historial:
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.session_state.historial.pop()
        st.rerun()

# HISTORIAL BURBUJAS
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-10:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:15px; border:1px solid #333;">{h_html}</div>', unsafe_allow_html=True)
