import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v5.2", page_icon="🦅", layout="wide")

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
    .radar-rosas { background-color: #2d3436; color: #fd79a8; padding: 5px; border-radius: 5px; text-align: center; font-size: 0.9rem; margin-top: -10px; font-weight: bold; }
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
    
    # NUEVA LISTA DE ESTRATEGIAS
    modo = st.selectbox("Estrategia:", 
                        ["Estrategia del Hueco", "Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"], 
                        key="modo_juego")
    
    # Divisores de apuesta
    div_ap = 25 if "Rosas" in modo or "Hueco" in modo else 8 if "2x2" in modo else 5
    apuesta_auto = max(2000, int(((saldo_in * (obj_pct/100)) / div_ap) // 1000) * 1000)

    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- REGISTRO ---
def registrar_vuelo():
    if st.session_state.entrada_vuelo:
        try:
            vuelo_val = float(st.session_state.entrada_vuelo.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            if st.session_state.check_apuesta:
                ap_real = float(st.session_state.valor_apuesta_manual)
                
                # Target según modo
                if "Rosas" in st.session_state.modo_juego or "Hueco" in st.session_state.modo_juego:
                    target = 10.0
                elif "2x2" in st.session_state.modo_juego:
                    target = 2.0
                else:
                    target = 1.50
                
                st.session_state.saldo_dinamico -= ap_real
                if vuelo_val > target: # Lógica estricta casino
                    st.session_state.saldo_dinamico += (ap_real * target)
        except: pass
        st.session_state.entrada_vuelo = ""

# --- COMPENSACIÓN Y MÉTRICAS ---
diferencia = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(st.session_state.saldo_dinamico):,} Gs")
c2.metric("Ganancias", f"{int(max(0, diferencia)):,} Gs")
c3.metric("Perdidas", f"{int(abs(min(0, diferencia))):,} Gs")

# --- LÓGICA DE HUECO ---
v_desde_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10: break
    v_desde_rosa += 1

# --- SEMÁFORO ACTUALIZADO ---
def motor_semaforo(h, modo_sel, hueco):
    if len(h) < 3: return "🟡 ANALIZANDO FLUJO", "#f1c40f", "black"
    
    if modo_sel == "Estrategia del Hueco":
        if hueco >= 25: return f"💖 HUECO ACTIVO ({hueco})", "#e91e63", "white"
        return f"⏳ CARGANDO HUECO ({hueco}/25)", "#2d3436", "white"
    
    elif modo_sel == "Cazador de Rosas (10x)":
        if h[-1] >= 10: return "🟢 ROSA RECIENTE", "#00ff41", "black"
        return "🔴 BUSCANDO ROSA", "#ff3131", "white"
    
    elif modo_sel == "Estrategia 2x2":
        if len(h) >= 2 and h[-1] < 2.0 and h[-2] < 2.0: return "🟢 PATRÓN 2x2", "#00ff41", "black"
        return "🟡 BUSCANDO DOBLE BAJO", "#f1c40f", "black"
    
    else: # Conservadora
        return "🟢 FLUJO ESTABLE (1.50x)", "#00ff41", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, modo, v_desde_rosa)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="radar-rosas">📡 RADAR ROSA: {v_desde_rosa} vuelos sin 10x+</div>', unsafe_allow_html=True)

st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {apuesta_auto:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_v, col_m, col_c = st.columns([2, 1, 1])
with col_v: st.text_input("Resultado y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_m: st.number_input("Gs. Apostados:", value=float(apuesta_auto), step=1000.0, key="valor_apuesta_manual")
with col_c: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")

# HISTORIAL
if st.session_state.historial:
    html_b = ""
    for val in reversed(st.session_state.historial[-30:]):
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)
