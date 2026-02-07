import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.2", page_icon="🦅", layout="wide")

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
    .time-elite { background: #121212; padding: 20px; border-radius: 20px; border: 2px solid #FFFFFF; text-align: center; }
    .burbuja { min-width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; border: 2px solid rgba(255,255,255,0.1); }
    
    /* Animación para Señal Activa */
    .alerta-activa {
        background: #ff3131;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-weight: 900;
        font-size: 1.5rem;
        animation: pulse 1s infinite;
    }
    @keyframes pulse { 0% {transform: scale(1);} 50% {transform: scale(1.05);} 100% {transform: scale(1);} }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'transacciones' not in st.session_state: st.session_state.transacciones = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

py_tz = pytz.timezone('America/Asuncion')

# --- LÓGICA DE MOTOR INDEPENDIENTE ---
def obtener_analisis():
    if len(st.session_state.historial) < 5:
        return "ESPERANDO DATOS...", "#222", False
    
    hist = st.session_state.historial
    est = st.session_state.modo_sel
    
    # 1. CAZADORA 10X (Patrón de Proximidad)
    if "Cazador" in est:
        # Analiza la distancia entre los últimos 10x
        distancia = 0
        encontrado = False
        for i, v in enumerate(reversed(hist)):
            if v >= 10:
                distancia = i
                encontrado = True
                break
        if encontrado and 2 <= distancia <= 8:
            return "🔥 CAZADORA: RACHA ACTIVA", "#e67e22", True
        return "⏳ CAZADORA: BUSCANDO CICLO", "#121212", False

    # 2. HUECO 10X+ (Estadística Pura)
    elif "Hueco" in est:
        rondas_sin_rosa = 0
        for v in reversed(hist):
            if v >= 10: break
            rondas_sin_rosa += 1
        if rondas_sin_rosa >= 25:
            return f"💖 HUECO ACTIVO ({rondas_sin_rosa})", "#e91e63", True
        return f"⏳ ESPERANDO: {rondas_sin_rosa}/25", "#121212", False

    # 3. CONSERVADORA (1.50x)
    elif "1.50x" in est:
        if hist[-1] >= 1.5 and hist[-2] >= 1.5:
            return "✅ SEÑAL: ESTABILIDAD", "#27ae60", True
        return "❌ SIN SEÑAL 1.5x", "#121212", False

    # 4. 2x2
    elif "2x2" in est:
        if hist[-1] < 2 and hist[-2] > 2:
            return "⚡ SEÑAL: RECUPERACIÓN", "#2980b9", True
        return "⏳ BUSCANDO CICLO 2.0x", "#121212", False

    return "ERROR ESTRATEGIA", "#222", False

def registrar_valor():
    if st.session_state.entrada_manual:
        try:
            v_val = float(str(st.session_state.entrada_manual).replace(',', '.'))
            st.session_state.historial.append(v_val)
            
            # Lógica de Saldo
            if st.session_state.check_apuesta:
                apuesta = float(st.session_state.valor_apuesta_manual)
                est = st.session_state.modo_sel
                target = 1.5 if "1.50x" in est else 2.0 if "2x2" in est else 10.0
                
                impacto = (apuesta * (target - 1)) if v_val >= target else -apuesta
                st.session_state.saldo_dinamico += impacto
                st.session_state.transacciones.append(impacto)
            
        except: pass
        st.session_state.entrada_manual = ""

# --- INTERFAZ ---
with st.sidebar:
    st.header("🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    st.session_state.modo_sel = st.selectbox("Estrategia:", 
        ["Cazador (10x)", "Hueco 10x+", "Conservadora (1.50x)", "2x2"])
    
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

st.markdown("<h1 style='text-align: center; color: white;'>🦅 AVIATOR ELITE v8.2</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card card-border-white"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card card-border-green"><p class="label-elite">Ganancia</p><h2 class="valor-elite valor-verde">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card card-border-red"><p class="label-elite">Pérdida</p><h2 class="valor-elite valor-rojo">{int(min(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: SEMÁFORO INTELIGENTE
txt_analisis, color_analisis, es_alerta = obtener_analisis()
st.markdown(f"""
    <div style="background:{color_analisis}; padding:25px; border-radius:20px; text-align:center; border:2px solid #555;">
        <p class="label-elite" style="font-size:1.2rem;">SISTEMA DE SEÑAL - {st.session_state.modo_sel}</p>
        <h2 style="color:white; font-weight:900; margin:0;">{txt_analisis}</h2>
    </div>
    """, unsafe_allow_html=True)

# FILA 3: ENTRADAS
st.markdown("<br>", unsafe_allow_html=True)
col_in, col_ap, col_ck = st.columns([2, 1, 1])
with col_in: st.text_input("VALOR DEL VUELO:", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("APUESTA Gs:", value=2000, step=1000, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-12:])])
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px; background:#0a0a0a; border-radius:15px; margin-top:20px;">{h_html}</div>', unsafe_allow_html=True)
