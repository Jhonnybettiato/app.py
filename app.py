import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v2.8", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #e91e63; color: white; border-radius: 10px; font-weight: bold; height: 3.5em; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .rosa-signal { background-color: #a21caf; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #f0abfc; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización (Historial extendido a 50)
if 'historial' not in st.session_state: st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🇵🇾 Panel v2.8")
    with st.expander("💰 Banca", expanded=True):
        saldo_inicial = st.number_input("Saldo en Gs.", min_value=0, value=10000, step=1000)
    
    st.header("🎯 Estrategia")
    modo_juego = st.selectbox("Estilo:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"])
    
    if st.button("🔄 Reiniciar Todo"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0
        st.session_state.ganancia_total = 0
        st.rerun()

# --- LÓGICA DE ANÁLISIS ---
def motor_analisis(h, modo):
    if len(h) < 3: return "Esperando más datos...", 0, "info"
    ultimos = h[-3:]
    
    # Contador de vuelos desde el último rosa (10x)
    vuelos_desde_rosa = 0
    for v in reversed(h):
        if v >= 10: break
        vuelos_desde_rosa += 1

    if modo == "Conservadora (1.50x)":
        if all(x < 1.30 for x in ultimos): return "🛑 Riesgo: Racha Baja", 0, "error"
        if sum(ultimos)/3 > 1.8: return "🔥 SEÑAL: Entrar a 1.50x", 1.50, "success"
        return "⚖️ Buscando estabilidad...", 0, "info"
    else:
        if vuelos_desde_rosa > 15 and sum(ultimos)/3 > 1.5:
            return f"🌸 ALERTA ROSA: {vuelos_desde_rosa} vuelos sin 10x!", 10.0, "rosa"
        return f"⌛ Ciclo: {vuelos_desde_rosa} vuelos sin rosa.", 0, "info"

# --- INTERFAZ PRINCIPAL ---
saldo_actual = saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada
c1, c2, c3 = st.columns(3)
c1.metric("Saldo Actual", f"{saldo_actual:,} Gs")
c2.metric("Ganancia Neta", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("Deuda Actual", f"{int(st.session_state.perdida_acumulada):,} Gs")

st.markdown("---")

# --- FORMULARIO DE REGISTRO (Habilita el ENTER) ---
with st.form("registro_vuelo", clear_on_submit=True):
    st.subheader("📥 Registro de Vuelo (Presiona Enter para enviar)")
    vuelo_in = st.number_input("Resultado del avión:", min_value=1.0, step=0.01, format="%.2f")
    apostaste = st.checkbox("¿Aposté dinero real en esta ronda?")
    
    # El botón 'submit' dentro del form es el que responde al Enter
    btn_submit = st.form_submit_button("REGISTRAR VUELO")

if btn_submit:
    # Guardamos en el historial (Limitado a los últimos 50 para no ralentizar)
    st.session_state.historial.append(vuelo_in)
    if len(st.session_state.historial) > 50:
        st.session_state.historial.pop(0)
    
    if apostaste:
        target = 1.50 if modo_juego == "Conservadora (1.50x)" else 10.0
        apuesta_base = max(2000, int(saldo_inicial * 0.05))
        
        if vuelo_in >= target:
            st.session_state.ganancia_total += (apuesta_base * (target - 1))
            st.session_state.perdida_acumulada = 0
            st.balloons()
        else:
            st.session_state.perdida_acumulada += apuesta_base
    st.rerun()

# --- SEÑAL Y GRÁFICO ---
msg, target, tipo = motor_analisis(st.session_state.historial, modo_juego)

if tipo == "success": st.success(f"### {msg}")
elif tipo == "rosa": st.markdown(f'<div class="rosa-signal"><h2>{msg}</h2></div>', unsafe_allow_html=True)
elif tipo == "error": st.error(f"### {msg}")
else: st.info(f"### {msg}")

# Gráfico de 50 vuelos
if st.session_state.historial:
    st.write(f"### Historial de Tendencia (Últimos {len(st.session_state.historial)} vuelos)")
    st.line_chart(st.session_state.historial)
    
    # Tabla rápida de los últimos 5 resultados
    st.write("Últimos resultados:", st.session_state.historial[-5:])
