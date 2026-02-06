import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v6.2", page_icon="🦅", layout="wide")

# --- DISEÑO CSS RESTAURADO ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    /* Estilo de tarjetas para métricas */
    .metric-card { 
        background-color: #1e272e; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        border: 1px solid #374151;
    }
    .apuesta-box { background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.4rem; margin: 10px 0px; }
    .meta-alcanzada { background-color: #f1c40f; color: #000000; padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 2rem; border: 4px solid #ffffff; margin-bottom: 20px; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; }
    .radar-rosas { background-color: #2d3436; color: #fd79a8; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9rem; margin-top: -10px; font-weight: bold; border: 1px solid #fd79a8; }
    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 15px 5px; background: #00000050; border-radius: 10px; }
    .burbuja { min-width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; color: white; border: 2px solid #ffffff20; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 Aviator Elite PY v6.2")

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")
if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    meta_ganancia = st.number_input("Meta de Ganancia Gs.", value=20000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    modo = st.selectbox("Estrategia:", ["Estrategia del Hueco 10x o +", "Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"])
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- FUNCIONES ---
def registrar_valor(valor):
    try:
        v_val = float(str(valor).replace(',', '.'))
        st.session_state.historial.append(v_val)
        if v_val >= 10.0:
            st.session_state.hora_10x = datetime.now(pytz.timezone('America/Asuncion')).strftime("%H:%M")
        if st.session_state.check_apuesta:
            ap_real = float(st.session_state.valor_apuesta_manual)
            target = 10.0 if ("10x" in modo or "Hueco" in modo) else 2.0 if "2x2" in modo else 1.50
            st.session_state.saldo_dinamico -= ap_real
            if v_val >= target: st.session_state.saldo_dinamico += (ap_real * target)
    except: pass

# --- PANEL DE MÉTRICAS PERSONALIZADAS ---
ganancia_actual = st.session_state.saldo_dinamico - saldo_in
if ganancia_actual >= meta_ganancia and meta_ganancia > 0:
    st.markdown(f'<div class="meta-alcanzada">🎯 META ALCANZADA: +{int(ganancia_actual):,} Gs</div>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card" style="border-color:#ffffff;"><p style="margin:0;color:#bdc3c7;font-size:0.9rem;">SALDO ACTUAL</p><h2 style="margin:0;color:#ffffff;">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card" style="border-color:#00ff41;"><p style="margin:0;color:#bdc3c7;font-size:0.9rem;">GANANCIA</p><h2 style="margin:0;color:#00ff41;">+{int(max(0, ganancia_actual)):,} Gs</h2></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card" style="border-color:#ff3131;"><p style="margin:0;color:#bdc3c7;font-size:0.9rem;">PÉRDIDA</p><h2 style="margin:0;color:#ff3131;">-{int(abs(min(0, ganancia_actual))):,} Gs</h2></div>', unsafe_allow_html=True)

# --- MOTOR SEMÁFORO ---
def motor_semaforo(h, modo_sel):
    if len(h) < 2: return "🟡 ANALIZANDO", "#f1c40f", "black"
    if "Hueco" in modo_sel:
        hueco = 0
        for v in reversed(h):
            if v >= 10: break
            hueco += 1
        return (f"💖 HUECO ACTIVO ({hueco} v)", "#e91e63", "white") if hueco >= 25 else (f"⏳ CARGANDO HUECO ({hueco}/25)", "#2d3436", "white")
    return "🟢 SISTEMA LISTO", "#00ff41", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, modo)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)

# RADAR
v_desde_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    v_desde_rosa += 1
st.markdown(f'<div class="radar-rosas">📡 RADAR ROSA: {v_desde_rosa} vuelos sin 10x+</div>', unsafe_allow_html=True)

# --- PANEL DE ATAJOS RÁPIDOS ---
st.write("### ⚡ Registro de Rondas")
col_b1, col_b2, col_b3, col_b4 = st.columns(4)
if col_b1.button("🟦 1.0x", use_container_width=True): registrar_valor(1.0)
if col_b2.button("🟦 1.5x", use_container_width=True): registrar_valor(1.5)
if col_b3.button("🟪 2.0x", use_container_width=True): registrar_valor(2.0)
if col_b4.button("🌸 10x", use_container_width=True): registrar_valor(10.0)

st.markdown("---")
c_manual, c_ap, c_ch = st.columns([2, 1, 1])
with c_manual:
    val_m = st.text_input("Valor Manual:")
    if st.button("Registrar Manual"): registrar_valor(val_m)
with c_ap: st.number_input("Apuesta Gs:", value=2000.0, step=1000.0, key="valor_apuesta_manual")
with c_ch: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-20:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)

if st.button("⬅️ Borrar Último"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.rerun()
