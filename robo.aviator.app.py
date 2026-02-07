import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v7.8", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ELITE ULTRA (Simulando la imagen) ---
st.markdown("""
    <style>
    /* Fondo oscuro profundo */
    .stApp {
        background-color: #050505;
        color: #ffffff;
    }
    
    /* TARJETAS ESTILO PANEL DE CONTROL */
    .elite-card { 
        background-color: #1a1a1a; 
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 15px;
        box-shadow: 0px 5px 20px rgba(0,0,0,0.8);
    }
    
    /* Bordes de colores según la imagen */
    .border-white { border: 2px solid #FFFFFF !important; }
    .border-green { border: 2px solid #00ff41 !important; }
    .border-red { border: 2px solid #ff3131 !important; }

    /* TEXTOS Y BRILLOS */
    .titulo-card {
        color: #FFFFFF !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 1rem;
        margin-bottom: 12px;
        letter-spacing: 1px;
    }
    
    .valor-neon { 
        color: #FFFFFF !important; 
        font-size: 2.5rem;
        font-weight: 900;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.7);
    }

    .valor-verde { color: #00ff41 !important; text-shadow: 0px 0px 15px rgba(0,255,65,0.7); }
    .valor-rojo { color: #ff3131 !important; text-shadow: 0px 0px 15px rgba(255,49,49,0.7); }

    /* RELOJES Y TIEMPOS */
    .time-box {
        background: #111111;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FFFFFF;
        text-align: center;
        margin-top: 10px;
    }
    
    .minutos-verde { color: #00ff41; font-weight: bold; font-size: 1.2rem; margin-top: 10px; }

    /* SEMAFORO Y BOTONES */
    .semaforo-elite {
        background: #1a1a1a;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #444;
        text-align: center;
    }
    
    .burbuja { 
        min-width: 60px; height: 60px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: bold; font-size: 16px; color: white; 
        border: 2px solid rgba(255,255,255,0.2); 
    }
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
            if v_val >= 100.0:
                st.session_state.hora_100x = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            elif v_val >= 10.0:
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                modo = st.session_state.modo_sel
                target = 1.50 if "1.50x" in modo else 2.0 if "2x2" in modo else 10.0
                res = -ap_real
                if v_val >= target: res += (ap_real * target)
                st.session_state.saldo_dinamico += res
                impacto_saldo = res
            st.session_state.transacciones.append(impacto_saldo)
        except: pass
        st.session_state.entrada_manual = ""

def get_minutos(hora_str):
    if hora_str == "---" or not hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        m = int((ahora - h_r).total_seconds() / 60)
        return m if m >= 0 else (m + 1440)
    except: return "?"

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: white;'>🦅 Aviator Elite PY v7.8</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS PRINCIPALES
saldo_inicial_gs = 50000 # Valor base para el cálculo inicial
if st.session_state.primer_inicio:
    st.session_state.saldo_dinamico = float(saldo_inicial_gs)
    st.session_state.primer_inicio = False

ganancia_neta = st.session_state.saldo_dinamico - saldo_inicial_gs
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="elite-card border-white"><p class="titulo-card">Saldo Actual</p><h2 class="valor-neon">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="elite-card border-green"><p class="titulo-card">Ganancia</p><h2 class="valor-neon valor-verde">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="elite-card border-red"><p class="titulo-card">Pérdida</p><h2 class="valor-neon valor-rojo">-{int(abs(min(0, ganancia_neta))):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: TIEMPOS (Con el Avión ✈️)
t1, t2, t3 = st.columns([1, 1, 1])

with t1:
    st.markdown(f'<div class="time-box"><p class="titulo-card">🌸 ÚLTIMA 10X</p><h2 class="valor-neon">{st.session_state.hora_10x}</h2><p class="minutos-verde">⏱️ {get_minutos(st.session_state.hora_10x)} min</p></div>', unsafe_allow_html=True)

with t2:
    hueco = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        hueco += 1
    color_s = "#e91e63" if hueco >= 25 else "#333"
    st.markdown(f'<div class="semaforo-elite"><p class="titulo-card">SEMAFORO</p><div style="background:{color_s}; padding:15px; border-radius:10px; font-weight:900;">{"💖 HUECO ACTIVO" if hueco >= 25 else f"⏳ {hueco}/25"}</div></div>', unsafe_allow_html=True)

with t3:
    st.markdown(f'<div class="time-box"><p class="titulo-card">✈️ GIGANTE 100X</p><h2 class="valor-neon">{st.session_state.hora_100x}</h2><p class="minutos-verde">⏱️ {get_minutos(st.session_state.hora_100x)} min</p></div>', unsafe_allow_html=True)

# ENTRADA DE DATOS
st.markdown("---")
with st.container():
    col_a, col_b, col_c = st.columns([2, 1, 1])
    col_a.text_input("VALOR DEL VUELO (ENTER):", key="entrada_manual", on_change=registrar_valor)
    col_b.number_input("APUESTA Gs:", value=2000, step=1000, key="valor_apuesta_manual")
    col_c.write("##"); col_c.checkbox("¿APOSTÉ?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    h_html = ""
    for val in reversed(st.session_state.historial[-15:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        h_html += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px;">{h_html}</div>', unsafe_allow_html=True)

# SIDEBAR PARA AJUSTES
with st.sidebar:
    st.header("⚙️ Ajustes")
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Conservadora (1.50x)", "2x2", "Cazador (10x)"])
    if st.button("🔄 Reset Total"):
        st.session_state.clear()
        st.rerun()
