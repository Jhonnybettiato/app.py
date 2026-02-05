import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY", page_icon="🦅", layout="wide")

# Estilo CSS (Dark Mode + Animaciones)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #e91e63; color: white; border-radius: 10px; font-weight: bold; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .rosa-signal { 
        background-color: #a21caf; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        border: 2px solid #f0abfc;
        animation: pulse 1s infinite;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
if 'historial' not in st.session_state: st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🇵🇾 Panel de Control")
    
    # SECCIÓN 1: AJUSTE DE BANCA
    with st.expander("💰 Ajuste de Banca", expanded=True):
        saldo_inicial = st.number_input("Saldo en Gs.", min_value=0, value=10000, step=1000)
    
    # SECCIÓN 2: ESTRATEGIA (Lo nuevo)
    st.markdown("---")
    st.header("🎯 Estrategia")
    modo_juego = st.selectbox(
        "Selecciona tu estilo:",
        ["Conservadora (1.50x)", "Cazador de Rosas (10x)"]
    )
    
    st.markdown("---")
    if st.button("🔄 Reiniciar Datos"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0
        st.session_state.ganancia_total = 0
        st.rerun()

# --- LÓGICA DE ESTRATEGIAS ---
def motor_analisis(h, modo):
    if len(h) < 3: return "Recolectando datos...", 0, "info"
    
    ultimos = h[-3:]
    vuelos_desde_rosa = 0
    # Contar cuántos vuelos pasaron desde el último 10x
    for i, v in enumerate(reversed(h)):
        if v >= 10: break
        vuelos_desde_rosa += 1

    if modo == "Conservadora (1.50x)":
        promedio = sum(ultimos)/3
        if all(x < 1.30 for x in ultimos): return "🛑 Riesgo: Racha Baja", 0, "error"
        if promedio > 1.8: return "🔥 SEÑAL: Entrar a 1.50x", 1.50, "success"
        return "⚖️ Esperando estabilidad...", 0, "info"
    
    else: # MODO CAZADOR 10x
        # Si han pasado más de 15 vuelos sin un 10x y hay estabilidad
        if vuelos_desde_rosa > 15 and sum(ultimos)/3 > 1.5:
            return f"🌸 ALERTA ROSA: {vuelos_desde_rosa} vuelos sin 10x. ¡Momento de buscarlo!", 10.0, "rosa"
        return f"⌛ Analizando ciclo: {vuelos_desde_rosa} vuelos desde el último rosa.", 0, "info"

# --- INTERFAZ PRINCIPAL ---
st.title(f"🦅 Aviator Pro - Modo {modo_juego}")
saldo_actual = saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada

c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{saldo_actual:,} Gs")
c2.metric("Ganancia Hoy", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("Pérdida/Deuda", f"{int(st.session_state.perdida_acumulada):,} Gs")

st.markdown("---")

# Registro
col_v, col_a = st.columns(2)
with col_v:
    vuelo_in = st.number_input("Resultado del avión:", min_value=1.0, step=0.01)
with col_a:
    st.write("##")
    apostaste = st.checkbox("¿Aposté en esta ronda?")

if st.button("Registrar Vuelo"):
    st.session_state.historial.append(vuelo_in)
    if apostaste:
        # Lógica de cobro según el modo seleccionado
        target = 1.50 if modo_juego == "Conservadora (1.50x)" else 10.0
        apuesta_base = max(2000, int(saldo_inicial * 0.05))
        
        if vuelo_in >= target:
            st.session_state.ganancia_total += (apuesta_base * (target - 1))
            st.session_state.perdida_acumulada = 0
            st.balloons()
        else:
            st.session_state.perdida_acumulada += apuesta_base
    st.rerun()

# Señal Visual
msg, target, tipo = motor_analisis(st.session_state.historial, modo_juego)

if tipo == "success":
    st.success(f"### {msg}")
elif tipo == "rosa":
    st.markdown(f'<div class="rosa-signal"><h2>{msg}</h2><p>Busca el 10x con apuesta pequeña</p></div>', unsafe_allow_html=True)
elif tipo == "error":
    st.error(f"### {msg}")
else:
    st.info(f"### {msg}")

if st.session_state.historial:
    st.line_chart(st.session_state.historial[-20:])
