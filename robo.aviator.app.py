import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.0", page_icon="🦅", layout="wide")

# --- DISEÑO CSS MASTER ELITE (Fondo Dinámico + Glassmorphism) ---
st.markdown("""
    <style>
    /* Aplicar el fondo de la imagen con overlay oscuro */
    .stApp {
        background-image: url("https://img.freepik.com/vector-gratis/fondo-abstracto-formas-geometricas-negras-rojas_1017-31718.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Filtro para oscurecer el fondo y que resalten las tarjetas */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.75); /* Ajusta este valor para más o menos oscuridad */
        z-index: -1;
    }

    /* TARJETAS ESTILO PANEL (Como en tu imagen) */
    .elite-card { 
        background: rgba(20, 20, 20, 0.85); 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 10px;
        backdrop-filter: blur(5px); /* Efecto de cristal */
        box-shadow: 0px 8px 16px rgba(0,0,0,0.6);
    }
    
    .border-white { border: 2px solid #FFFFFF !important; }
    .border-green { border: 2px solid #00ff41 !important; }
    .border-red { border: 2px solid #ff3131 !important; }

    /* TEXTOS */
    .label-elite {
        color: #FFFFFF !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    
    .valor-neon { 
        color: #FFFFFF !important; 
        font-size: 2.4rem;
        font-weight: 900;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.4);
    }

    .valor-verde { color: #00ff41 !important; }
    .valor-rojo { color: #ff3131 !important; }

    /* RELOJES */
    .time-box {
        background: rgba(30, 30, 30, 0.9);
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #FFFFFF;
        text-align: center;
    }
    
    .minutos-verde { color: #00ff41; font-weight: bold; font-size: 1.1rem; }

    /* BOTONES DE REGISTRO RÁPIDO */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Lógica de Sesión
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 50000.0

py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

def registrar_vuelo(v):
    # Lógica simplificada para el ejemplo
    st.session_state.historial.append(v)
    if v >= 100: st.session_state.hora_100x = datetime.now(py_tz).strftime("%H:%M")
    if v >= 10: st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")

def get_min(h):
    if h == "---": return "?"
    try:
        ahora = datetime.now(py_tz)
        h_dt = py_tz.localize(datetime.strptime(h, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        return int((ahora - h_dt).total_seconds() / 60)
    except: return "?"

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: white;'>🦅 Aviator Elite PY v8.0</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS (Igual a la imagen)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="elite-card border-white"><p class="label-elite">Saldo Actual</p><h2 class="valor-neon">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="elite-card border-green"><p class="label-elite">Ganancia</p><h2 class="valor-neon valor-verde">+0 Gs</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="elite-card border-red"><p class="label-elite">Pérdida</p><h2 class="valor-neon valor-rojo">-0 Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: TIEMPOS Y SEMÁFORO
t1, t2, t3 = st.columns([1, 1.2, 1])
with t1:
    st.markdown(f'<div class="time-box"><p class="label-elite">🌸 ÚLTIMA 10X</p><h2 class="valor-neon">{st.session_state.hora_10x}</h2><p class="minutos-verde">⏱️ {get_min(st.session_state.hora_10x)} min</p></div>', unsafe_allow_html=True)

with t2:
    st.markdown(f'<div class="elite-card" style="background: rgba(40,40,40,0.9); border: 1px solid #555;"><p class="label-elite">SEMAFORO</p><div style="background:#222; padding:10px; border-radius:10px; font-weight:900;">⏳ CARGANDO (0/25)</div></div>', unsafe_allow_html=True)

with t3:
    st.markdown(f'<div class="time-box"><p class="label-elite">✈️ GIGANTE 100X</p><h2 class="valor-neon">{st.session_state.hora_100x}</h2><p class="minutos-verde">⏱️ {get_min(st.session_state.hora_100x)} min</p></div>', unsafe_allow_html=True)

# REGISTRO RÁPIDO Y ENTRADA
st.markdown("---")
col_in, col_ap = st.columns([3, 1])
with col_in:
    st.write("### ⚡ Registro Rápido")
    r1, r2, r3, r4 = st.columns(4)
    if r1.button("🟦 1.0x", use_container_width=True): registrar_vuelo(1.0)
    if r2.button("🟪 2.0x", use_container_width=True): registrar_vuelo(2.0)
    if r3.button("🌸 10x", use_container_width=True): registrar_vuelo(10.0)
    if r4.button("✈️ 100x", use_container_width=True): registrar_vuelo(100.0)
