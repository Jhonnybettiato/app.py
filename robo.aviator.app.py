import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v6.0", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .apuesta-box { background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.4rem; margin: 10px 0px; }
    .meta-alcanzada { background-color: #f1c40f; color: #000000; padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 2rem; border: 4px solid #ffffff; margin-bottom: 20px; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; }
    .radar-rosas { background-color: #2d3436; color: #fd79a8; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9rem; margin-top: -10px; font-weight: bold; }
    .time-container { display: flex; gap: 10px; margin: 10px 0px; }
    .time-card { flex: 1; background-color: #1e272e; padding: 10px; border-radius: 10px; text-align: center; border: 1px dashed #ef5777; }
    .time-card.giant { border-color: #f1c40f; }
    .time-label { font-size: 0.8rem; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #ef5777; }
    .time-card.giant .time-value { color: #f1c40f; }
    .time-elapsed { font-size: 0.85rem; color: #00ff41; font-weight: bold; }
    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 15px 5px; background: #00000050; border-radius: 10px; }
    .burbuja { min-width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; color: white; border: 2px solid #ffffff20; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 Aviator Elite PY v6.0")

# 2. Inicialización de variables
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")
if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    
    # Nuevo campo de Meta fija en Gs.
    meta_ganancia = st.number_input("Meta de Ganancia Gs.", value=20000, step=5000)
    
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    modo = st.selectbox("Estrategia:", ["Estrategia del Hueco 10x o +", "Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"])
    
    st.session_state.hora_10x = st.text_input("Editar Hora 10x:", value=st.session_state.hora_10x)
    st.session_state.hora_100x = st.text_input("Editar Hora 100x:", value=st.session_state.hora_100x)
    
    # Apuesta sugerida fija o basada en un cálculo simple (no en % de meta)
    apuesta_sugerida_base = 2000 if "10x" in modo else 5000

    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- FUNCIONES ---
def registrar_vuelo():
    if st.session_state.entrada_vuelo:
        try:
            v_val = float(st.session_state.entrada_vuelo.replace(',', '.'))
            st.session_state.historial.append(v_val)
            py_tz = pytz.timezone('America/Asuncion')
            
            if v_val >= 100.0:
                st.session_state.hora_100x = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            elif v_val >= 10.0:
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                # Determinamos el multiplicador objetivo según el modo para el cálculo del saldo
                target = 10.0 if ("10x" in modo or "Hueco" in modo) else 2.0 if "2x2" in modo else 1.50
                st.session_state.saldo_dinamico -= ap_real
                if v_val >= target: 
                    st.session_state.saldo_dinamico += (ap_real * target)
        except: pass
        st.session_state.entrada_vuelo = ""

# --- ALERTA DE META ALCANZADA ---
ganancia_actual = st.session_state.saldo_dinamico - saldo_in
if ganancia_actual >= meta_ganancia and meta_ganancia > 0:
    st.markdown(f'<div class="meta-alcanzada">🎯 META ALCANZADA: +{int(ganancia_actual):,} Gs<br><span style="font-size:1rem;">¡ES HORA DE RETIRAR!</span></div>', unsafe_allow_html=True)

# --- INTERFAZ DE MÉTRICAS ---
color_ganancia = "#00ff41"
color_perdida = "#ff3131"

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div style="background-color:#1e272e;padding:15px;border-radius:10px;border:1px solid #374151;text-align:center;"><p style="margin:0;color:#bdc3c7;">Saldo Actual</p><h2 style="margin:0;color:#ffffff;">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2:
    val_g = max(0, ganancia_actual)
    st.markdown(f'<div style="background-color:#1e272e;padding:15px;border-radius:10px;border:1px solid {color_ganancia if val_g > 0 else "#374151"};text-align:center;"><p style="margin:0;color:#bdc3c7;">Ganancia</p><h2 style="margin:0;color:{color_ganancia};">+{int(val_g):,} Gs</h2></div>', unsafe_allow_html=True)
with c3:
    val_p = abs(min(0, ganancia_actual))
    st.markdown(f'<div style="background-color:#1e272e;padding:15px;border-radius:10px;border:1px solid {color_perdida if val_p > 0 else "#374151"};text-align:center;"><p style="margin:0;color:#bdc3c7;">Pérdida</p><h2 style="margin:0;color:{color_perdida};">-{int(val_p):,} Gs</h2></div>', unsafe_allow_html=True)

# --- MOTOR SEMÁFORO ---
def motor_semaforo(h, modo_sel):
    if len(h) < 3: return "🟡 ANALIZANDO FLUJO", "#f1c40f", "black"
    if "Hueco" in modo_sel:
        hueco = 0
        for v in reversed(h):
            if v >= 10: break
            hueco += 1
        return (f"💖 HUECO ACTIVO ({hueco} v)", "#e91e63", "white") if hueco >= 25 else (f"⏳ CARGANDO HUECO ({hueco}/25)", "#2d3436", "white")
    if "Cazador" in modo_sel:
        return ("🟢 ROSA RECIENTE", "#00ff41", "black") if h[-1] >= 10 else ("🔴 BUSCANDO ROSA", "#ff3131", "white")
    if "2x2" in modo_sel:
        if h[-1] < 2.0 and h[-2] < 2.0: return "🟢 ENTRADA 2x2 DETECTADA", "#00ff41", "black"
        return ("🟡 ESPERANDO BAJO", "#f1c40f", "black") if h[-1] < 2.0 else ("🔴 BUSCANDO PATRÓN 2x2", "#2d3436", "white")
    if "Conservadora" in modo_sel:
        return ("🟢 ENTRADA SEGURA (1.50x)", "#00ff41", "black") if h[-1] < 1.50 else ("🟡 ESPERANDO BAJO", "#f1c40f", "black")
    return "🟢 SISTEMA LISTO", "#00ff41", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, modo)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)

# RADAR
v_desde_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    v_desde_rosa += 1
st.markdown(f'<div class="radar-rosas">📡 RADAR ROSA: {v_desde_rosa} vuelos sin 10x+</div>', unsafe_allow_html=True)

# TIEMPOS
def get_minutos(hora_str):
    if hora_str == "---": return "?"
    try:
        ahora = datetime.now(pytz.timezone('America/Asuncion'))
        h_r = datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day)
        h_r = py_tz.localize(h_r)
        diff = ahora - h_r
        m = int(diff.total_seconds() / 60)
        return m if m >= 0 else (m + 1440)
    except: return "?"

st.markdown(f"""
    <div class="time-container">
        <div class="time-card"><div class="time-label">🌸 ÚLTIMA ROSA (10x)</div><div class="time-value">{st.session_state.hora_10x} hs</div><div class="time-elapsed">⏱️ {get_minutos(st.session_state.hora_10x)} min</div></div>
        <div class="time-card giant"><div class="time-label">👑 GIGANTE (100x+)</div><div class="time-value">{st.session_state.hora_100x} hs</div><div class="time-elapsed">⏱️ {get_minutos(st.session_state.hora_100x)} min</div></div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {apuesta_sugerida_base:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_v, col_m, col_c = st.columns([2, 1, 1])
with col_v: st.text_input("Resultado:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_m: st.number_input("Gs. Apostados:", value=float(apuesta_sugerida_base), step=1000.0, key="valor_apuesta_manual")
with col_c: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

st.write("### 📜 Historial")
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-40:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)

if st.button("⬅️ Deshacer"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.rerun()
