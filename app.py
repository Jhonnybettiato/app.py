import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v3.4", page_icon="🦅", layout="wide")

# --- MEJORA VISUAL TOTAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Números de métricas en Blanco Brillante */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.4);
    }
    
    /* Etiquetas en gris claro */
    [data-testid="stMetricLabel"] {
        color: #ced4da !important;
        font-weight: bold !important;
        text-transform: uppercase;
    }

    .stMetric { 
        background-color: #111827; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #374151;
        box-shadow: 0px 10px 15px -3px rgba(0,0,0,0.5);
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
    st.header("🇵🇾 Panel de Control")
    st.number_input("Saldo Inicial Gs.", min_value=0, value=50000, step=5000, key="saldo_inicial")
    st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"], key="modo_juego")
    if st.button("🔄 Reiniciar"):
        st.session_state.historial = []
        st.session_state.ganancia_total = 0
        st.session_state.perdida_acumulada = 0
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
saldo_actual = st.session_state.saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{int(saldo_actual):,} Gs")
c2.metric("Ganancia Neta", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("Recuperación", f"{int(st.session_state.perdida_acumulada):,} Gs")

st.markdown("---")

# --- REGISTRO ---
st.subheader("📥 Registro de Vuelo")
col_in, col_ap = st.columns([2, 1])
with col_in:
    st.text_input("Ingresa el multiplicador y presiona ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_ap:
    st.write("##")
    st.checkbox("¿Aposté en esta ronda?", key="check_apuesta")

# --- HISTORIAL DE BURBUJAS (CORREGIDO) ---
if st.session_state.historial:
    st.subheader("📊 Historial Reciente")
    ultimos = list(reversed(st.session_state.historial))[:15]
    cols = st.columns(15)
    
    for i, val in enumerate(ultimos):
        if i < len(cols):
            # Aquí estaba el error de sintaxis, ahora está blindado:
            if val < 2.0:
                color = "#3498db" # Azul
            elif val < 10.0:
                color = "#9b59b6" # Morado
            else:
                color = "#e91e63" # Rosa
            
            with cols[i]:
                st.markdown(f"""
                    <div style="background-color:{color}; color:white; border-radius:50%; width:45px; height:45px; 
                    display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px;
                    border:2px solid rgba(255,255,255,0.2); box-shadow: 0px 4px 6px rgba(0,0,0,0.3);">
                        {val:.2f}
                    </div>
                """, unsafe_allow_html=True)
