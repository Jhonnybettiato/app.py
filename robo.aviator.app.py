import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.7.0", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; border-bottom: 2px solid #333; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; }
    .label-elite { color: #888; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; }
    .valor-elite { color: #FFFFFF; font-size: 1.8rem; font-weight: 900; }
    
    /* Resaltado de la caja activa */
    input:focus { 
        border: 3px solid #00ff41 !important; 
        box-shadow: 0 0 20px #00ff41 !important;
    }
    
    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización
py_tz = pytz.timezone('America/Asuncion')
if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo' not in st.session_state: st.session_state.saldo = 475000.0
if 'h_10x' not in st.session_state: st.session_state.h_10x = "00:00"
if 'h_100x' not in st.session_state: st.session_state.h_100x = "---"
if 'key_count' not in st.session_state: st.session_state.key_count = 0

# --- LÓGICA ---
def registrar():
    k = f"in_{st.session_state.key_count}"
    raw = st.session_state[k].replace(',', '.')
    if raw:
        try:
            val = float(raw)
            ap = st.session_state.in_apuesta
            jugo = st.session_state.in_chk
            gan = (ap * 9) if (jugo and val >= 10.0) else (-float(ap) if jugo else 0.0)
            
            st.session_state.historial.append(val)
            st.session_state.registro_saldos.append(gan)
            st.session_state.saldo += gan
            
            hora = datetime.now(py_tz).strftime("%H:%M")
            if val >= 10.0: st.session_state.h_10x = hora
            if val >= 100.0: st.session_state.h_100x = hora
            
            # Cambiamos la key para forzar el foco al refrescar
            st.session_state.key_count += 1
        except: pass

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("CONFIG")
    st.session_state.h_10x = st.text_input("Hora 10x", value=st.session_state.h_10x)
    st.session_state.h_100x = st.text_input("Hora 100x", value=st.session_state.h_100x)
    if st.button("RESET"):
        st.session_state.clear()
        st.rerun()

# --- INTERFAZ ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE v9.7.0</div>', unsafe_allow_html=True)

# 1. Dashboard de Métricas
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="elite-card"><p class="label-elite">SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="elite-card"><p class="label-elite">10X</p><h2 class="valor-elite">{st.session_state.h_10x}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="elite-card"><p class="label-elite">100X</p><h2 class="valor-elite">{st.session_state.h_100x}</h2></div>', unsafe_allow_html=True)
# Conteo
rosa = 0
for v in reversed(st.session_state.historial):
    if v >= 10.0: break
    rosa += 1
c4.markdown(f'<div class="elite-card"><p class="label-elite">RONDAS SIN ROSA</p><h2 class="valor-elite">{rosa}</h2></div>', unsafe_allow_html=True)

# 2. PANEL DE ENTRADA (MOVIDO ARRIBA PARA PRIORIDAD)
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3 = st.columns([2, 1, 1])
with r1:
    # autofocus=True le dice al navegador: "esta es la caja importante"
    st.text_input(
        "VALOR DEL VUELO", 
        value="", 
        key=f"in_{st.session_state.key_count}", 
        on_change=registrar,
        placeholder="Escribe aquí..."
    )
with r2: st.number_input("APUESTA", value=2000, key="in_apuesta")
with r3: st.write("##"); st.checkbox("¿APOSTÉ?", key="in_chk")
st.markdown('</div>', unsafe_allow_html=True)

# 3. Historial de burbujas
if st.session_state.historial:
    h_h = "".join([f'<div class="burbuja" style="background-color:{"#e91e63" if v >= 10 else "#9b59b6" if v >= 2 else "#3498db"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:20px;">{h_h}</div>', unsafe_allow_html=True)

# 4. Inyección de JavaScript (Último recurso)
st.components.v1.html(f"""
    <script>
    var input = window.parent.document.querySelector('input[aria-label="VALOR DEL VUELO"]');
    input.focus();
    </script>
    """, height=0)
