import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v6.8", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .metric-card { 
        background-color: #1e272e; 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        border: 2px solid #374151;
        margin-bottom: 10px;
    }
    .saldo-brillante { color: #FFFFFF !important; text-shadow: 0px 0px 10px rgba(255,255,255,0.3); margin: 0; font-size: 2.4rem; font-weight: 900; }
    .ganancia-viva { color: #00FF41 !important; text-shadow: 0px 0px 8px rgba(0,255,65,0.2); margin: 0; font-size: 2.4rem; font-weight: 900; }
    .perdida-viva { color: #FF3131 !important; margin: 0; font-size: 2.4rem; font-weight: 900; }
    
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; border: 2px solid rgba(255,255,255,0.1); }
    .radar-rosas { background-color: #2d3436; color: #fd79a8; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9rem; margin-top: -10px; font-weight: bold; border: 1px solid #fd79a8; }
    
    .time-container { display: flex; gap: 10px; margin: 10px 0px; }
    .time-card { flex: 1; background-color: #1e272e; padding: 10px; border-radius: 10px; text-align: center; border: 1px dashed #ef5777; }
    .time-card.giant { border-color: #f1c40f; }
    .time-label { font-size: 0.8rem; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
    .time-value { font-size: 1.2rem; font-weight: bold; color: #ef5777; }
    .time-card.giant .time-value { color: #f1c40f; }
    
    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 15px 5px; background: #00000050; border-radius: 10px; }
    .burbuja { min-width: 55px; height: 55px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; color: white; border: 2px solid #ffffff20; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'transacciones' not in st.session_state: st.session_state.transacciones = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

# --- FUNCIONES ---
def registrar_valor(valor_input=None):
    valor_raw = valor_input if valor_input is not None else st.session_state.entrada_manual
    impacto_saldo = 0.0
    if valor_raw:
        try:
            v_val = float(str(valor_raw).replace(',', '.'))
            st.session_state.historial.append(v_val)
            
            # Tiempos
            if v_val >= 100.0:
                st.session_state.hora_100x = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            elif v_val >= 10.0:
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            
            # Lógica de Saldo según Estrategia
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                
                # Definir objetivo según el selector
                if "1.50x" in st.session_state.modo_sel: target = 1.50
                elif "2x2" in st.session_state.modo_sel: target = 2.0
                else: target = 10.0 # Hueco o Rosa
                
                resultado_ronda = -ap_real
                if v_val >= target: 
                    resultado_ronda += (ap_real * target)
                
                st.session_state.saldo_dinamico += resultado_ronda
                impacto_saldo = resultado_ronda
            
            st.session_state.transacciones.append(impacto_saldo)
        except: pass
        st.session_state.entrada_manual = ""

def deshacer_ultimo():
    if st.session_state.historial:
        st.session_state.historial.pop()
        ultimo_impacto = st.session_state.transacciones.pop()
        st.session_state.saldo_dinamico -= ultimo_impacto
        st.rerun()

def get_minutos(hora_str):
    if hora_str == "---" or not hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        m = int((ahora - h_r).total_seconds() / 60)
        return m if m >= 0 else (m + 1440)
    except: return "?"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    # REINSTALADA LA ESTRATEGIA 1.50x
    st.session_state.modo_sel = st.selectbox("Estrategia:", [
        "Estrategia del Hueco 10x o +", 
        "Cazador de Rosas (10x)", 
        "Estrategia 2x2", 
        "Conservadora (1.50x)"
    ])
    
    st.markdown("---")
    st.session_state.hora_10x = st.text_input("Editar Hora 10x:", value=st.session_state.hora_10x)
    st.session_state.hora_100x = st.text_input("Editar Hora 100x:", value=st.session_state.hora_100x)
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- INTERFAZ ---
st.title("🦅 Aviator Elite PY v6.8")

ganancia_actual = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="metric-card" style="border-color:#FFFFFF;"><p>Saldo Actual</p><h2 class="saldo-brillante">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-card" style="border-color:#00FF41;"><p>Ganancia</p><h2 class="ganancia-viva">+{int(max(0, ganancia_actual)):,}</h2></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="metric-card" style="border-color:#FF3131;"><p>Pérdida</p><h2 class="perdida-viva">-{int(abs(min(0, ganancia_actual))):,}</h2></div>', unsafe_allow_html=True)

# Semáforo
hueco = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    hueco += 1
bg_sem = "#e91e63" if hueco >= 25 else "#2d3436"
st.markdown(f'<div class="semaforo" style="background-color:{bg_sem}; color:white;">{"💖 HUECO ACTIVO" if hueco >= 25 else f"⏳ CARGANDO ({hueco}/25)"}</div>', unsafe_allow_html=True)

# Relojes
st.markdown(f"""
    <div class="time-container">
        <div class="time-card"><div class="time-label">🌸 10x</div><div class="time-value">{st.session_state.hora_10x}</div><div class="time-elapsed">⏱️ {get_minutos(st.session_state.hora_10x)}m</div></div>
        <div class="time-card giant"><div class="time-label">👑 100x</div><div class="time-value">{st.session_state.hora_100x}</div><div class="time-elapsed">⏱️ {get_minutos(st.session_state.hora_100x)}m</div></div>
    </div>
""", unsafe_allow_html=True)

# Registro
st.write("### ⚡ Quick-Access")
c1, c2, c3, c4 = st.columns(4)
if c1.button("🟦 1.0x", use_container_width=True): registrar_valor(1.0)
if c2.button("🟦 1.5x", use_container_width=True): registrar_valor(1.5)
if c3.button("🟪 2.0x", use_container_width=True): registrar_valor(2.0)
if c4.button("🌸 10x", use_container_width=True): registrar_valor(10.0)

st.markdown("---")
col_txt, col_ap, col_ck = st.columns([2, 1, 1])
with col_txt: st.text_input("Valor Manual + Enter:", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("Apuesta Gs:", value=2000.0, step=1000.0, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

# Historial
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-15:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)

if st.button("⬅️ Borrar Último (Deshacer Saldo)"):
    deshacer_ultimo()
