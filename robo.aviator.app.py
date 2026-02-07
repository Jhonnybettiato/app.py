import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v7.3", page_icon="🦅", layout="wide")

# --- DISEÑO CSS PREMIUM WHITE ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* VALORES EN BLANCO PURO */
    .valor-blanco { 
        color: #FFFFFF !important; 
        text-shadow: 0px 0px 12px rgba(255,255,255,0.4);
        margin: 0; 
        font-weight: 900; 
    }
    
    /* TARJETAS DE MÉTRICAS */
    .metric-card { 
        background-color: #1e272e; 
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        border: 1px solid #374151;
        margin-bottom: 10px;
    }
    /* Resalte especial para el Saldo Actual */
    .card-saldo { border: 2px solid #FFFFFF !important; box-shadow: 0px 0px 15px rgba(255,255,255,0.1); }
    
    .metric-card h2 { font-size: 2.6rem; }
    .metric-card p { margin: 0; color: #bdc3c7; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
    
    /* RELOJES */
    .time-container { display: flex; gap: 10px; margin: 10px 0px; }
    .time-card { 
        flex: 1; 
        background-color: #1e272e; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        border: 1px solid #ffffff40; 
    }
    .val-tiempo { font-size: 2rem; }
    .time-elapsed { font-size: 1rem; color: #00ff41; font-weight: bold; margin-top: 5px; }

    /* OTROS */
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; border: 1px solid rgba(255,255,255,0.1); }
    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 15px 5px; background: #00000050; border-radius: 10px; }
    .burbuja { min-width: 55px; height: 55px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; color: white; border: 2px solid #ffffff20; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
if 'historial' not in st.session_state: st.session_state.historial = []
if 'transacciones' not in st.session_state: st.session_state.transacciones = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

# --- LÓGICA DE REGISTRO ---
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
            
            # Gestión de Saldo
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                modo = st.session_state.modo_sel
                if "1.50x" in modo: target = 1.50
                elif "2x2" in modo: target = 2.0
                else: target = 10.0
                
                res = -ap_real
                if v_val >= target: res += (ap_real * target)
                st.session_state.saldo_dinamico += res
                impacto_saldo = res
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

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    st.session_state.modo_sel = st.selectbox("Estrategia activa:", [
        "Conservadora (1.50x)", 
        "Estrategia 2x2", 
        "Cazador de Rosas (10x)", 
        "Estrategia del Hueco 10x o +"
    ])
    
    st.markdown("---")
    st.session_state.hora_10x = st.text_input("Editar Hora 10x:", value=st.session_state.hora_10x)
    st.session_state.hora_100x = st.text_input("Editar Hora 100x:", value=st.session_state.hora_100x)
    
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- PANEL PRINCIPAL ---
st.title("🦅 Aviator Elite PY v7.3")

ganancia_actual = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: 
    st.markdown(f'<div class="metric-card card-saldo"><p>Saldo Actual</p><h2 class="valor-blanco">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
with m2: 
    st.markdown(f'<div class="metric-card"><p>Ganancia</p><h2 class="valor-blanco">+{int(max(0, ganancia_actual)):,}</h2></div>', unsafe_allow_html=True)
with m3: 
    st.markdown(f'<div class="metric-card"><p>Pérdida</p><h2 class="valor-blanco">-{int(abs(min(0, ganancia_actual))):,}</h2></div>', unsafe_allow_html=True)

# Semáforo de Hueco
hueco = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    hueco += 1
bg_sem = "#e91e63" if hueco >= 25 else "#2d3436"
st.markdown(f'<div class="semaforo" style="background-color:{bg_sem}; color:white;">{"💖 HUECO ACTIVO" if hueco >= 25 else f"⏳ CARGANDO ({hueco}/25)"}</div>', unsafe_allow_html=True)

# Relojes en Blanco
st.markdown(f"""
    <div class="time-container">
        <div class="time-card">
            <div class="time-label">🌸 ÚLTIMA 10X</div>
            <div class="valor-blanco val-tiempo">{st.session_state.hora_10x}</div>
            <div class="time-elapsed">⏱️ {get_minutos(st.session_state.hora_10x)} min</div>
        </div>
        <div class="time-card">
            <div class="time-label">👑 GIGANTE 100X</div>
            <div class="valor-blanco val-tiempo">{st.session_state.hora_100x}</div>
            <div class="time-elapsed">⏱️ {get_minutos(st.session_state.hora_100x)} min</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Registro y Controles
st.write("### ⚡ Quick-Access")
c1, c2, c3, c4 = st.columns(4)
if c1.button("🟦 1.0x", use_container_width=True): registrar_valor(1.0)
if c2.button("🟦 1.5x", use_container_width=True): registrar_valor(1.5)
if c3.button("🟪 2.0x", use_container_width=True): registrar_valor(2.0)
if c4.button("🌸 10x", use_container_width=True): registrar_valor(10.0)

st.markdown("---")
col_txt, col_ap, col_ck = st.columns([2, 1, 1])
with col_txt: st.text_input("Valor Manual + Enter:", key="entrada_manual", on_change=registrar_valor)
with col_ap:
