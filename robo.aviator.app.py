import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.5", page_icon="🦅", layout="wide")

# --- DISEÑO CSS BLACK EDITION CON SEMÁFORO ---
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
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.8rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 900; }
    
    /* ESTILO RELOJES */
    .time-box {
        background: #121212;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #FFFFFF;
        text-align: center;
    }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 1.1rem; margin-top: 5px; }
    
    /* SEMÁFORO DINÁMICO */
    .semaforo-box {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 4px solid rgba(255,255,255,0.1);
        margin-top: 10px;
        transition: 0.5s;
    }
    .semaforo-texto {
        font-size: 2rem;
        font-weight: 900;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin: 0;
    }
    
    .burbuja { min-width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; border: 2px solid rgba(255,255,255,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = now_str
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- LÓGICA DEL SEMÁFORO DE 3 ESTADOS ---
def obtener_semaforo():
    if len(st.session_state.historial) < 3:
        return "ESPERANDO DATOS", "#7f8c8d" # Gris
    
    hist = st.session_state.historial
    est = st.session_state.modo_sel
    
    # LÓGICA PARA ESTRATEGIAS DE 10X (Cazador y Hueco)
    if "10x" in est:
        rondas_sin_10x = 0
        distancia_ultimo_10x = 0
        for i, v in enumerate(reversed(hist)):
            if v >= 10:
                if rondas_sin_10x == 0: distancia_ultimo_10x = i
                break
            rondas_sin_10x += 1
            
        # VERDE: Si es Hueco (25+) o Cazadora detecta racha (distancia 2-10)
        if ("Hueco" in est and rondas_sin_10x >= 25) or ("Cazador" in est and 2 <= distancia_ultimo_10x <= 10):
            return "🟢 APUESTE AHORA", "#27ae60"
        # AMARILLO: Si se acerca al objetivo
        elif ("Hueco" in est and 18 <= rondas_sin_10x < 25) or ("Cazador" in est and distancia_ultimo_10x > 10):
            return "🟡 ANALIZANDO...", "#f1c40f"
        # ROJO: Riesgo alto
        else:
            return "🔴 NO ENTRAR", "#c0392b"

    # LÓGICA PARA 1.50x y 2x2
    else:
        if (hist[-1] >= 1.5): return "🟢 APUESTE AHORA", "#27ae60"
        return "🔴 NO ENTRAR", "#c0392b"

# --- FUNCIONES DE SOPORTE ---
def get_minutos(hora_str):
    if hora_str == "---" or not hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

def registrar_valor():
    if st.session_state.entrada_manual:
        try:
            v_val = float(str(st.session_state.entrada_manual).replace(',', '.'))
            st.session_state.historial.append(v_val)
            nueva_hora = datetime.now(py_tz).strftime("%H:%M")
            if v_val >= 100.0:
                st.session_state.h_100x_input = nueva_hora
                st.session_state.h_10x_input = nueva_hora
            elif v_val >= 10.0:
                st.session_state.h_10x_input = nueva_hora
            if st.session_state.check_apuesta:
                apuesta = float(st.session_state.valor_apuesta_manual)
                est = st.session_state.modo_sel
                target = 1.5 if "1.50x" in est else 2.0 if "2x2" in est else 10.0
                st.session_state.saldo_dinamico += (apuesta * (target - 1)) if v_val >= target else -apuesta
        except: pass
        st.session_state.entrada_manual = ""

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

st.markdown("<h1 style='text-align: center; color: white;'>🦅 AVIATOR ELITE v8.5</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card" style="border:2px solid #fff;"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card" style="border:2px solid #00ff41;"><p class="label-elite">Ganancia</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card" style="border:2px solid #ff3131;"><p class="label-elite">Pérdida</p><h2 class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: RELOJES
t1, t2 = st.columns(2)
with t1:
    st.markdown('<div class="time-box"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.text_input("H10", key="h_10x_input", label_visibility="collapsed")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="time-box"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.text_input("H100", key="h_100x_input", label_visibility="collapsed")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)

# --- FILA 3: EL NUEVO SEMÁFORO VISUAL ---
txt_sem, col_sem = obtener_semaforo()
st.markdown(f"""
    <div class="semaforo-box" style="background-color:{col_sem};">
        <p class="label-elite" style="margin-bottom:10px; font-size:1rem;">INDICADOR DE ENTRADA</p>
        <p class="semaforo-texto">{txt_sem}</p>
    </div>
    """, unsafe_allow_html=True)

# FILA 4: ENTRADAS
st.markdown("<br>", unsafe_allow_html=True)
col_in, col_ap, col_ck = st.columns([2, 1, 1])
with col_in: st.text_input("VALOR DEL VUELO (ENTER):", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("APUESTA Gs:", value=2000, step=1000, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-12:])])
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px; background:#111; border-radius:15px; margin-top:20px; border:1px solid #333;">{h_html}</div>', unsafe_allow_html=True)
