import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.3.4", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 10px; border-radius: 12px; 
        text-align: center; margin-bottom: 5px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 0.9rem; }
    .semaforo-box { padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .semaforo-texto { font-size: 1.5rem; font-weight: 900; color: white; margin: 0; }
    
    .burbuja { 
        min-width: 55px; height: 50px; border-radius: 25px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; margin-right: 4px; font-size: 0.85rem;
    }
    label { color: white !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'historial_rosas' not in st.session_state: st.session_state.historial_rosas = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = "00:00"
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- FUNCIONES CORE ---
def obtener_sin_rosa():
    if not st.session_state.historial: return 0
    if float(st.session_state.historial[-1]) >= 10.0: return 0
    count = 0
    for v in reversed(st.session_state.historial):
        if float(v) >= 10.0: break
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

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🦅 CONFIG")
    saldo_in = st.number_input("Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Hueco 10x+", "Cazador (10x)"])
    if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

# --- UI PRINCIPAL ---
st.title("🦅 AVIATOR ELITE v9.3.4")

# Cálculo de valores actuales
sin_rosa_val = obtener_sin_rosa()
ganancia_neta = st.session_state.saldo_dinamico - saldo_in

# Bloque de Métricas
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="elite-card" style="border:1px solid #fff;"><p class="label-elite">SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="elite-card" style="border:1px solid #00ff41;"><p class="label-elite">GANANCIA</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,}</h2></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="elite-card" style="border:1px solid #ff3131;"><p class="label-elite">SIN ROSA</p><h2 class="valor-elite" style="color:#e91e63!important;">{sin_rosa_val}</h2></div>', unsafe_allow_html=True)

# Relojes
r1, r2 = st.columns(2)
with r1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.session_state.h_10x_input = st.text_input("H10", value=st.session_state.h_10x_input, label_visibility="collapsed", key="h10")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with r2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.session_state.h_100x_input = st.text_input("H100", value=st.session_state.h_100x_input, label_visibility="collapsed", key="h100")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)

# Semáforo
txt_s, col_s = ("🟢 HUECO ACTIVO", "#27ae60") if sin_rosa_val >= 25 else ("🔴 NO ENTRAR", "#c0392b")
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# --- 🚀 REGISTRO Y HISTORIAL (UNIFICADOS ABAJO) ---
with st.container():
    with st.form("form_v934", clear_on_submit=True):
        f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
        with f1: v_vuelo = st.text_input("VALOR DEL VUELO (Ej: 2.50)")
        with f2: a_vuelo = st.number_input("APUESTA", value=2000, step=1000)
        with f3: st.write("##"); check_ap = st.checkbox("¿APOSTÉ?")
        with f4: st.write("##"); btn_reg = st.form_submit_button("REGISTRAR")

        if btn_reg:
            if v_vuelo.strip():
                try:
                    # Limpieza total de entrada
                    val_clean = float(re.sub(r'[^0-9.]', '', v_vuelo.replace(',', '.')))
                    
                    # Impacto en dinero
                    imp = 0.0
                    if check_ap:
                        meta = 10.0 if "10x" in st.session_state.modo_sel else 1.5
                        imp = (a_vuelo * (meta - 1)) if val_clean >= meta else -float(a_vuelo)
                    
                    # Guardar y Forzar salida del formulario
                    st.session_state.historial.append(val_clean)
                    st.session_state.registro_saldos.append(imp)
                    st.session_state.saldo_dinamico += imp
                    
                    if val_clean >= 10:
                        ahora = datetime.now(py_tz).strftime("%H:%M")
                        st.session_state.h_10x_input = ahora
                        st.session_state.historial_rosas.append({"valor": val_clean, "hora": ahora})
                        if val_clean >= 100: st.session_state.h_100x_input = ahora
                    
                    st.rerun()
                except ValueError:
                    st.warning("Escribe solo números (Ej: 5.20)")
            else:
                st.warning("Campo vacío")

# BURBUJAS HISTÓRICAS
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if float(v) < 2 else "#9b59b6" if float(v) < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-14:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:10px; background:#111; border-radius:15px; border: 1px solid #333; margin-top:2px; margin-bottom:10px;">{h_html}</div>', unsafe_allow_html=True)

# Botón Deshacer
if st.button("🔙 DESHACER ÚLTIMA", use_container_width=True):
    if st.session_state.historial:
        v = st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        if v >= 10: st.session_state.historial_rosas.pop()
        st.rerun()
