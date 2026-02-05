import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v4.6", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-weight: 850 !important; font-size: 2.2rem !important; }
    div[data-testid="stMetric"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #ffffff !important; }
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #00ff41 !important; }
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #ff3131 !important; }
    .stMetric { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .apuesta-box { background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.4rem; margin: 10px 0px; }
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; }
    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 10px 0px; }
    .burbuja { min-width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

# --- LÓGICA DE COMPENSACIÓN (TU EJEMPLO) ---
def registrar_vuelo():
    valor = st.session_state.entrada_vuelo
    if valor:
        try:
            vuelo_val = float(valor.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            
            if st.session_state.check_apuesta:
                apuesta = st.session_state.apuesta_sugerida
                if st.session_state.modo_juego == "Cazador de Rosas (10x)": target = 10.0
                elif st.session_state.modo_juego == "Estrategia 2x2": target = 2.0
                else: target = 1.50
                
                # Proceso Casino: Resta apuesta siempre
                st.session_state.saldo_dinamico -= apuesta
                
                if vuelo_val >= target:
                    # GANA: Suma premio bruto
                    premio_bruto = apuesta * target
                    st.session_state.saldo_dinamico += premio_bruto
                    
        except: pass
        st.session_state.entrada_vuelo = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = saldo_in
        st.session_state.primer_inicio = False
    
    obj_pct = st.slider("Meta %", 10, 100, 20)
    st.selectbox("Estrategia:", ["Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"], key="modo_juego")
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- CÁLCULO DE MÉTRICAS DINÁMICAS ---
# Aquí es donde ocurre la magia de tu ejemplo
diferencia = st.session_state.saldo_dinamico - saldo_in

if diferencia >= 0:
    ganancias_display = diferencia
    perdidas_display = 0
else:
    ganancias_display = 0
    perdidas_display = abs(diferencia)

# --- PANEL DE MÉTRICAS ---
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(st.session_state.saldo_dinamico):,} Gs")
c2.metric("Ganancias", f"{int(ganancias_display):,} Gs")
c3.metric("Perdidas", f"{int(perdidas_display):,} Gs")

# SEMÁFORO (Hueco de Tiempo)
def motor_semaforo(h, modo):
    if len(h) < 3: return "🟡 ANALIZANDO", "#f1c40f", "black"
    v_desde_rosa = 0
    for v in reversed(h):
        if v >= 10: break
        v_desde_rosa += 1
    if modo == "Cazador de Rosas (10x)":
        if v_desde_rosa >= 25: return f"🟢 VERDE: HUECO ({v_desde_rosa})", "#e91e63", "white"
        return f"🔴 ROJO: CICLO BAJO ({v_desde_rosa})", "#ff3131", "white"
    return "🟡 BUSCANDO PATRÓN", "#f1c40f", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, st.session_state.modo_juego)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {st.session_state.apuesta_sugerida:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_in, col_ap = st.columns([2, 1])
with col_in: st.text_input("Resultado y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_ap: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-30:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)
