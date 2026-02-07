import streamlit as st
from datetime import datetime
import pytz
import re

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v9.2.8", page_icon="🦅", layout="wide")

# --- DISEÑO CSS (Tu diseño original) ---
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
    
    .rosa-val-txt { color: #e91e63; font-weight: 900; font-size: 1.1rem; }
    
    .burbuja { 
        min-width: 65px; height: 60px; border-radius: 30px; 
        display: flex; align-items: center; justify-content: center; 
        font-weight: 900; color: white; padding: 0 10px; margin-right: 5px;
    }
    /* Estilo para que las etiquetas del formulario se vean blancas */
    div[data-testid="stForm"] label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'historial_rosas' not in st.session_state: st.session_state.historial_rosas = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = "00:00"
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- FUNCIONES ---
def contar_rondas_desde_rosa():
    count = 0
    for v in reversed(st.session_state.historial):
        if v >= 10: break
        count += 1
    return count

def obtener_semaforo():
    if len(st.session_state.historial) < 2: return "ESPERANDO DATOS...", "#333"
    est = st.session_state.modo_sel
    hist = st.session_state.historial
    sin_rosa = contar_rondas_desde_rosa()
    if "Hueco" in est:
        if sin_rosa >= 25: return "🟢 HUECO ACTIVO", "#27ae60"
        if sin_rosa >= 18: return "🟡 ANALIZANDO...", "#f1c40f"
        return "🔴 NO ENTRAR", "#c0392b"
    elif "Cazador" in est:
        if 2 <= sin_rosa <= 10: return "🟢 ZONA DE CAZA", "#27ae60"
        return "🔴 ESPERAR SEÑAL", "#c0392b"
    elif "Espejo" in est:
        if hist[-1] >= 10: return "🟢 POSIBLE ESPEJO", "#8e44ad"
        return "🔴 ESPERANDO ROSA", "#c0392b"
    elif "Conservadora" in est:
        if hist[-1] < 2.0: return "🟢 ENTRAR (RECUPERACIÓN)", "#27ae60"
        return "🔴 ESPERAR AZUL", "#c0392b"
    return "SISTEMA LISTO", "#3498db"

def get_minutos(hora_str):
    if "---" in hora_str or ":" not in hora_str: return "?"
    try:
        ahora = datetime.now(py_tz)
        h_r = py_tz.localize(datetime.strptime(hora_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        diff = int((ahora - h_r).total_seconds() / 60)
        return diff if diff >= 0 else (diff + 1440)
    except: return "?"

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Hueco 10x+", "Cazador (10x)", "Espejo Gemelo (10x)", "Conservadora (1.50x)"])
    if st.button("🔄 Reiniciar App"): st.session_state.clear(); st.rerun()

# ---------------------------------------------------------
# LÓGICA DE PROCESAMIENTO (OCULTA PERO PRIMERO QUE TODO)
# ---------------------------------------------------------
# Creamos un formulario fantasma o capturamos los datos antes de mostrar la UI
# para que el cambio sea instantáneo al presionar el botón.

st.title("🦅 AVIATOR ELITE v9.2.8")

# --- PANEL DE REGISTRO (Ubicado arriba para respuesta inmediata) ---
with st.form("panel_registro", clear_on_submit=True):
    col_in, col_ap, col_ck, col_btn = st.columns([2, 1, 1, 1])
    with col_in: valor_raw = st.text_input("VUELO:", placeholder="Ej: 12.50")
    with col_ap: apuesta_manual = st.number_input("APUESTA:", value=2000, step=1000)
    with col_ck: st.write("##"); check_apuesta = st.checkbox("¿APOSTÉ?")
    with col_btn: st.write("##"); submit = st.form_submit_button("REGISTRAR")

    if submit and valor_raw:
        try:
            clean_val = re.sub(r'[^0-9.,]', '', valor_raw).replace(',', '.')
            v_val = float(clean_val)
            impacto = 0.0
            if check_apuesta:
                t = 10.0 if "10x" in st.session_state.modo_sel else 1.5 if "1.50x" in st.session_state.modo_sel else 2.0
                impacto = (apuesta_manual * (t - 1)) if v_val >= t else -float(apuesta_manual)
            
            st.session_state.historial.append(v_val)
            st.session_state.registro_saldos.append(impacto)
            st.session_state.saldo_dinamico += impacto
            
            if v_val >= 10:
                ahora = datetime.now(py_tz).strftime("%H:%M")
                st.session_state.h_10x_input = ahora
                st.session_state.historial_rosas.append({"valor": v_val, "hora": ahora})
                if v_val >= 100: st.session_state.h_100x_input = ahora
            st.rerun() # Esto hace que la actualización sea instantánea
        except: pass

# --- FILA 1: MÉTRICAS (Ya actualizadas por el bloque anterior) ---
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card" style="border:2px solid #fff;"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card" style="border:2px solid #00ff41;"><p class="label-elite">Ganancia</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card" style="border:2px solid #ff3131;"><p class="label-elite">Pérdida</p><h2 class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)

# --- FILA 2: RELOJES ---
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown('<div class="elite-card"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.session_state.h_10x_input = st.text_input("H10", value=st.session_state.h_10x_input, label_visibility="collapsed", key="h10_fix")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_10x_input)} min</p></div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.session_state.h_100x_input = st.text_input("H100", value=st.session_state.h_100x_input, label_visibility="collapsed", key="h100_fix")
    st.markdown(f'<p class="minutos-meta">⏱️ {get_minutos(st.session_state.h_100x_input)} min</p></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="elite-card" style="border:1px solid #e91e63;"><p class="label-elite">📊 RONDAS SIN ROSA</p><h2 class="valor-elite" style="color:#e91e63!important;">{contar_rondas_desde_rosa()}</h2></div>', unsafe_allow_html=True)

# --- CAJA DE HISTORIAL ROSA ---
with st.expander("📊 HISTORIAL DE HORARIOS ROSA", expanded=True):
    if st.session_state.historial_rosas:
        for idx, rosa in enumerate(reversed(st.session_state.historial_rosas[-5:])):
            real_idx = len(st.session_state.historial_rosas) - 1 - idx
            col_val, col_time = st.columns([1, 1])
            with col_val:
                st.markdown(f'<div style="padding-top:10px;"><span class="rosa-val-txt">🌸 {rosa["valor"]}x</span></div>', unsafe_allow_html=True)
            with col_time:
                nueva_hora = st.text_input(f"edit_h_{real_idx}", value=rosa["hora"], key=f"rosa_key_{real_idx}", label_visibility="collapsed")
                st.session_state.historial_rosas[real_idx]["hora"] = nueva_hora
    else:
        st.write("Esperando registro de rosas...")

# --- SEMÁFORO ---
txt_s, col_s = obtener_semaforo()
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s};"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# --- BURBUJAS ---
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v}</div>' for v in reversed(st.session_state.historial[-12:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:15px; border: 1px solid #333; margin-top:10px; margin-bottom:10px;">{h_html}</div>', unsafe_allow_html=True)

# --- BOTÓN DESHACER ---
if st.button("🔙 DESHACER ÚLTIMA", use_container_width=True):
    if st.session_state.historial:
        v = st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        if v >= 10: st.session_state.historial_rosas.pop()
        st.rerun()
