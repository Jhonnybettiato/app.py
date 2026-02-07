import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.0", page_icon="🦅", layout="wide")

# --- DISEÑO CSS MASTER ELITE (Fondo Dinámico + Glassmorphism) ---
st.markdown("""
    <style>
    /* Aplicar el fondo de líneas rojas y doradas */
    .stApp {
        background-image: url("https://img.freepik.com/vector-gratis/fondo-abstracto-formas-geometricas-negras-rojas_1017-31718.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Overlay para oscurecer el fondo y mejorar legibilidad */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.82);
        z-index: -1;
    }

    /* TARJETAS ESTILO PANEL (Como en tu imagen) */
    .elite-card { 
        background: rgba(25, 25, 25, 0.9); 
        padding: 22px; 
        border-radius: 18px; 
        text-align: center; 
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.7);
    }
    
    .border-white { border: 2px solid #FFFFFF !important; }
    .border-green { border: 2px solid #00ff41 !important; }
    .border-red { border: 2px solid #ff3131 !important; }

    /* TEXTOS Y BRILLOS NEÓN */
    .label-elite {
        color: #FFFFFF !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }
    
    .valor-neon { 
        color: #FFFFFF !important; 
        font-size: 2.6rem;
        font-weight: 900;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.6), 0px 0px 5px rgba(255,255,255,1);
    }

    .valor-verde { color: #00ff41 !important; text-shadow: 0px 0px 15px rgba(0,255,65,0.6); }
    .valor-rojo { color: #ff3131 !important; text-shadow: 0px 0px 15px rgba(255,49,49,0.6); }

    /* RELOJES */
    .time-box {
        background: rgba(15, 15, 15, 0.95);
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #FFFFFF;
        text-align: center;
    }
    
    .minutos-verde { color: #00ff41; font-weight: bold; font-size: 1.2rem; margin-top: 5px; }

    /* BURBUJAS */
    .burbuja { 
        min-width: 60px; height: 60px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; font-size: 16px; color: white; 
        border: 2px solid rgba(255,255,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Sesión
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
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 15px rgba(255,49,49,0.5);'>🦅 Aviator Elite PY v8.0</h1>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Conservadora (1.50x)", "2x2", "Cazador 10x"])
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# FILA 1: MÉTRICAS
ganancia_actual = st.session_state.saldo_dinamico - saldo_in
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="elite-card border-white"><p class="label-elite">Saldo Actual</p><h2 class="valor-neon">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="elite-card border-green"><p class="label-elite">Ganancia</p><h2 class="valor-neon valor-verde">+{int(max(0, ganancia_actual)):,} Gs</h2></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="elite-card border-red"><p class="label-elite">Pérdida</p><h2 class="valor-neon valor-rojo">-{int(abs(min(0, ganancia_actual))):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: TIEMPOS Y SEMÁFORO
t1, t2, t3 = st.columns([1, 1.2, 1])
with t1:
    st.markdown(f'<div class="time-box"><p class="label-elite">🌸 ÚLTIMA 10X</p><h2 class="valor-neon">{st.session_state.hora_10x}</h2><p class="minutos-verde">⏱️ {get_minutos(st.session_state.hora_10x)} min</p></div>', unsafe_allow_html=True)

with t2:
    hueco = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        hueco += 1
    bg_sem = "#e91e63" if hueco >= 25 else "#2d3436"
    st.markdown(f'<div class="elite-card" style="background:{bg_sem};"><p class="label-elite">SEMAFORO</p><h3 style="margin:0; font-weight:900;">{"💖 HUECO ACTIVO" if hueco >= 25 else f"⏳ CARGANDO ({hueco}/25)"}</h3></div>', unsafe_allow_html=True)

with t3:
    st.markdown(f'<div class="time-box"><p class="label-elite">✈️ GIGANTE 100X</p><h2 class="valor-neon">{st.session_state.hora_100x}</h2><p class="minutos-verde">⏱️ {get_minutos(st.session_state.hora_100x)} min</p></div>', unsafe_allow_html=True)

# CONTROLES
st.markdown("---")
col_in, col_ap, col_ck = st.columns([2, 1, 1])
with col_in: st.text_input("VALOR (ENTER):", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("APUESTA:", value=2000, step=1000, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    h_html = ""
    for val in reversed(st.session_state.historial[-12:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        h_html += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px; background:rgba(0,0,0,0.5); border-radius:15px;">{h_html}</div>', unsafe_allow_html=True)
