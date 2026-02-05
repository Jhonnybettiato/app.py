import streamlit as st
import pandas as pd

# 1. Configuración de página con moneda PYG
st.set_page_config(page_title="Aviator PY Pro", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #e91e63; color: white; border-radius: 10px; font-weight: bold; height: 3.5em; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .bet-signal { 
        background-color: #22c55e; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: bold;
        border: 2px solid #ffffff;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de datos
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state:
    st.session_state.perdida_acumulada = 0
if 'ganancia_total' not in st.session_state:
    st.session_state.ganancia_total = 0

# 3. Barra Lateral Configurada para Paraguay
with st.sidebar:
    st.header("🇵🇾 Ajustes de Banca")
    # Saldo en Gs (Ejemplo: 10.000)
    saldo_inicial = st.number_input("Saldo en Guaraníes", min_value=0, value=10000, step=1000)
    st.markdown("---")
    if st.button("🔄 Reiniciar Sesión"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0
        st.session_state.ganancia_total = 0
        st.rerun()

# 4. Lógica de Análisis Estratégico
def analizar_py(h):
    if len(h) < 3: return "Recolectando datos...", 0, 0, "info"
    ult = h[-3:]
    promedio = sum(ult)/3
    confianza = min(int((promedio / 2.2) * 100), 98)
    
    if all(x < 1.35 for x in ult): return "🛑 RIESGO EXTREMO: Racha muy baja", 0, 0, "error"
    if ult[-1] > 10.0: return "📉 ENFRIAMIENTO: Salió un Rosa alto", 0, 0, "warning"
    if promedio > 1.85: return "🔥 ¡APUESTA AHORA!", 1.50, confianza, "success"
    
    return "⚖️ Esperando Oportunidad...", 1.25, 0, "info"

# 5. Cabecera con Métricas en Gs
st.title("🦅 Aviator Estratega PY v2.6")
saldo_actual = saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

c1, c2, c3 = st.columns(3)
c1.metric("Saldo Real Gs.", f"{saldo_actual:,}")
c2.metric("Meta de Sesión Gs.", f"{int(saldo_inicial * 1.2):,}")
c3.metric("Ganancia Neta Gs.", f"{int(st.session_state.ganancia_total):,}", 
          delta=f"{int(st.session_state.ganancia_total - st.session_state.perdida_acumulada):,}")

st.markdown("---")

# 6. Registro con Selección de Apuesta
with st.container():
    st.subheader("📥 Registro de Vuelo")
    col_v, col_a = st.columns([1, 1])
    
    with col_v:
        vuelo_in = st.number_input("Multiplicador del avión:", min_value=1.0, step=0.01, format="%.2f")
    
    with col_a:
        # Pregunta clave antes de registrar
        apostaste = st.radio("¿Pusiste dinero en este vuelo?", ["No, solo miraba", "SÍ, aposté"], horizontal=True)

    if st.button("🚀 REGISTRAR Y ANALIZAR"):
        # Determinar monto de apuesta basado en la última sugerencia
        apuesta_sug = max(2000, int(saldo_inicial * 0.05)) # Mínimo 2000 Gs o 5%
        if st.session_state.perdida_acumulada > 0:
            apuesta_sug = int(st.session_state.perdida_acumulada * 2)

        st.session_state.historial.append(vuelo_in)
        
        if apostaste == "SÍ, aposté":
            if vuelo_in >= 1.50: # Si alcanzó el target mínimo de la estrategia
                st.session_state.ganancia_total += (apuesta_sug * 0.5)
                st.session_state.perdida_acumulada = 0
            else:
                st.session_state.perdida_acumulada += apuesta_sug
        st.rerun()

# 7. Cuadro de Señal Visual
msg, target, conf, tipo = analizar_py(st.session_state.historial)

if tipo == "success":
    st.markdown(f"""
        <div class="bet-signal">
            <h1 style='margin:0;'>{msg}</h1>
            <p style='font-size: 22px; margin:0;'>Confianza: {conf}% | Salida sugerida: {target}x</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Cálculo de monto para Paraguay
    monto = max(2000, int(saldo_inicial * 0.05))
    if st.session_state.perdida_acumulada > 0:
        monto = int(st.session_state.perdida_acumulada * 2)
        
    st.info(f"💰 **APUESTA RECOMENDADA:** {monto:,} Gs.")
else:
    if tipo == "error": st.error(f"### {msg}")
    elif tipo == "warning": st.warning(f"### {msg}")
    else: st.info(f"### {msg}")

# 8. Gráfico de Historial
if st.session_state.historial:
    st.line_chart(st.session_state.historial[-15:])
