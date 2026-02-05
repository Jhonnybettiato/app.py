import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v3.3", page_icon="🦅", layout="wide")

# --- MEJORA DE COLOR Y VISIBILIDAD (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Estilo para que los números de las métricas resalten */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.8rem !important;
        text-shadow: 0px 0px 10px rgba(255,255,255,0.2);
    }
    
    /* Estilo para las etiquetas de las métricas (el nombre arriba del número) */
    [data-testid="stMetricLabel"] {
        color: #adb5bd !important;
        font-weight: bold !important;
    }

    .stMetric { 
        background-color: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #374151;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    
    .rosa-signal { 
        background-color: #a21caf; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        border: 2px solid #f0abfc; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estado
if 'historial' not in st.session_state: st.session_state.historial = []
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0

# --- FUNCIÓN DE REGISTRO ---
def registrar_vuelo():
    valor_texto = st.session_state.entrada_vuelo
    if valor_texto:
        try:
            vuelo_val = float(valor_texto.replace(',', '.'))
            st.session_state.historial.append(vuelo_val)
            if len(st.session_state.historial) > 50:
                st.session_state.historial.pop(0)
            
            if st.session_state.check_apuesta:
                target = 1.50 if st.session_state.modo_juego == "Conservadora (1.50x)" else 10.0
                apuesta_base = max(2000, int(st.session_state.saldo_inicial * 0.05))
                
                if vuelo_val >= target:
                    st.session_state.ganancia_total += (apuesta_base * (target - 1))
                    st.session_state.perdida_acumulada = 0
                else:
                    st.session_state.perdida_acumulada += apuesta_base
        except:
            pass
        st.session_state.entrada_vuelo = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🇵🇾 Panel v3.3")
    st.number_input("Saldo Inicial Gs.", min_value=0, value=50000, step=5000, key="saldo_inicial")
    st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"], key="modo_juego")
    if st.button("🔄 Reiniciar Todo"):
        st.session_state.historial = []
        st.session_state.ganancia_total = 0
        st.session_state.perdida_acumulada = 0
        st.rerun()

# --- INTERFAZ ---
saldo_actual = st.session_state.saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

# Las métricas ahora usarán el estilo "fuerte" definido arriba
c1, c2, c3 = st.columns(3)
c1.metric("SALDO ACTUAL", f"{int(saldo_actual):,} Gs")
c2.metric("GANANCIA NETA", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("DEUDA/RECUP.", f"{int(st.session_state.perdida_acumulada):,} Gs")

st.markdown("---")

# --- INPUT ---
st.subheader("📥 Registro de Vuelo")
col_in, col_ap = st.columns([2, 1])

with col_in:
    st.text_input("Escribe el número y presiona ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)

with col_ap:
    st.write("##")
    st.checkbox("¿Aposté en esta ronda?", key="check_apuesta")

# --- HISTORIAL ---
if st.session_state.historial:
    st.subheader("📊 Historial Reciente")
    ultimos_vuelos = list(reversed(st.session_state.historial))[:15]
    cols = st.columns(15)
    for i, valor in enumerate(ultimos_vuelos):
        if i < len(cols):
            color = "#3498db" if valor < 2.0 else "#9b59b6" if valor < 10.0 else "#
