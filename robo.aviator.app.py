import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.3", page_icon="🦅", layout="wide")

# --- DISEÑO CSS BLACK EDITION ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    .card-border-white { border: 2px solid #FFFFFF; }
    .card-border-green { border: 2px solid #00ff41; }
    .card-border-red { border: 2px solid #ff3131; }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.8rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 900; }
    .valor-verde { color: #00ff41 !important; }
    .valor-rojo { color: #ff3131 !important; }
    
    /* ESTILO RELOJES */
    .time-box {
        background: #121212;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #FFFFFF;
        text-align: center;
    }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 1rem; margin-top: 5px; }
    
    .burbuja { min-width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; border: 2px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Sesión
py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'hora_10x' not in st.session_state: st.session_state.hora_10x = now_str
if 'hora_100x' not in st.session_state: st.session_state.hora_100x = "---"

# --- FUNCIONES DE APOYO ---
def get_minutos(hora_str):
    if hora_str == "---" or not hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        m = int((ahora - h_r).total_seconds() / 60)
        return m if m >= 0 else (m + 1440)
    except: return "?"

def registrar_valor():
    if st.session_state.entrada_manual:
        try:
            v_val = float(str(st.session_state.entrada_manual).replace(',', '.'))
            st.session_state.historial.append(v_val)
            
            # Actualizar Relojes
            if v_val >= 100.0:
                st.session_state.hora_100x = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            elif v_val >= 10.0:
                st.session_state.hora_10x = datetime.now(py_tz).strftime("%H:%M")
            
            # Lógica de Saldo
            if st.session_state.check_apuesta:
                apuesta = float(st.session_state.valor_apuesta_manual)
                est = st.session_state.modo_sel
                target = 1.5 if "1.50x" in est else 2.0 if "2x2" in est else 10.0
                impacto = (apuesta * (target - 1)) if v_val >= target else -apuesta
                st.session_state.saldo_dinamico += impacto
        except: pass
        st.session_state.entrada_manual = ""

def obtener_analisis():
    if len(st.session_state.historial) < 3: return "ESPERANDO DATOS...", "#222"
    hist = st.session_state.historial
    est = st.session_state.modo_sel
    
    if "Cazador" in est:
        distancia = 0
        encontrado = False
        for i, v in enumerate(reversed(hist)):
            if v >= 10: 
                distancia = i
                encontrado = True
                break
        if encontrado and 2 <= distancia <= 10: return "🔥 CAZADORA: RACHA ACTIVA", "#e67e22"
        return "⏳ CAZADORA: BUSCANDO CICLO", "#121212"
    
    elif "Hueco" in est:
        rondas_sin_rosa = 0
        for v in reversed(hist):
            if v >= 10: break
            rondas_sin_rosa += 1
        if rondas_sin_rosa >= 25: return f"💖 HUECO ACTIVO ({rondas_sin_rosa})", "#e91e63"
        return f"⏳ ESPERANDO: {rondas_sin_rosa}/25", "#121212"
    
    return "ANALIZANDO MERCADO...", "#121212"

# --- INTERFAZ ---
with st.sidebar:
    st.header("🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Cazador (10x)", "Hueco 10x+", "Conservadora (1.50x)", "2x2"])
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

st.markdown("<h1 style='text-align: center; color: white;'>🦅 AVIATOR ELITE v8.3</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS FINANCIERAS
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card card-border-white"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card card-border-green"><p class="label-elite">Ganancia</p><h2 class="valor-elite valor-verde">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card card-border-red"><p class="label-elite">Pérdida</p><h2 class="valor-elite valor-rojo">{int(min(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: RELOJES (🌸 10x y ✈️ 100x)
t1, t2 = st.columns(2)
with t1:
    st.markdown(f"""<div class="time-box"><p class="label-elite">🌸 ÚLTIMA 10X</p><h2 class="valor-elite">{st.session_state.hora_10x}</h2><p class="minutos-meta">⏱️ {get_minutos(st.session_state.hora_10x)} min</p></div>""", unsafe_allow_html=True)
with t2:
    st.markdown(f"""<div class="time-box"><p class="label-elite">✈️ GIGANTE 100X</p><h2 class="valor-elite">{st.session_state.hora_100x}</h2><p class="minutos-meta">⏱️ {get_minutos(st.session_state.hora_100x)} min</p></div>""", unsafe_allow_html=True)

# FILA 3: SEMÁFORO DE ESTRATEGIA
txt_an, col_an = obtener_analisis()
st.markdown(f"""<div style="background:{col_an}; padding:20px; border-radius:15px; text-align:center; border:1px solid #444; margin-top:10px;"><p class="label-elite">SEMAFORO: {st.session_state.modo_sel}</p><h2 style="color:white; margin:0;">{txt_an}</h2></div>""", unsafe_allow_html=True)

# FILA 4: ENTRADAS
st.markdown("<br>", unsafe_allow_html=True)
col_in, col_ap, col_ck = st.columns([2, 1, 1])
with col_in: st.text_input("VALOR DEL VUELO:", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("APUESTA Gs:", value=2000, step=1000, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-12:])])
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px; background:#0a0a0a; border-radius:15px; margin-top:20px;">{h_html}</div>', unsafe_allow_html=True)
