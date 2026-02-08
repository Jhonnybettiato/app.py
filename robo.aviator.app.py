import streamlit as st
from datetime import datetime
import pytz
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite Robot v9.6.6", page_icon="🦅", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-header { color: #FFFFFF; font-size: 2.2rem; font-weight: 900; text-align: center; padding: 10px; text-transform: uppercase; letter-spacing: 3px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .elite-card { background-color: #121212; padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #333; height: 100%; }
    .label-elite { color: #888 !important; font-weight: 800; text-transform: uppercase; font-size: 0.7rem; margin-bottom: 5px; }
    .valor-elite { color: #FFFFFF !important; font-size: 1.8rem; font-weight: 900; margin: 0; }
    .win-box { background-color: #003311; border: 2px solid #00ff41; padding: 15px; border-radius: 15px; text-align: center; }
    .loss-box { background-color: #330000; border: 2px solid #ff3131; padding: 15px; border-radius: 15px; text-align: center; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #2ecc71; } 50% { box-shadow: 0 0 30px #2ecc71; } 100% { box-shadow: 0 0 5px #2ecc71; } }
    .semaforo { padding: 25px; border-radius: 20px; text-align: center; margin: 15px 0; transition: 0.3s; }
    .fuego { animation: pulse 1s infinite; border: 2px solid #fff; }
    .semaforo-txt { font-size: 1.8rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { min-width: 65px; height: 60px; border-radius: 30px; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; margin-right: 6px; font-size: 0.95rem; flex-shrink: 0; }
    
    /* Resaltado para saber dónde está el foco */
    input:focus { border: 2px solid #00ff41 !important; box-shadow: 0 0 15px #00ff41 !important; }
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

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ AJUSTES PRO")
    st.session_state.cap_ini = st.number_input("Capital Inicial", value=int(st.session_state.cap_ini), step=5000)
    
    st.divider()
    st.markdown("### 🕒 HORARIOS")
    st.session_state.h_10x = st.text_input("Editar 10x", value=st.session_state.h_10x)
    st.session_state.h_100x = st.text_input("Editar 100x", value=st.session_state.h_100x)
    
    if st.button("🔄 RESET COMPLETO"):
        st.session_state.clear()
        st.rerun()

# --- LÓGICA ---
def get_mins(h_str):
    if "---" in h_str or ":" not in h_str or h_str == "00:00": return "?"
    try:
        ahora = datetime.now(py_tz)
        h_f = py_tz.localize(datetime.strptime(h_str, "%H:%M").replace(year=ahora.year, month=ahora.month, day=ahora.day))
        d = int((ahora - h_f).total_seconds() / 60)
        return d if d >= 0 else (d + 1440)
    except: return "?"

def registrar():
    curr_key = f"input_{st.session_state.key_id}"
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
            
            # Incrementar Key para limpiar y forzar nuevo render
            st.session_state.key_id += 1
        except: pass

# Cálculo estrategia
sin_rosa = 0
if st.session_state.historial:
    for v in reversed(st.session_state.historial):
        if v >= 10.0: break
        sin_rosa += 1

# --- INTERFAZ ---
st.markdown('<div class="main-header">🦅 AVIATOR ELITE ROBOT v9.6.6</div>', unsafe_allow_html=True)

c = st.columns(4)
c[0].markdown(f'<div class="elite-card"><p class="label-elite">SALDO</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,}</h2></div>', unsafe_allow_html=True)
res_ac = st.session_state.saldo_dinamico - st.session_state.cap_ini
cl_res = "win-box" if res_ac >= 0 else "loss-box"
c[1].markdown(f'<div class="{cl_res}"><p class="label-elite">RESULTADO</p><h2 class="valor-elite">{int(res_ac):,}</h2></div>', unsafe_allow_html=True)
c[2].markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 10X</p><h2 class="valor-elite">{st.session_state.h_10x}</h2><p style="color:#0f4;font-size:0.7rem;margin:0;">⏱️ {get_mins(st.session_state.h_10x)} min</p></div>', unsafe_allow_html=True)
c[3].markdown(f'<div class="elite-card"><p class="label-elite">ÚLTIMA 100X</p><h2 class="valor-elite">{st.session_state.h_100x}</h2><p style="color:#0f4;font-size:0.7rem;margin:0;">⏱️ {get_mins(st.session_state.h_100x)} min</p></div>', unsafe_allow_html=True)

# Semáforo
if sin_rosa >= 30: t, col, anim = "🔥 ENTRAR AHORA", "#27ae60", "fuego"
elif sin_rosa >= 25: t, col, anim = "🟡 PREPARAR", "#f39c12", ""
else: t, col, anim = f"⏳ ESPERAR ({sin_rosa}/30)", "#333", ""
st.markdown(f'<div class="semaforo {anim}" style="background-color:{col};"><p class="semaforo-txt">{t}</p></div>', unsafe_allow_html=True)

# Entrada
st.markdown('<div class="elite-card">', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
with r1:
    # INPUT CON KEY DINÁMICA
    st.text_input("VALOR DEL VUELO", value="", placeholder="Escribe aquí...", 
                  key=f"input_{st.session_state.key_id}", on_change=registrar)
with r2: st.number_input("APUESTA Gs.", value=2000, step=1000, key="in_apuesta")
with r3: st.write("##"); st.checkbox("¿APOSTÉ?", key="in_chk")
with r4: st.write("##"); st.button("REGISTRAR 🚀", on_click=registrar, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- EL TRUCO DEL FOCO (JAVASCRIPT) ---
components.html(f"""
    <script>
    var input = window.parent.document.querySelector('input[aria-label="VALOR DEL VUELO"]');
    if (input) {{
        input.focus();
    }}
    </script>
    """, height=0)

# Historial
if st.session_state.historial:
    h_h = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.2f}</div>' for v in reversed(st.session_state.historial[-15:])])
    st.markdown(f'<div style="display:flex; overflow-x:auto; padding:15px; background:#111; border-radius:20px; border: 1px solid #333; margin-top:20px;">{h_h}</div>', unsafe_allow_html=True)

if st.button("🔙 DESHACER ÚLTIMA"):
    if st.session_state.historial:
        st.session_state.historial.pop()
        st.session_state.saldo_dinamico -= st.session_state.registro_saldos.pop()
        st.rerun()
