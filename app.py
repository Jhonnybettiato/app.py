import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v5.0", page_icon="🦅", layout="wide")

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
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    
    obj_pct = st.slider("Meta %", 10, 100, 20)
    modo = st.selectbox("Estrategia:", ["Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"], key="modo_juego")
    
    div_ap = 25 if modo == "Cazador de Rosas (10x)" else 8 if modo == "Estrategia 2x2" else 5
    apuesta_auto = max(2000, int(((saldo_in * (obj_pct/100)) / div_ap) // 1000) * 1000)

    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- FUNCIÓN DE REGISTRO CON LÓGICA DE MARGEN ---
def registrar_vuelo():
    if st.session_state.entrada_vuelo:
        try:
            vuelo_val = float(st.session_state.entrada_vuelo.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                
                # Ajuste de targets para la comparación
                if st.session_state.modo_juego == "Cazador de Rosas (10x)": target = 10.0
                elif st.session_state.modo_juego == "Estrategia 2x2": target = 2.0
                else: target = 1.50
                
                # RESTA SIEMPRE
                st.session_state.saldo_dinamico -= ap_real
                
                # LÓGICA ESTRICTA: Debe ser > que el target para ganar
                if vuelo_val > target:
                    st.session_state.saldo_dinamico += (ap_real * target)
                # Si es igual o menor (vuelo_val <= target), se queda como pérdida
        except: pass
        st.session_state.entrada_vuelo = ""

# --- COMPENSACIÓN ---
diferencia = st.session_state.saldo_dinamico - saldo_in
ganancias_display = max(0, diferencia)
perdidas_display = abs(min(0, diferencia))

# --- MÉTRICAS ---
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(st.session_state.saldo_dinamico):,} Gs")
c2.metric("Ganancias", f"{int(ganancias_display):,} Gs")
c3.metric("Perdidas", f"{int(perdidas_display):,} Gs")

# SEMÁFORO
def motor_semaforo(h, modo_sel):
    if len(h) < 3: return "🟡 ANALIZANDO", "#f1c40f", "black"
    v_desde_rosa = 0
    for v in reversed(h):
        if v >= 10: break
        v_desde_rosa += 1
    if modo_sel == "Cazador de Rosas (10x)":
        if v_desde_rosa >= 25: return f"🟢 VERDE: HUECO ({v_desde_rosa})", "#e91e63", "white"
        return f"🔴 ROJO: CICLO BAJO ({v_desde_rosa})", "#ff3131", "white"
    return "🟡 BUSCANDO PATRÓN", "#f1c40f", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, modo)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {apuesta_auto:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_vuelo, col_monto, col_check = st.columns([2, 1, 1])
with col_vuelo: st.text_input("Resultado y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_monto: st.number_input("Gs. Apostados:", value=float(apuesta_auto), step=1000.0, key="valor_apuesta_manual")
with col_check: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-30:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)
