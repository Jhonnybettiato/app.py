import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.2", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 15px; border-radius: 15px; 
        text-align: center; margin-bottom: 10px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.8rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 900; }
    .minutos-meta { color: #00ff41; font-weight: bold; font-size: 1.1rem; margin-top: 5px; }
    .semaforo-box { padding: 30px; border-radius: 20px; text-align: center; margin-top: 10px; }
    .semaforo-texto { font-size: 2rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { 
        min-width: 75px; height: 60px; border-radius: 30px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; padding: 0 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = now_str
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- FUNCIONES DE APOYO ---
def contar_rondas_desde_rosa():
    count = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        count += 1
    return count

def obtener_semaforo():
    if len(st.session_state.historial) < 3: 
        return "ESPERANDO DATOS...", "#333"
    
    hist = st.session_state.historial
    est = st.session_state.modo_sel
    sin_rosa = contar_rondas_desde_rosa()
    
    # 1. ESTRATEGIA: HUECO 10X+
    if "Hueco" in est:
        if sin_rosa >= 25: return "🟢 HUECO ACTIVO", "#27ae60"
        if sin_rosa >= 18: return "🟡 ANALIZANDO...", "#f1c40f"
        return "🔴 NO ENTRAR", "#c0392b"
    
    # 2. ESTRATEGIA: CAZADOR (RACHAS)
    elif "Cazador" in est:
        # Busca a qué distancia está la última rosa
        distancia = -1
        for i, v in enumerate(reversed(hist)):
            if v >= 10:
                distancia = i
                break
        if 2 <= distancia <= 10: return "🟢 RACHA DETECTADA", "#27ae60"
        return "🔴 ESPERANDO CICLO", "#c0392b"

    # 3. ESTRATEGIA: ESPEJO GEMELO
    elif "Espejo" in est:
        if len(hist) < 4: return "FALTAN DATOS", "#333"
        # Patrón: Rosa (H-3 o H-2) + Azul + Rosa cercana
        ultimos_5 = hist[-5:]
        rosas = sum(1 for v in ultimos_5 if v >= 10)
        if rosas >= 2: return "🟢 ESPEJO ACTIVO", "#8e44ad"
        return "🔴 BUSCANDO PAR", "#c0392b"

    # 4. ESTRATEGIAS CONSERVADORAS (1.50x y 2x2)
    else:
        target = 1.5 if "1.50x" in est else 2.0
        # Si la última fue buena, hay probabilidad de racha corta
        if hist[-1] >= target: return "🟢 APUESTE (RACHA)", "#27ae60"
        return "🔴 NO ENTRAR", "#c0392b"

# --- REGISTRO Y ACCIONES ---
def registrar_valor():
    if st.session_state.entrada_manual:
        try:
            v_val = float(str(st.session_state.entrada_manual).replace(',', '.'))
            impacto = 0.0
            if st.session_state.check_apuesta:
                ap = float(st.session_state.valor_apuesta_manual)
                est = st.session_state.modo_sel
                # Definir meta según estrategia para contabilidad
                t = 10.0 if any(x in est for x in ["Cazador", "Hueco", "Espejo"]) else (1.5 if "1.5" in est else 2.0)
                impacto = (ap * (t - 1)) if v_val >= t else -float(ap)
            
            st.session_state.historial.append(v_val)
            st.session_state.registro_saldos.append(impacto)
            st.session_state.saldo_dinamico += impacto
            
            nueva_h = datetime.now(py_tz).strftime("%H:%M")
            if v_val >= 100: 
                st.session_state.h_100x_input = nueva_h
                st.session_state.h_10x_input = nueva_h
            elif v_val >= 10: 
                st.session_state.h_10x_input = nueva_h
        except: pass
        st.session_state.entrada_manual = ""

def deshacer_accion():
    if st.session_state.historial:
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.session_state.historial.pop()

def get_minutos(hora_str):
    if "---" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

# --- INTERFAZ ---
with st.sidebar:
    st.header("🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Espejo Gemelo (10x)", "Cazador (10x)", "Hueco 10x+", "Conservadora (1.50x)", "2x2"])
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear(); st.rerun()

st.markdown("<h1 style='text-align: center; color: white;'>🦅 AVIATOR ELITE v9.2</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card" style="border:2px solid #fff;"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card" style="border:2px solid #00ff41;"><p class="label-elite">Ganancia</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card" style="border:2px solid #ff3131;"><p class="label-elite">Pérdida</p><h2 class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: RELOJES Y CONTADOR
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.text_input("H10", key="h_10x_input", label_visibility="collapsed")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.text_input("H100", key="h_100x_input", label_visibility="collapsed")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)
with t3:
    r_count = contar_rondas_desde_rosa()
    st.markdown(f'<div class="elite-card" style="border:1px solid #e91e63;"><p class="label-elite">📊 RONDAS SIN ROSA</p><h2 class="valor-elite" style="color:#e91e63!important;">{r_count}</h2></div>', unsafe_allow_html=True)

# FILA 3: SEMÁFORO (CORREGIDO)
txt_s, col_s = obtener_semaforo()
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s}; border:4px solid rgba(255,255,255,0.2);"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# FILA 4: ENTRADAS
st.markdown("<br>", unsafe_allow_html=True)
col_in, col_ap, col_ck, col_undo = st.columns([2, 1, 1, 1])
with col_in: st.text_input("VUELO:", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("APUESTA:", value=2000, step=1000, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")
with col_undo: st.write("##"); st.button("🔙 DESHACER", on_click=deshacer_accion)

# HISTORIAL
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-10:])])
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px; background:#111; border-radius:15px; margin-top:20px;">{h_html}</div>', unsafe_allow_html=True)
