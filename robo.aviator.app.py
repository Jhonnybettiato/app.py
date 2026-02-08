import streamlit as st
from datetime import datetime
import pytz
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.7.2", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; text-transform: uppercase; letter-spacing: 3px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; height: 100%; }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; display: flex; align-items: center; justify-content: center; gap: 5px; margin-bottom: 5px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; margin-bottom: 0px; }
    .cronometro { color: #00ff41; font-family: monospace; font-size: 0.9rem; font-weight: bold; margin-top: 5px; }
    
    input:focus { 
        border: 2px solid #00ff41 !important; 
        box-shadow: 0 0 15px #00ff41 !important;
        background-color: #050505 !important;
    }

    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Estados
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 475000.0
if 'h_10x' not in st.session_state: st.session_state.h_10x = "00:00"
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"
if 'key_id' not in st.session_state: st.session_state.key_id = 0
if 'cap_ini' not in st.session_state: st.session_state.cap_ini = 475000.0

# --- FUNCIONES DE TIEMPO ---
def calcular_cronometro(hora_str):
    if hora_str == "---" or hora_str == "00:00":
        return "00m 00s"
    try:
        ahora = datetime.now(py_tz)
        # Convertir HH:MM a objeto datetime del día de hoy
        hora_obj = datetime.strptime(hora_str, "%H:%M")
        hora_final = ahora.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0, microsecond=0)
        
        # Si la hora registrada es mayor a la actual, asumimos que fue del día anterior (o error de input)
        # pero para el robot usualmente trabajamos en el ciclo actual
        diferencia = ahora - hora_final
        total_segundos = int(diferencia.total_seconds())
        
        if total_segundos < 0: # Caso de cambio de día
            total_segundos += 86400
            
        minutos = total_segundos // 60
        segundos = total_segundos % 60
        return f"{minutos:02d}m {segundos:02d}s"
    except:
        return "error"

# --- LÓGICA DE REGISTRO ---
def registrar():
    curr_key = f"input_{st.session_state.key_id}"
    if curr_key in st.session_state:
        raw = st.session_state[curr_key].replace(',', '.')
        if raw:
            try:
                val = float(raw)
                apuesta = st.session_state.in_apuesta
                jugado = st.session_state.in_chk
                gan = (apuesta * 9) if (jugado and val >= 10.0) else (-float(apuesta) if jugado else 0.0)
                
                st.session_state.historial.append(val)
                st.session_state.registro_saldos.append(gan)
                st.session_state.saldo_dinamico += gan
                
                ahora_f = datetime.now(py_tz).strftime("%H:%M")
                if val >= 10.0: st.session_state.h_10x = ahora_f
                if val >= 100.0: st.session_state.h_100x = ahora_f
                
                st.session_state.key_id += 1
            except: pass

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTES")
    
    # Usamos una key diferente para el widget
    nuevo_cap = st.number_input("Capital Inicial", 
                                value=float(st.session_state.cap_ini),
                                step=1000.0,
                                key="input_cap_ini")
    
    # Si el valor del widget cambia, actualizamos el capital y recalculamos saldo
    if nuevo_cap != st.session_state.cap_ini:
        diferencia = nuevo_cap - st.session_state.cap_ini
        st.session_state.cap_ini = nuevo_cap
        st.session_state.saldo_dinamico += diferencia
        st.rerun()

    st.session_state.h_10x = st.text_input("Hora 10x", value=st.session_state.h_10x)
    st.session_state.h_100x = st.text_input("Hora 100x", value=st.session_state.h_100x)
    
    if st.button("🔄 REINICIAR"):
        # Limpiamos todo excepto el capital inicial si quieres mantenerlo
        st.session_state.clear()
        st.rerun()

# --- INTERFAZ ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE ROBOT v9.7.2</div>', unsafe_allow_html=True)

# Dashboard de métricas
c1, c2, c3, c4 = st.columns(4)
res_ac = st.session_state.saldo_dinamico - st.session_state.cap_ini

