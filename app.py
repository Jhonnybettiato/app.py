import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v3.5", page_icon="🦅", layout="wide")

# --- DISEÑO CSS AVANZADO (COLORES DINÁMICOS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Estilo General de Métricas */
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        font-size: 2.2rem !important;
    }
    
    /* COLOR VERDE PARA GANANCIA (Solo el valor) */
    [data-testid="stMetricValue"] > div:nth-child(1) { } /* Selector base */
    
    /* Aplicamos colores específicos por posición de columna */
    div[data-testid="column"]:nth-of-type(2) [data-testid="stMetricValue"] {
        color: #00ff41 !important; /* Verde Matrix/Neón */
        text-shadow: 0px 0px 15px rgba(0,255,65,0.4);
    }
    
    /* COLOR ROJO PARA RECUPERACIÓN (Solo el valor) */
    div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] {
        color: #ff3131 !important; /* Rojo Brillante */
        text-shadow: 0px 0px 15px rgba(255,49,49,0.4);
    }
    
    /* COLOR BLANCO PARA SALDO */
    div[data-testid="column"]:nth-of-type(1) [data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0px 0px 15px rgba(255,255,255,0.3);
    }

    [data-testid="stMetricLabel"] {
        color: #ced4da !important;
        font-weight: bold !important;
    }

    .stMetric { 
        background-color: #111827; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #374151;
    }
    
    .apuesta-box {
        background-color: #ffeb3b;
        color: #000000;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        border: 2px solid #fbc02d;
        margin: 10px 0px;
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
            
            if st.session_state.check_apuesta:
                target = 1.50 if st.session_state.modo_juego == "Conservadora (1.50x)" else 10.0
                # Usamos la apuesta sugerida calculada
                apuesta_base = st.session_state.apuesta_sugerida
                
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
    st.header("🇵🇾 Configuración")
    saldo_in = st.number_input("Saldo Inicial Gs.", min_value=0, value=100000, step=5000, key="saldo_inicial")
    
    # NUEVO: Selector de Porcentaje de Objetivo
    objetivo_pct = st.slider("Objetivo de Ganancia (%)", 10, 100, 20)
    st.caption(f"Buscando ganar: {int(saldo_in * (objetivo_pct/100)):,} Gs")
    
    st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"], key="modo_juego")
    
    if st.button("🔄 Reiniciar App"):
        st.session_state.historial = []
        st.session_state.ganancia_total = 0
        st.session_state.perdida_acumulada = 0
        st.rerun()

# --- CÁLCULO DE APUESTA SUGERIDA ---
# Si es conservador, arriesga un poco más del saldo. Si es rosa, arriesga muy poco.
if st.session_state.modo_juego == "Conservadora (1.50x)":
    # Fórmula: (Saldo * % objetivo) / 10 rondas para seguridad
    sugerida = (saldo_in * (objetivo_pct/100)) / 5
else:
    # Para rosas 10x, la apuesta debe ser pequeña porque se falla mucho
    sugerida = (saldo_in * (objetivo_pct/100)) / 20

# Ajustar a múltiplos de 1.000 para Paraguay y mínimo de 2.000
st.session_state.apuesta_sugerida = max(2000, int(sugerida // 1000) * 1000)

# --- INTERFAZ PRINCIPAL ---
saldo_actual = st.session_state.saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

c1, c2, c3 = st.columns(3)
c1.metric("SALDO ACTUAL", f"{int(saldo_actual):,} Gs")
c2.metric("GANANCIA NETA", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("RECUPERACIÓN", f"{int(st.session_state.perdida_acumulada):,} Gs")

# --- BLOQUE DE APUESTA SUGERIDA ---
st.markdown(f"""
    <div class="apuesta-box">
        📢 APUESTA RECOMENDADA: {st.session_state.apuesta_sugerida:,} Gs
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- REGISTRO ---
col_in, col_ap = st.columns([2, 1])
with col_in:
    st.text_input("Resultado del avión y ENTER:", key="entrada_vuelo", on_change=registrar_vuelo)
with col_ap:
    st.write("##")
    st.checkbox("¿Aposté esta sugerencia?", key="check_apuesta")

# --- HISTORIAL ---
if st.session_state.historial:
    st.subheader("📊 Últimos Resultados")
    ultimos = list(reversed(st.session_state.historial))[:15]
    cols = st.columns(15)
    for i, val in enumerate(ultimos):
        if i < len(cols):
            color = "#3498db" if val < 2.0 else "#9b59b6" if val < 10.0 else "#e91e63"
            with cols[i]:
                st.markdown(f"""<div style="background-color:{color}; color:white; border-radius:50%; width:45px; height:45px; 
                display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px;
                border:2px solid rgba(255,255,255,0.2);">{val:.2f}</div>""", unsafe_allow_html=True)
