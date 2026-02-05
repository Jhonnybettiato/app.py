import streamlit as st
import pandas as pd

# 1. Configuración y Estilo
st.set_page_config(page_title="Aviator Pro", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #e91e63; color: white; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 Aviator Estratega v2.1")

# 2. Memoria de la sesión
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state:
    st.session_state.perdida_acumulada = 0.0

# 3. Barra Lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    saldo = st.number_input("Saldo", min_value=0.0, value=100.0)
    if st.button("Resetear Todo"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0.0
        st.rerun()

# 4. Lógica
def analizar(h):
    if len(h) < 3: return "Esperando datos...", 1.20, "info"
    ult = h[-3:]
    if all(x < 1.40 for x in ult): return "🛑 RIESGO: Racha baja", 0, "error"
    if ult[-1] > 8.0: return "📉 ESPERA: Salió rosa", 0, "warning"
    if sum(ult)/3 > 1.8: return "🎯 SEÑAL: Entrar ahora", 1.50, "success"
    return "⚖️ Monitoreando...", 1.25, "info"

# 5. Interfaz
col1, col2 = st.columns(2)
col1.metric("Saldo", f"{saldo:.2f}")
col2.metric("Pérdida a recuperar", f"{st.session_state.perdida_acumulada:.2f}")

valor = st.number_input("Último vuelo:", min_value=1.0, step=0.01)
if st.button("Registrar Vuelo"):
    st.session_state.historial.append(valor)
    st.rerun()

msg, cash, tipo = analizar(st.session_state.historial)

if tipo == "success":
    st.success(msg)
    apuesta = max(saldo * 0.02, st.session_state.perdida_acumulada / 0.5)
    st.info(f"Apuesta: {apuesta:.2f} | Cobrar en: {cash}x")
    c1, c2 = st.columns(2)
    if c1.button("✅ GANÉ"):
        st.session_state.perdida_acumulada = 0.0
        st.rerun()
    if c2.button("❌ PERDÍ"):
        st.session_state.perdida_acumulada += apuesta
        st.rerun()
elif tipo == "error": st.error(msg)
else: st.warning(msg)

if st.session_state.historial:
    st.line_chart(st.session_state.historial[-15:])
