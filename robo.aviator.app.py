import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v7.8", page_icon="🦅", layout="wide")

# --- DISEÑO CSS BLACK EDITION ---
st.markdown("""
    <style>
    /* Fondo Negro Puro */
    .stApp {
        background-color: #000000;
        background-attachment: fixed;
    }
    
    .main { 
        color: #ffffff; 
    }

    /* TARJETAS ESTILO PANEL */
    .elite-card { 
        background-color: #121212; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 10px;
        box-shadow: 0px 4px 20px rgba(255,255,255,0.05);
    }
    
    /* Bordes de Colores Sólidos */
    .card-border-white { border: 2px solid #FFFFFF; }
    .card-border-green { border: 2px solid #00ff41; }
    .card-border-red { border: 2px solid #ff3131; }

    /* TEXTOS Y ETIQUETAS */
    .label-elite {
        color: #FFFFFF !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.9rem;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    .valor-elite { 
        color: #FFFFFF !important; 
        font-size: 2.3rem;
        font-weight: 900;
        text-shadow: 0px 0px 10px rgba(255,255,255,0.3);
    }

    .valor-verde { color: #00ff41 !important; text-shadow: 0px 0px 10px rgba(0,255,65,0.4); }
    .valor-rojo { color: #ff3131 !important; text-shadow: 0px 0px 10px rgba(255,49,49,0.4); }

    /* RELOJES */
    .time-container { display: flex; gap: 10px; margin: 15px 0px; }
    .time-elite {
        flex: 1;
        background: #121212;
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #FFFFFF;
        text-align: center;
    }
    
    /* SEMAFORO CENTRAL */
    .semaforo-container {
        background: #121212;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #333;
        text-align: center;
    }

    /* BURBUJAS DE HISTORIAL */
    .burbuja { 
        min-width: 60px; height: 60px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; font-size: 16px; color: white; 
        border: 2px solid rgba(255,255,255,0.1); 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de estados
if 'historial' not in st.session_state: st.session_state.historial = []
if 'transacciones' not in st.session_state: st.session_state.transacciones = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

# --- LÓGICA ---
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
    st.header("🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Conservadora (1.50x)", "2x2", "Cazador (10x)", "Hueco 10x+"])
    if st.button("🔄 Reset Total"):
        st.session_state.clear()
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: white; letter-spacing: 2px;'>🦅 AVIATOR ELITE PY v7.8</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS
ganancia_actual = st.session_state.saldo_dinamico - saldo_in
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="elite-card card-border-white"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="elite-card card-border-green"><p class="label-elite">Ganancia</p><h2 class="valor-elite valor-verde">+{int(max(0, ganancia_actual)):,} Gs</h2></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="elite-card card-border-red"><p class="label-elite">Pérdida</p><h2 class="valor-elite valor-rojo">-{int(abs(min(0, ganancia_actual))):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: TIEMPOS Y SEMÁFORO
t1, t2, t3 = st.columns([1, 1.2, 1])

with t1:
    st.markdown(f"""
        <div class="time-elite">
            <div class="label-elite">🌸 ÚLTIMA 10X</div>
            <div class="valor-elite">{st.session_state.hora_10x}</div>
            <div style="color:#00ff41; font-weight:bold; font-size:1.1rem; margin-top:5px;">⏱️ {get_minutos(st.session_state.hora_10x)} min</div>
        </div>
    """, unsafe_allow_html=True)

with t2:
    hueco = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        hueco += 1
    texto_sem = "💖 HUECO ACTIVO" if hueco >= 25 else f"⏳ CARGANDO ({hueco}/25)"
    color_sem = "#e91e63" if hueco >= 25 else "#222"
    
    st.markdown(f"""
        <div class="semaforo-container">
            <div class="label-elite">SEMAFORO</div>
            <div style="background:{color_sem}; padding:15px; border-radius:10px; font-weight:900; font-size:1.4rem;">{texto_sem}</div>
        </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown(f"""
        <div class="time-elite">
            <div class="label-elite">✈️ GIGANTE 100X</div>
            <div class="valor-elite">{st.session_state.hora_100x}</div>
            <div style="color:#00ff41; font-weight:bold; font-size:1.1rem; margin-top:5px;">⏱️ {get_minutos(st.session_state.hora_100x)} min</div>
        </div>
    """, unsafe_allow_html=True)

# CONTROLES DE ENTRADA
st.markdown("---")
c_in, c_ap, c_ck = st.columns([2, 1, 1])
with c_in: st.text_input("VALOR MANUAL + ENTER:", key="entrada_manual", on_change=registrar_valor)
with c_ap: st.number_input("APUESTA Gs:", value=2000.0, step=1000.0, key="valor_apuesta_manual")
with c_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")

# HISTORIAL BURBUJAS
if st.session_state.historial:
    st.write("**HISTORIAL RECIENTE**")
    h_html = ""
    for val in reversed(st.session_state.historial[-15:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        h_html += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:10px; background:#0a0a0a; border-radius:10px;">{h_html}</div>', unsafe_allow_html=True)

if st.button("⬅️ BORRAR ÚLTIMO MOVIMIENTO"): deshacer_ultimo()
