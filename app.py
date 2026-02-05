import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v3.7", page_icon="🦅", layout="wide")

# --- DISEÑO CSS DINÁMICO (COLORES FIJOS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Estilo base para todas las métricas */
    [data-testid="stMetricValue"] {
        font-weight: 850 !important;
        font-size: 2.2rem !important;
    }

    /* 1. SALDO ACTUAL - BLANCO */
    div[data-testid="stMetric"]:nth-of-type(1) [data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.3);
    }
    
    /* 2. GANANCIA NETA - VERDE */
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] {
        color: #00ff41 !important;
        text-shadow: 0px 0px 15px rgba(0,255,65,0.4);
    }
    
    /* 3. RECUPERACIÓN - ROJO */
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] {
        color: #ff3131 !important;
        text-shadow: 0px 0px 15px rgba(255,49,49,0.4);
    }

    /* Etiquetas de los títulos (Gris claro) */
    [data-testid="stMetricLabel"] {
        color: #ced4da !important;
        font-weight: bold !important;
        text-transform: uppercase;
        font-size: 0.9rem !important;
    }

    .stMetric { 
        background-color: #111827; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #374151; 
    }
    
    .apuesta-box {
        background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px;
        text-align: center; font-weight: 900; font-size: 1.4rem; border: 3px solid #fbc02d; margin: 10px 0px;
    }

    .semaforo {
        padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0

# --- LÓGICA DEL SEMÁFORO ---
def motor_semaforo(h, modo):
    if len(h) < 3:
        return "🟡 AMARILLO: ANALIZANDO", "#f1c40f", "black"
    
    vuelos_desde_rosa = 0
    for v in reversed(h):
        if v >= 10: break
        vuelos_desde_rosa += 1

    if modo == "Conservadora (1.50x)":
        if h[-1] < 1.2 and h[-2] < 1.2:
            return "🔴 ROJO: NO APOSTAR", "#ff3131", "white"
        if sum(h[-3:])/3 >= 1.7:
            return "🟢 VERDE: HACER APUESTA", "#00ff41", "black"
        return "🟡 AMARILLO: ESPERAR", "#f1c40f", "black"
    else:
        if vuelos_desde_rosa >= 18:
            return "🟢 VERDE: SEÑAL ROSA", "#e91e63", "white"
        if vuelos_desde_rosa >= 12:
            return "🟡 AMARILLO: CICLO CERCA", "#f1c40f", "black"
        return "🔴 ROJO: CICLO BAJO", "#ff3131", "white"

# --- REGISTRO ---
def registrar_vuelo():
    valor = st.session_state.entrada_vuelo
    if valor:
        try:
            vuelo_val = float(valor.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            if len(st.session_state.historial) > 50: st.session_state.historial.pop(0)
            
            if st.session_state.check_apuesta:
                target = 1.50 if st.session_state.modo_juego == "Conservadora (1.50x)" else 10.0
                apuesta = st.session_state.apuesta_sugerida
                if vuelo_val >= target:
                    st.session_state.ganancia_total += (apuesta * (target - 1))
                    st.session_state.perdida_acumulada = 0
                else:
                    st.session_state.perdida_acumulada += apuesta
        except: pass
        st.session_state.entrada_vuelo = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Panel")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=100000, step=5000, key="saldo_inicial")
    obj_pct = st.slider("Meta de Ganancia %", 10, 100, 20)
    st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"], key="modo_juego")
    if st.button("🔄 Reiniciar App"):
        st.session_state.historial, st.session_state.ganancia_total, st.session_state.perdida_acumulada = [], 0, 0
        st.rerun()

# --- CÁLCULOS ---
div = 5 if st.session_state.modo_juego == "Conservadora (1.50x)" else 25
sugerida = (saldo_in * (obj_pct/100)) / div
st.session_state.apuesta_sugerida = max(2000, int(sugerida // 1000) * 1000)
saldo_actual = st.session_state.saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

# --- INTERFAZ ---
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(saldo_actual):,} Gs")
c2.metric("Ganancia Neta", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("Recuperación", f"{int(st.session_state.perdida_acumulada):,} Gs")

msg, bg, txt = motor_semaforo(st.session_state.historial, st.session_state.modo_juego)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {st.session_state.apuesta_sugerida:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_in, col_ap = st.columns([2, 1])
with col_in: st.text_input("Resultado y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_ap: 
    st.write("##")
    st.checkbox("¿Aposté?", key="check_apuesta")

# BURBUJAS
if st