c1.markdown(f'<div class="elite-card"><p class="label-elite">💰 SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="elite-card" style="border-color:{"#0f4" if res_ac >=0 else "#f31"};"><p class="label-elite">📈 GANANCIA</p><h2 class="valor-elite">{int(res_ac):,}</h2></div>', unsafe_allow_html=True)

# Tarjeta 10x con CRONÓMETRO
c3.markdown(f"""
    <div class="elite-card">
        <p class="label-elite">✈️ ÚLTIMA 10X</p>
        <h2 class="valor-elite" style="color:#9b59b6 !important;">{st.session_state.h_10x}</h2>
        <p class="cronometro">⏱️ hace {calcular_cronometro(st.session_state.h_10x)}</p>
    </div>
""", unsafe_allow_html=True)

# Tarjeta 100x con CRONÓMETRO
c4.markdown(f"""
    <div class="elite-card">
        <p class="label-elite">🚀 ÚLTIMA 100X</p>
        <h2 class="valor-elite" style="color:#e91e63 !important;">{st.session_state.h_100x}</h2>
        <p class="cronometro">⏱️ hace {calcular_cronometro(st.session_state.h_100x)}</p>
    </div>
""", unsafe_allow_html=True)

# --- SEMÁFORO DE ESTRATEGIA (RONDAS SIN ROSA) ---
sin_rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10.0: break
    sin_rosa += 1

# Lógica de colores y mensajes
if sin_rosa <= 20:
    color_semaforo = "#ff4b4b"  # Rojo
    mensaje_accion = "🚫 ESPERAR - ZONA DE RIESGO"
    texto_color = "white"
elif 21 <= sin_rosa <= 30:
    color_semaforo = "#ffeb3b"  # Amarillo
    mensaje_accion = "⚠️ ANALIZANDO - POSIBLE ENTRADA"
    texto_color = "black"
elif 31 <= sin_rosa <= 40:
    color_semaforo = "#00ff41"  # Verde
    mensaje_accion = "🚀 ENTRADA CONFIRMADA - ¡VUELO ELITE!"
    texto_color = "black"
else:
    color_semaforo = "#9b59b6"  # Púrpura (Exceso de rondas)
    mensaje_accion = "🔥 ALERTA MÁXIMA - PATRÓN EXTENDIDO"
    texto_color = "white"

st.markdown(f"""
    <div style="
        background-color: {color_semaforo}; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 15px; 
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0px 4px 15px {color_semaforo}66;
    ">
        <h2 style="color: {texto_color}; margin: 0; font-weight: 900; letter-spacing: 1px;">
            RONDAS SIN ROSA: {sin_rosa}
        </h2>
        <h4 style="color: {texto_color}; margin: 5px 0 0 0; opacity: 0.9; font-weight: 700;">
            {mensaje_accion}
        </h4>
    </div>
""", unsafe_allow_html=True)

# PANEL DE ENTRADA
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns([2, 1, 1, 1])

with r1:
    st.text_input("VALOR DEL VUELO", value="", key=f"input_{st.session_state.key_id}", 
                  on_change=registrar, placeholder="INGRESE VALOR")

with r2: st.number_input("APUESTA", value=2000, key="in_apuesta")
with r3: st.write("##"); st.checkbox("¿APOSTÉ?", key="in_chk")
with r4: st.write("##"); st.button("REGISTRAR 🚀", on_click=registrar)
st.markdown('</div>', unsafe_allow_html=True)

# --- INYECTOR DE FOCO ---
components.html(f"""
    <script>
    function setFocus() {{
        var inputs = window.parent.document.querySelectorAll('input[placeholder="INGRESE VALOR"]');
        if (inputs.length > 0) {{
            inputs[0].focus();
        }}
    }}
    setFocus();
    setTimeout(setFocus, 300);
    </script>
    """, height=0)

# Historial
if st.session_state.historial:
    h_h = "".join([f'<div class="burbuja" style="background-color:{"#e91e63" if v >= 10 else "#9b59b6" if v >= 2 else "#3498db"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:20px;">{h_h}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.rerun()
