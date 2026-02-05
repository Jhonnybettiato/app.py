import streamlit as st
import pandas as pd

# 1. Configuración y Estilo Mejorado
st.set_page_config(page_title="Aviator Pro Elite", page_icon="🦅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #e91e63; color: white; border-radius: 10px; font-weight: bold; height: 3em; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .bet-signal { 
        background-color: #22c55e; 
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: bold;
        border: 2px solid #ffffff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Estado de la Sesión
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state:
    st.session_state.perdida_acumulada = 0.0
if 'ganancia_total' not in st.session_state:
    st.session_state.ganancia_total = 0.0

# 3. Barra Lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    saldo_inicial = st.number_input("Saldo Inicial", min_value=0.0, value=100.0)
    if st.button("Resetear Sesión"):
        st.session_state.historial = []
        st.session_state.perdida_acumulada = 0.0
        st.session_state.ganancia_total = 0.0
        st.rerun()

# 4. Lógica de Análisis
def analizar_avanzado(h):
    if len(h) < 3: return "Analizando patrones...", 1.20, 0, "info"
    ult = h[-3:]
    promedio = sum(ult)/3
    
    # Probabilidad de éxito basada en promedio
    confianza = min(int((promedio / 2.5) * 100), 95)
    
    if all(x < 1.40 for x in ult): return "🛑 RIESGO: Racha Baja", 0, 0, "error"
    if ult[-1] > 8.0: return "📉 ESPERA: Enfriamiento", 0, 0, "warning"
    if promedio > 1.8: return "🎯 ¡APUESTA AHORA!", 1.50, confianza, "success"
    
    return "⚖️ Monitoreando...", 1.25, 0, "info"

# 5. Interfaz Principal
st.title("🦅 Aviator Estratega v2.5")

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Saldo Real", f"{saldo_inicial + st.session_state.ganancia_total - st.session_state.perdida_acumulada:.2f}")
with col_m2:
    st.metric("Recuperación Pendiente", f"{st.session_state.perdida_acumulada:.2f}")
with col_m3:
    st.metric("Ganancia Neta", f"{st.session_state.ganancia_total:.2f}")

st.markdown("---")

# 6. Registro con Pregunta de Apuesta
with st.expander("📥 Registrar Último Vuelo", expanded=True):
    val_vuelo = st.number_input("Multiplicador del avión:", min_value=1.0, step=0.01, format="%.2f")
    opcion_apuesta = st.radio("¿Apostaste en esta ronda?", ["No, solo observando", "Sí, hice una apuesta"])
    
    if st.button("Confirmar y Analizar"):
        st.session_state.historial.append(val_vuelo)
        msg, cash, conf, tipo = analizar_avanzado(st.session_state.historial)
        
        # Si apostó, calcular resultado financiero
        if opcion_apuesta == "Sí, hice una apuesta":
            # Necesitamos saber cuánto apostó (usamos la sugerencia anterior)
            apuesta_previa = max(saldo_inicial * 0.02, st.session_state.perdida_acumulada / 0.5)
            if val_vuelo >= 1.50: # Asumimos el target de la estrategia
                st.session_state.ganancia_total += (apuesta_previa * 0.5)
                st.session_state.perdida_acumulada = 0.0
                st.balloons()
            else:
                st.session_state.perdida_acumulada += apuesta_previa
        st.rerun()

# 7. Cuadro de Señal de Apuesta
msg, cash, conf, tipo = analizar_avanzado(st.session_state.historial)

if tipo == "success":
    st.markdown(f"""
        <div class="bet-signal">
            <h1>{msg}</h1>
            <p style='font-size: 24px;'>Confianza: {conf}% | Objetivo: {cash}x</p>
        </div>
    """, unsafe_allow_html=True)
    
    apuesta_sug = max(saldo_inicial * 0.02, st.session_state.perdida_acumulada / 0.5)
    st.info(f"💰 **Monto sugerido para apostar:** {apuesta_sug:.2f}")
else:
    if tipo == "error": st.error(f"### {msg}")
    elif tipo == "warning": st.warning(f"### {msg}")
    else: st.info(f"### {msg}")

# 8. Gráfico
if st.session_state.historial:
    st.line_chart(st.session_state.historial[-20:])
