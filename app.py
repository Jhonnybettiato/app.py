import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Aviator Smart Strategy", page_icon="🦅")

st.title("🦅 Aviator Estratega v2.0")
st.markdown("---")

# --- BARRA LATERAL (Configuración) ---
st.sidebar.header("💰 Configuración de Banca")
saldo_actual = st.sidebar.number_input("Saldo Actual (Gs/USD)", min_value=0.0, value=100.0)
meta_ganancia = st.sidebar.slider("Meta de Ganancia (%)", 10, 100, 20)
meta_final = saldo_actual * (1 + meta_ganancia/100)

# --- ESTADO DE LA SESIÓN ---
if 'historial' not in st.session_state:
    st.session_state.historial = []
if 'perdida_acumulada' not in st.session_state:
    st.session_state.perdida_acumulada = 0.0

# --- LÓGICA DE ESTRATEGIA ---
def analizar_racha(h):
    if len(h) < 3: return "Esperando datos...", 1.20, "info"
    ultimos = h[-3:]
    if all(x < 1.50 for x in ultimos):
        return "⚠️ ALERTA: Racha fría. NO APOSTAR.", 0, "error"
    if ultimos[-1] > 10.0:
        return "📉 AVISO: Rosa alto. Espera 2 rondas.", 0, "warning"
    if sum(ultimos)/3 > 2.0:
        return "✅ SEÑAL: Racha estable.", 1.50, "success"
    return "🔍 ESTADO: Mercado lento.", 1.20, "info"

# --- INTERFAZ PRINCIPAL ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Saldo", f"{saldo_actual:.2f}")
with col2:
    st.metric("Meta", f"{meta_final:.2f}")

# Entrada de datos
nuevo_valor = st.number_input("Resultado del último avión:", min_value=1.0, step=0.1, key="input_aviao")
btn_add = st.button("Registrar Vuelo")

if btn_add:
    st.session_state.historial.append(nuevo_valor)
    # Lógica de limpieza de pérdida si el vuelo fue exitoso
    # (Aquí podrías añadir más lógica personalizada)

# --- RESULTADO DE ESTRATEGIA ---
msg, sugerencia, tipo = analizar_racha(st.session_state.historial)

if tipo == "success":
    st.success(msg)
    apuesta = max(saldo_actual * 0.02, st.session_state.perdida_acumulada * 2)
    st.write(f"### 💸 Apuesta Recomendada: **{apuesta:.2f}**")
    st.write(f"### 🎯 Auto Cashout: **{sugerencia}x**")
elif tipo == "error":
    st.error(msg)
else:
    st.info(msg)

# Mostrar Historial
if st.session_state.historial:
    st.write("### Historial Reciente")
    st.line_chart(st.session_state.historial[-10:])
