import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.0", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .meta-alcanzada { background-color: #f1c40f; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.5rem; border: 3px solid #ffffff; margin-bottom: 10px; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    .semaforo { padding: 15px; border-radius: 12px; text-align: center; font-weight: 900; font-size: 1.4rem; margin: 10px 0px; }
    .radar-rosas { padding: 8px; border-radius: 5px; text-align: center; font-size: 0.9rem; font-weight: bold; margin-bottom: 10px; }
    .burbuja { min-width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; color: white; border: 2px solid #ffffff20; }
    /* Ajuste para pantallas pequeñas (ventana flotante) */
    h2 { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

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
    saldo_in = st.number_input("Saldo Inicial Gs.", value=110000, step=5000)
    meta_ganancia = st.number_input("Meta Gs.", value=100000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    modo = st.selectbox("Estrategia:", ["Estrategia del Hueco 10x o +", "Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"])
    
    if st.button("🔄 Reiniciar Todo"):
        st.session_state.clear()
        st.rerun()

# --- FUNCIÓN DE REGISTRO ---
def registrar_valor(valor):
    try:
        v_val = float(str(valor).replace(',', '.'))
        st.session_state.historial.append(v_val)
        py_tz = pytz.timezone('America/Asuncion')
        
        if v_val >= 10.0:
            st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
        
        if st.session_state.check_apuesta:
            ap_real = float(st.session_state.valor_apuesta_manual)
            target = 10.0 if ("10x" in modo or "Hueco" in modo) else 2.0 if "2x2" in modo else 1.50
            st.session_state.saldo_dinamico -= ap_real
            if v_val >= target: st.session_state.saldo_dinamico += (ap_real * target)
    except: pass

# --- INTERFAZ SUPERIOR (Métricas compactas) ---
ganancia_actual = st.session_state.saldo_dinamico - saldo_in

if ganancia_actual >= meta_ganancia:
    st.markdown(f'<div class="meta-alcanzada">🎯 META OK: +{int(ganancia_actual):,} Gs</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Saldo", f"{int(st.session_state.saldo_dinamico):,}")
c2.metric("Ganancia", f"+{int(max(0, ganancia_actual)):,}", delta_color="normal")
c3.metric("Pérdida", f"-{int(abs(min(0, ganancia_actual))):,}")

# --- MOTOR Y SEMÁFORO ---
def motor_semaforo(h, modo_sel):
    if len(h) < 2: return "🟡 ANALIZANDO", "#f1c40f", "black"
    if "Hueco" in modo_sel:
        hueco = 0
        for v in reversed(h):
            if v >= 10: break
            hueco += 1
        return (f"💖 HUECO ACTIVO ({hueco})", "#e91e63", "white") if hueco >= 25 else (f"⏳ CARGANDO ({hueco}/25)", "#2d3436", "white")
    if "2x2" in modo_sel:
        if h[-1] < 2.0 and h[-2] < 2.0: return "🟢 ENTRAR AHORA", "#00ff41", "black"
        return "🔴 ESPERANDO PATRÓN", "#2d3436", "white"
    return "🟢 LISTO", "#00ff41", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, modo)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)

# --- RADAR ---
v_desde_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    v_desde_rosa += 1
st.markdown(f'<div class="radar-rosas" style="background-color:#2d3436; color:#fd79a8; border: 1px solid #fd79a8;">📡 RADAR: {v_desde_rosa} vuelos sin 10x</div>', unsafe_allow_html=True)

# --- PANEL DE ENTRADA RÁPIDA ---
st.write("### ⚡ Registro Rápido")
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
if col_btn1.button("1.0x (PÉRDIDA)"): registrar_valor(1.0)
if col_btn2.button("1.5x (AZUL)"): registrar_valor(1.5)
if col_btn3.button("2.0x (MORADO)"): registrar_valor(2.0)
if col_btn4.button("10x (ROSA)"): registrar_valor(10.0)

st.markdown("---")
# Entrada manual por si sale un número raro
c_v, c_a, c_c = st.columns([2, 1, 1])
with c_v: 
    manual = st.text_input("Manual:", key="manual_in")
    if st.button("Registrar Manual"):
        registrar_valor(manual)
with c_a: st.number_input("Apuesta:", value=2000, key="valor_apuesta_manual")
with c_c: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

# --- HISTORIAL ---
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-15:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.1f}</div>'
    st.markdown(f'<div style="display:flex; gap:5px; overflow-x:auto;">{html_b}</div>', unsafe_allow_html=True)

if st.button("⬅️ Borrar Último"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.rerun()
