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

# --- 8. HISTORIAL ESTILO AVIATOR (NUEVO) ---
st.markdown("---")
st.subheader("📊 Historial Reciente (Estilo Aviator)")

if st.session_state.historial:
    # Creamos una fila de burbujas (mostramos las últimas 15)
    cols = st.columns(15)
    ultimos_vuelos = list(reversed(st.session_state.historial))[:15]
    
    for i, valor in enumerate(ultimos_vuelos):
        if i < len(cols):
            # Determinar color según el multiplicador
            if valor < 2.0:
                bg_color = "#3498db" # Azul
                text_color = "white"
            elif valor < 10.0:
                bg_color = "#9b59b6" # Morado
                text_color = "white"
            else:
                bg_color = "#e91e63" # Rosa
                text_color = "white"
            
            with cols[i]:
                st.markdown(f"""
                    <div style="
                        background-color: {bg_color};
                        color: {text_color};
                        border-radius: 50%;
                        width: 45px;
                        height: 45px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 12px;
                        margin-bottom: 10px;
                        border: 2px solid rgba(255,255,255,0.2);
                        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
                    ">
                        {valor:.2f}x
                    </div>
                """, unsafe_allow_html=True)

# --- 9. GRÁFICO DE TENDENCIA LARGA ---
if st.session_state.historial:
    with st.expander("📈 Ver Gráfico de Tendencia Completo (50 vuelos)"):
        st.line_chart(st.session_state.historial)
