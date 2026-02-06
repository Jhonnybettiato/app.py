import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v5.8", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-weight: 850 !important; font-size: 2.2rem !important; }
    .stMetric { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .apuesta-box { background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.4rem; margin: 10px 0px; }
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; }
    .radar-rosas { background-color: #2d3436; color: #fd79a8; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9rem; margin-top: -10px; font-weight: bold; }
    
    /* Estilos para las cajas de tiempo */
    .time-container { display: flex; gap: 10px; margin: 10px 0px; }
    .time-card { flex: 1; background-color: #1e272e; padding: 10px; border-radius: 10px; text-align: center; border: 1px dashed #ef5777; }
    .time-card.giant { border-color: #f1c40f; } /* Dorado para 100x */
    .time-label { font-size: 0.8rem; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #ef5777; }
    .time-card.giant .time-value { color: #f1c40f; }
    .time-elapsed { font-size: 0.85rem; color: #00ff41; font-weight: bold; }

    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 10px 0px; }
    .burbuja { min-width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 Aviator Elite PY v5.8")

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'ultimo_cambio_saldo' not in st.session_state: st.session_state.ultimo_cambio_saldo = 0.0

# Horarios iniciales
py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")
if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    obj_pct = st.slider("Meta %", 10, 100, 20)
    modo = st.selectbox("Estrategia:", 
                        ["Estrategia del Hueco 10x o +", "Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"], 
                        key="modo_juego")
    
    st.session_state.hora_10x = st.text_input("Editar Hora 10x (HH:MM):", value=st.session_state.hora_10x)
    st.session_state.hora_100x = st.text_input("Editar Hora 100x (HH:MM):", value=st.session_state.hora_100x)
    
    div_ap = 25 if "10x" in modo or "Hueco" in modo else 8 if "2x2" in modo else 5
    apuesta_auto = max(2000, int(((saldo_in * (obj_pct/100)) / div_ap) // 1000) * 1000)

    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- LÓGICA DE TIEMPO ---
def get_minutos(hora_str):
    if hora_str == "---": return "?"
    try:
        py_tz = pytz.timezone('America/Asuncion')
        ahora = datetime.now(py_tz)
        h_rosa = datetime.strptime(hora_str, "%H:%M")
        h_rosa = py_tz.localize(datetime(ahora.year, ahora.month, ahora.day, h_rosa.hour, h_rosa.minute))
        diff = ahora - h_rosa
        minutos = int(diff.total_seconds() / 60)
        return minutos if minutos >= 0 else (minutos + 1440)
    except: return "?"

# --- REGISTRO ---
def registrar_vuelo():
    if st.session_state.entrada_vuelo:
        try:
            v_val = float(st.session_state.entrada_vuelo.replace(',', '.'))
            st.session_state.historial.append(v_val)
            py_tz = pytz.timezone('America/Asuncion')
            
            if v_val >= 100.0:
                st.session_state.hora_100x = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M") # También es una rosa
            elif v_val >= 10.0:
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            
            # Lógica saldo... (omito por brevedad pero sigue igual)
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                target = 10.0 if ("10x" in st.session_state.modo_juego or "Hueco" in st.session_state.modo_juego) else 2.0 if "2x2" in st.session_state.modo_juego else 1.50
                st.session_state.saldo_dinamico -= ap_real
                if v_val > target: st.session_state.saldo_dinamico += (ap_real * target)
        except: pass
        st.session_state.entrada_vuelo = ""

# --- INTERFAZ ---
diferencia_gs = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(st.session_state.saldo_dinamico):,} Gs")
c2.metric("Ganancias", f"{int(max(0, diferencia_gs)):,} Gs")
c3.metric("Perdidas", f"{int(abs(min(0, diferencia_gs))):,} Gs")

# SEMÁFORO Y RADAR (Igual que antes...)
v_desde_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    v_desde_rosa += 1
st.markdown(f'<div class="radar-rosas">📡 RADAR ROSA: {v_desde_rosa} vuelos sin 10x+</div>', unsafe_allow_html=True)

# --- NUEVO PANEL DE TIEMPOS DOBLE ---
min_10x = get_minutos(st.session_state.hora_10x)
min_100x = get_minutos(st.session_state.hora_100x)

st.markdown(f"""
    <div class="time-container">
        <div class="time-card">
            <div class="time-label">🌸 ÚLTIMA ROSA (10x)</div>
            <div class="time-value">{st.session_state.hora_10x} hs</div>
            <div class="time-elapsed">⏱️ {min_10x} min</div>
        </div>
        <div class="time-card giant">
            <div class="time-label">👑 GIGANTE (100x+)</div>
            <div class="time-value">{st.session_state.hora_100x} hs</div>
            <div class="time-elapsed">⏱️ {min_100x} min</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {apuesta_auto:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_v, col_m, col_c = st.columns([2, 1, 1])
with col_v: st.text_input("Resultado:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_m: st.number_input("Gs. Apostados:", value=float(apuesta_auto), step=1000.0, key="valor_apuesta_manual")
with col_c: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")
