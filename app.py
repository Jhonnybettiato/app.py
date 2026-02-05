import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v3.6", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Colores dinámicos para las métricas */
    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #ffffff !important; }
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #00ff41 !important; text-shadow: 0px 0px 15px rgba(0,255,65,0.4); }
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #ff3131 !important; text-shadow: 0px 0px 15px rgba(255,49,49,0.4); }

    .stMetric { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    
    /* Caja de Apuesta Recomendada */
    .apuesta-box {
        background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px;
        text-align: center; font-weight: 900; font-size: 1.4rem; border: 3px solid #fbc02d; margin: 10px 0px;
    }

    /* Semáforo de Señal */
    .semaforo {
        padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 1.5rem; margin: 15px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0

# --- NUEVO MOTOR DE ANÁLISIS (SEMÁFORO) ---
def motor_semaforo(h, modo):
    if len(h) < 3:
        return "🟡 AMARILLO: ANALIZANDO", "#f1c40f", "white" # Amarillo
    
    ultimos = h[-3:]
    vuelos_desde_rosa = 0
    for v in reversed(h):
        if v >= 10: break
        vuelos_desde_rosa += 1

    if modo == "Conservadora (1.50x)":
        # Rojo si los últimos 2 son muy malos
        if h[-1] < 1.2 and h[-2] < 1.2:
            return "🔴 ROJO: NO APOSTAR", "#ff3131", "white"
        # Verde si hay buena racha
        if sum(ultimos)/3 >= 1.7:
            return "🟢 VERDE: HACER APUESTA", "#00ff41", "black"
        # Por defecto amarillo
        return "🟡 AMARILLO: ESPERAR PATRÓN", "#f1c40f", "black"
    
    else: # Modo Cazador de Rosas (10x)
        if vuelos_desde_rosa >= 18:
            return "🟢 VERDE: PROBABILIDAD ROSA ALTA", "#e91e63", "white"
        if vuelos_desde_rosa >= 12:
            return "🟡 AMARILLO: CICLO CERCA", "#f1c40f", "black"
        return "🔴 ROJO: NO APOSTAR (Ciclo Joven)", "#ff3131", "white"

# --- FUNCIÓN DE REGISTRO ---
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

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🇵🇾 Ajustes")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=100000, step=5000, key="saldo_inicial")
    objetivo_pct = st.slider("Objetivo de Ganancia (%)", 10, 100, 20)
    st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"], key="modo_juego")
    if st.button("🔄 Reiniciar App"):
        st.session_state.historial, st.session_state.ganancia_total, st.session_state.perdida_acumulada = [], 0, 0
        st.rerun()

# --- CÁLCULOS ---
sugerida = (saldo_in * (objetivo_pct/100)) / (5 if st.session_state.modo_juego == "Conservadora (1.50x)" else 25)
st.session_state.apuesta_sugerida = max(2000, int(sugerida // 1000) * 1000)
saldo_actual = st.session_state.saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

# --- INTERFAZ ---
c1, c2, c3 = st.columns(3)
c1.metric("SALDO ACTUAL", f"{int(saldo_actual):,} Gs")
c2.metric("GANANCIA NETA", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("RECUPERACIÓN", f"{int(st.session_state.perdida_acumulada):,} Gs")

# SEMÁFORO VISUAL
msg, color_bg, color_txt = motor_semaforo(st.session_state.historial, st.session_state.modo_juego)
st.markdown(f'<div class="semaforo" style="background-color:{color_bg}; color:{color_txt};">{msg}</div>', unsafe_allow_html=True)

st.markdown(f'<div class="apuesta-box">📢 APUESTA RECOMENDADA: {st.session_state.apuesta_sugerida:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_in, col_ap = st.columns([2, 1])
with col_in: st.text_input("Resultado del avión y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_ap: 
    st.write("##")
    st.checkbox("¿Aposté?", key="check_apuesta")

# BURBUJAS
if st.session_state.historial:
    ultimos = list(reversed(st.session_state.historial))[:15]
    cols = st.columns(15)
    for i, val in enumerate(ultimos):
        if i < len(cols):
            bg = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
            with cols[i]: st.markdown(f'<div style="background-color:{bg}; color:white; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:10px;">{val:.2f}</div>', unsafe_allow_html=True)
