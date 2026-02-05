import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v3.1", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #e91e63; color: white; border-radius: 10px; font-weight: bold; height: 3.5em; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .rosa-signal { background-color: #a21caf; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #f0abfc; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estado
if 'historial' not in st.session_state: st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state: st.session_state.perdida_acumulada = 0
if 'ganancia_total' not in st.session_state: st.session_state.ganancia_total = 0

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🇵🇾 Panel de Control")
    saldo_inicial = st.number_input("Saldo Inicial Gs.", min_value=0, value=50000, step=5000)
    modo_juego = st.selectbox("Estrategia:", ["Conservadora (1.50x)", "Cazador de Rosas (10x)"])
    if st.button("🔄 Reiniciar"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0
        st.session_state.ganancia_total = 0
        st.rerun()

# --- LÓGICA DE ANÁLISIS ---
def motor_analisis(h, modo):
    if len(h) < 3: return "Esperando datos...", 0, "info"
    ultimos = h[-3:]
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
c1.metric("Saldo Actual", f"{int(saldo_actual):,} Gs")
c2.metric("Ganancia", f"{int(st.session_state.ganancia_total):,} Gs")
c3.metric("Deuda", f"{int(st.session_state.perdida_acumulada):,} Gs")

st.markdown("---")

# --- REGISTRO DE VUELO (NUEVA LÓGICA SIN FORM PARA EVITAR ERRORES) ---
st.subheader("📥 Registro de Vuelo")
col_input, col_check = st.columns([2, 1])

with col_input:
    # Usamos text_input para asegurar que el Enter siempre dispare la acción
    vuelo_str = st.text_input("Multiplicador (ej: 2.50) y presiona ENTER:", key="input_vuelo_txt")

with col_check:
    st.write("##") # Espaciador
    apostaste = st.checkbox("¿Aposté en esta ronda?", key="check_apuesta")

# Función para procesar el registro
if vuelo_str:
    try:
        vuelo_val = float(vuelo_str.replace(',', '.'))
        # Añadir al historial
        st.session_state.historial.append(vuelo_val)
        if len(st.session_state.historial) > 50:
            st.session_state.historial.pop(0)
        
        # Procesar apuesta si marcó el check
        if apostaste:
            target = 1.50 if modo_juego == "Conservadora (1.50x)" else 10.0
            apuesta_base = max(2000, int(saldo_inicial * 0.05))
            if vuelo_val >= target:
                st.session_state.ganancia_total += (apuesta_base * (target - 1))
                st.session_state.perdida_acumulada = 0
                st.balloons()
            else:
                st.session_state.perdida_acumulada += apuesta_base
        
        # Limpiar el input y refrescar
        st.session_state.input_vuelo_txt = "" # Intentar limpiar para el siguiente
        st.rerun()
    except ValueError:
        st.error("Por favor, ingresa un número válido (ej: 1.55)")

# --- SEÑAL Y BURBUJAS ---
msg, target, tipo = motor_analisis(st.session_state.historial, modo_juego)
if tipo == "success": st.success(f"### {msg}")
elif tipo == "rosa": st.markdown(f'<div class="rosa-signal"><h2>{msg}</h2></div>', unsafe_allow_html=True)
elif tipo == "error": st.error(f"### {msg}")
else: st.info(f"### {msg}")

st.subheader("📊 Historial Reciente")
if st.session_state.historial:
    ultimos_vuelos = list(reversed(st.session_state.historial))[:15]
    cols = st.columns(15)
    for i, valor in enumerate(ultimos_vuelos):
        if i < len(cols):
            color = "#3498db" if valor < 2.0 else "#9b59b6" if valor < 10.0 else "#e91e63"
            with cols[i]:
                st.markdown(f"""<div style="background-color:{color}; color:white; border-radius:50%; width:45px; height:45px; 
                display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:11px;
                border:2px solid rgba(255,255,255,0.2); box-shadow:0px 4px 6px rgba(0,0,0,0.3);">{valor:.2f}</div>""", unsafe_allow_html=True)

with st.expander("📈 Gráfico de Tendencia"):
    if st.session_state.historial:
        st.line_chart(st.session_state.historial)
