import streamlit as st
import pandas as pd

# 1. Configuración de página y Estilo Dark
st.set_page_config(page_title="Aviator Pro Strategy", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        background-color: #e91e63;
        color: white;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Título e Intro
st.title("🦅 Aviator Estratega v2.1")
st.caption("Panel de Control Inteligente para Gestión de Riesgos")

# 3. Estado de la Sesión (Memoria del programa)
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state:
    st.session_state.perdida_acumulada = 0.0

# 4. Barra Lateral de Configuración
with st.sidebar:
    st.header("⚙️ Parámetros")
    saldo_actual = st.number_input("Saldo Total Disponible", min_value=0.0, value=100.0, step=10.0)
    meta_ganancia = st.slider("Meta de Beneficio (%)", 5, 100, 20)
    meta_final = saldo_actual * (1 + meta_ganancia/100)
    
    if st.button("Resetear Sesión"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0.0
        st.rerun()

# 5. Funciones de Lógica
def analizar_estrategia(h):
    if len(h) < 3: return "Iniciando análisis...", 1.20, "info"
    ultimos = h[-3:]
    # Lógica de racha fría
    if all(x < 1.40 for x in ultimos):
        return "🛑 RIESGO ALTO: Racha de multiplicadores bajos. ¡No entres!", 0, "error"
    # Lógica de aviso tras rosa
    if ultimos[-1] > 8.0:
        return "📉 ENFRIAMIENTO: Salió un rosa alto. Espera 1 o 2 vuelos.", 0, "warning"
    # Lógica de oportunidad
    if sum(ultimos)/3 > 1.8:
        return "🎯 OPORTUNIDAD: Racha estable detectada.", 1.50, "success"
    return "⚖️ MERCADO NEUTRAL: Monitoreando...", 1.25, "info"

# 6. Panel Principal de Métricas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Saldo Actual", f"{saldo_actual:.2f}")
with col2:
    st.metric("Objetivo", f"{meta_final:.2f}")
with col3:
    st.metric("Deuda/Pérdida", f"{st.session_state.perdida_acumulada:.2f}", delta_color="inverse")

st.markdown("---")

# 7. Entrada de Datos y Acción
c1, c2 = st.columns([2, 1])
with c1:
    nuevo_valor = st.number_input("Registrar último multiplicador (Ej: 2.54):", min_value=1.0, step=0.01, format="%.2f")
with c2:
    st.write("##") # Espaciador
    if st.button("Añadir al Historial"):
        st.session_state.historial.append(nuevo_valor)
        st.rerun()

# 8. Recomendación del Algoritmo
msg, cashout, tipo = analizar_estrategia(st.session_state.historial)

if tipo == "success":
    st.success(f"### {msg}")
    # Cálculo de apuesta: 2% del saldo o recuperación
    base = saldo_actual * 0.02
    if st.session_state.perdida_acumulada > 0:
        apuesta = st.session_state.perdida_acumulada / (cashout - 1)
    else:
        apuesta = base
    
    st.info(f"💰 **Apuesta Recomendada:** {apuesta:.2f} | 🎯 **Auto-Cashout en:** {cashout}x")
    
    # Botones de control de apuesta real
    b1, b2 = st.columns(2)
    with b1:
        if st.button("✅ ¡GANÉ!"):
            st.session_state.perdida_acumulada = 0.0
            st.balloons()
            st.rerun()
    with b2:
        if st.button("❌ PER
