import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v4.0", page_icon="🦅", layout="wide")

# --- DISEÑO CSS (INCLUYE HISTORIAL HORIZONTAL) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-weight: 850 !important; font-size: 2.2rem !important; }
    
    /* Colores de métricas */
    div[data-testid="stMetric"]:nth-of-type(1) [data-testid="stMetricValue"] { color: #ffffff !important; text-shadow: 0px 0px 15px rgba(255,255,255,0.3); }
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] { color: #00ff41 !important; text-shadow: 0px 0px 15px rgba(0,255,65,0.4); }
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] { color: #ff3131 !important; text-shadow: 0px 0px 15px rgba(255,49,49,0.4); }
    
    .stMetric { background-color: #111827; padding: 20px; border-radius: 15px; border: 1px solid #374151; }
    .apuesta-box { background-color: #ffeb3b; color: #000000; padding: 15px; border-radius: 10px; text-align: center; font-weight: 900; font-size: 1.4rem; border: 3px solid #fbc02d; margin: 10px 0px; }
    .semaforo { padding: 20px; border-radius: 15px; text-align: center; font-weight: 900; font-size: 1.6rem; margin: 15px 0px; }

    /* CONTENEDOR HORIZONTAL PARA BURBUJAS */
    .historial-container {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 10px;
        padding: 10px 0px;
    }
    .burbuja {
        min-width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 11px;
        color: white;
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estado
if 'historial' not in st.session_state: st.session_state.historial = []
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0
if 'ult_apuesta_realizada' not in st.session_state: st.session_state.ult_apuesta_realizada = 0

# --- FUNCIONES ---
def registrar_vuelo():
    valor = st.session_state.entrada_vuelo
    if valor:
        try:
            vuelo_val = float(valor.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            if st.session_state.check_apuesta:
                target = 1.50 if st.session_state.modo_juego == "Conservadora (1.50x)" else 10.0
                apuesta = st.session_state.apuesta_sugerida
                st.session_state.ult_apuesta_realizada = apuesta
                if vuelo_val >= target:
                    st.session_state.ganancia_total += (apuesta * (target - 1))
                    st.session_state.perdida_acumulada = 0
                else:
                    st.session_state.perdida_acumulada += apuesta
            else:
                st.session_state.ult_apuesta_realizada = 0
        except: pass
        st.session_state.entrada_vuelo = ""

def deshacer_ultimo():
    if st.session_state.historial:
        ultimo_valor = st.session_state.historial.pop()
        if st.session_state.ult_apuesta_realizada > 0:
            target = 1.50 if st.session_state.modo_juego == "Conservadora (1.50x)" else 10.0
            if ultimo_valor >= target:
                st.session_state.ganancia_total -= (st.session_state.ult_apuesta_realizada * (target - 1))
            else:
                st.session_state.perdida_acumulada -= st.session_state.ult_apuesta_realizada
            st.session_state.ult_apuesta_realizada = 0

# --- ESTRUCTURA ---
with st.sidebar:
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=100000, step=5000, key="saldo_inicial")
    obj_pct = st.slider("Meta %", 10, 100, 20)
    st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"], key="modo_juego")
    if st.button("🔄 Reiniciar App"):
        st.session_state.historial, st.session_state.ganancia_total, st.session_state.perdida_acumulada = [], 0, 0
        st.rerun()

div_ap = 5 if st.session_state.modo_juego == "Conservadora (1.50x)" else 25
st.session_state.apuesta_sugerida = max(2000, int(((saldo_in * (obj_pct/100)) / div_ap) // 1000) * 1000)
saldo_actual = st.session_state.saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

# --- MÉTRICAS ---
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(saldo_actual):,} Gs")
c2.metric("Ganancia Neta", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("Recuperación", f"{int(st.session_state.perdida_acumulada):,} Gs")

# SEMÁFORO
def motor_semaforo(h, modo):
    if len(h) < 3: return "🟡 ANALIZANDO", "#f1c40f", "black"
    if modo == "Conservadora (1.50x)":
        if h[-1] < 1.2 and h[-2] < 1.2: return "🔴 ROJO: NO APOSTAR", "#ff3131", "white"
        if sum(h[-3:])/3 >= 1.7: return "🟢 VERDE: DALE!", "#00ff41", "black"
    else:
        v_rosa = 0
        for v in reversed(h):
            if v >= 10: break
            v_rosa += 1
        if v_rosa >= 18: return "🟢 VERDE: SEÑAL ROSA", "#e91e63", "white"
    return "🟡 ESPERAR PATRÓN", "#f1c40f", "black"

msg, bg, txt = motor_semaforo(st.session_state.historial, st.session_state.modo_juego)
st.markdown(f'<div class="semaforo" style="background-color:{bg}; color:{txt};">{msg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="apuesta-box">📢 APUESTA SUGERIDA: {st.session_state.apuesta_sugerida:,} Gs</div>', unsafe_allow_html=True)

st.markdown("---")
col_in, col_ap, col_del = st.columns([2, 1, 1])
with col_in: st.text_input("Resultado y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_ap: st.write("##"); st.checkbox("¿Aposté?", key="check_apuesta")
with col_del: st.write("##"); st.button("⚠️ Borrar Último", on_click=deshacer_ultimo)

# --- HISTORIAL HORIZONTAL ---
if st.session_state.historial:
    st.subheader("📊 Historial Reciente")
    # Generamos el HTML para todas las burbujas
    html_burbujas = ""
    for val in reversed(st.session_state.historial[-20:]): # Mostramos los últimos 20
        color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
        html_burbujas += f'<div class="burbuja" style="background-color:{color};">{val:.2f}</div>'
    
    # Lo metemos dentro del contenedor horizontal
    st.markdown(f'<div class="historial-container">{html_burbujas}</div>', unsafe_allow_html=True)
