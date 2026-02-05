import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v4.3", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-weight: 850 !important; font-size: 2.2rem !important; }
    div[data-testid="stMetric"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #ffffff !important; text-shadow: 0px 0px 15px rgba(255,255,255,0.3); }
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #00ff41 !important; text-shadow: 0px 0px 15px rgba(0,255,65,0.4); }
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #ff3131 !important; text-shadow: 0px 0px 15px rgba(255,49,49,0.4); }
    .stMetric { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .apuesta-box { background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.4rem; border: 3px solid #fbc02d; margin: 10px 0px; }
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
    .historial-container { display: flex; flex-direction: row; flex-wrap: nowrap; overflow-x: auto; gap: 10px; padding: 10px 0px; }
    .burbuja { min-width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; color: white; border: 2px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0
if 'ganancia_neta' not in st.session_state: st.session_state.ganancia_neta = 0
if 'recuperacion' not in st.session_state: st.session_state.recuperacion = 0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True

# --- FUNCIONES DE REGISTRO ---
def registrar_vuelo():
    valor = st.session_state.entrada_vuelo
    if valor:
        try:
            vuelo_val = float(valor.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            if st.session_state.check_apuesta:
                apuesta = st.session_state.apuesta_sugerida
                target = 1.50 if st.session_state.modo_juego == "Conservadora (1.50x)" else 2.0 if st.session_state.modo_juego == "Estrategia 2x2" else 10.0
                st.session_state.saldo_dinamico -= apuesta
                if vuelo_val >= target:
                    premio_bruto = apuesta * target
                    st.session_state.saldo_dinamico += premio_bruto
                    st.session_state.ganancia_neta += (premio_bruto - apuesta)
                    st.session_state.recuperacion = 0
                else:
                    st.session_state.recuperacion += apuesta
        except: pass
        st.session_state.entrada_vuelo = ""

# --- MOTOR DE SEMÁFORO (CON HUECO DE TIEMPO) ---
def motor_semaforo(h, modo):
    if len(h) < 3: return "🟡 ANALIZANDO FLUJO", "#f1c40f", "black"
    
    if modo == "Cazador de Rosas (10x)":
        # Contamos cuántos vuelos han pasado desde la última Rosa
        v_desde_rosa = 0
        for v in reversed(h):
            if v >= 10: break
            v_desde_rosa += 1
        
        # Lógica de Hueco de Tiempo (25 vuelos)
        if v_desde_rosa >= 25:
            return f"🟢 VERDE: HUECO DETECTADO ({v_desde_rosa} VUELOS)", "#e91e63", "white"
        elif v_desde_rosa >= 18:
            return f"🟡 AMARILLO: PRESIÓN ALTA ({v_desde_rosa}/25)", "#f1c40f", "black"
        else:
            return f"🔴 ROJO: CICLO JOVEN ({v_desde_rosa} VUELOS)", "#ff3131", "white"
    
    elif modo == "Estrategia 2x2":
        if h[-1] < 2.0 and h[-2] < 2.0: return "🟢 VERDE: ENTRAR 2x2", "#00ff41", "black"
        return "🟡 AMARILLO: BUSCANDO PATRÓN", "#f1c40f", "black"
    
    else: # Conservadora
        if h[-1] < 1.2 and h[-2] < 1.2: return "🔴 ROJO: ESPERAR", "#ff3131", "white"
        return "🟢 VERDE: DALE!", "#00ff41", "black"

# --- SIDEBAR ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_input = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = saldo_input
        st.session_state.primer_inicio = False
    
    obj_pct = st.slider("Meta %", 10, 100, 20)
    st.selectbox("Estrategia:", ["Cazador de Rosas (10x)", "Estrategia 2x2", "Conservadora (1.50x)"], key="modo_juego")
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear()
        st.rerun()

# --- CÁLCULOS ---
div_ap = 25 if st.session_state.modo_juego == "Cazador de Rosas (10x)" else 8 if st.session_state.modo_juego == "Estrategia 2x2" else 5
st.session_state.apuesta_sugerida = max(2000, int(((saldo_input * (obj_pct/100)) / div_ap) // 1000) * 1000)

# --- INTERFAZ ---
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(st.session_state.saldo_dinamico):,} Gs")
c2.metric("Ganancia Neta", f"{int(st.session_state.ganancia_neta):,} Gs")
c3.metric("Recuperación", f"{int(st.session_state.recuperacion):,} Gs")

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
    for val in reversed(st.session_state.historial[-30:]): # Mostramos más para ver el hueco
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_b += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    st.markdown(f'<div class="historial-container">{html_b}</div>', unsafe_allow_html=True)
