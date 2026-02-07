import streamlit as st
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(page_title="Aviator Elite PY v8.7", page_icon="🦅", layout="wide")

# --- DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .elite-card { 
        background-color: #121212; padding: 20px; border-radius: 15px; 
        text-align: center; margin-bottom: 10px; border: 1px solid #333;
    }
    .label-elite { color: #FFFFFF !important; font-weight: 800; text-transform: uppercase; font-size: 0.8rem; }
    .valor-elite { color: #FFFFFF !important; font-size: 2.2rem; font-weight: 900; }
    .semaforo-box { padding: 30px; border-radius: 20px; text-align: center; margin-top: 10px; }
    .semaforo-texto { font-size: 2rem; font-weight: 900; color: white; margin: 0; }
    .burbuja { min-width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialización de Sesión
py_tz = pytz.timezone('America/Asuncion')
now_str = datetime.now(py_tz).strftime("%H:%M")

if 'historial' not in st.session_state: st.session_state.historial = []
if 'registro_saldos' not in st.session_state: st.session_state.registro_saldos = []
if 'saldo_dinamico' not in st.session_state: st.session_state.saldo_dinamico = 0.0
if 'primer_inicio' not in st.session_state: st.session_state.primer_inicio = True
if 'h_10x_input' not in st.session_state: st.session_state.h_10x_input = now_str
if 'h_100x_input' not in st.session_state: st.session_state.h_100x_input = "---"

# --- FUNCIONES DE ACCIÓN ---
def registrar_valor():
    if st.session_state.entrada_manual:
        try:
            v_val = float(str(st.session_state.entrada_manual).replace(',', '.'))
            
            # Calcular impacto ANTES de guardar
            impacto = 0.0
            if st.session_state.check_apuesta:
                ap = float(st.session_state.valor_apuesta_manual)
                est = st.session_state.modo_sel
                # Definir target según la estrategia seleccionada
                target = 1.5 if "1.5" in est else 2.0 if "2x2" in est else 10.0
                impacto = (ap * (target - 1)) if v_val >= target else -float(ap)
            
            # Guardar en historial y registro de dinero
            st.session_state.historial.append(v_val)
            st.session_state.registro_saldos.append(impacto)
            st.session_state.saldo_dinamico += impacto
            
            # Actualizar relojes
            nueva_h = datetime.now(py_tz).strftime("%H:%M")
            if v_val >= 100: st.session_state.h_100x_input = nueva_h; st.session_state.h_10x_input = nueva_h
            elif v_val >= 10: st.session_state.h_10x_input = nueva_h
            
        except ValueError:
            st.error("Error: Ingresa un número válido")
        st.session_state.entrada_manual = ""

def deshacer_accion():
    if st.session_state.historial:
        # 1. Revertir el saldo usando el último impacto registrado
        ultimo_impacto = st.session_state.registro_saldos.pop()
        st.session_state.saldo_dinamico -= ultimo_impacto
        
        # 2. Eliminar del historial visual
        st.session_state.historial.pop()
        st.toast("Última ronda eliminada y contabilidad corregida")

# --- LÓGICA VISUAL ---
def obtener_semaforo():
    if len(st.session_state.historial) < 2: return "ESPERANDO DATOS", "#333"
    hist = st.session_state.historial
    est = st.session_state.modo_sel
    
    if "10x" in est:
        rondas_sin = 0
        dist = 0
        for i, v in enumerate(reversed(hist)):
            if v >= 10:
                if rondas_sin == 0: dist = i
                break
            rondas_sin += 1
        if ("Hueco" in est and rondas_sin >= 25) or ("Cazador" in est and 2 <= dist <= 10):
            return "🟢 APUESTE AHORA", "#27ae60"
        elif ("Hueco" in est and 18 <= rondas_sin < 25) or ("Cazador" in est and dist > 10):
            return "🟡 ANALIZANDO...", "#f1c40f"
        return "🔴 NO ENTRAR", "#c0392b"
    return ("🟢 APUESTE" if hist[-1] >= 1.5 else "🔴 ESPERE"), ("#27ae60" if hist[-1] >= 1.5 else "#c0392b")

# --- INTERFAZ ---
with st.sidebar:
    st.header("🦅 CONFIG ELITE")
    saldo_in = st.number_input("Saldo Inicial Gs.", value=50000, step=5000)
    if st.session_state.primer_inicio:
        st.session_state.saldo_dinamico = float(saldo_in)
        st.session_state.primer_inicio = False
    st.session_state.modo_sel = st.selectbox("Estrategia:", ["Cazador (10x)", "Hueco 10x+", "Conservadora (1.50x)", "2x2"])
    if st.button("🔄 Reiniciar App"):
        st.session_state.clear(); st.rerun()

st.markdown("<h1 style='text-align: center; color: white;'>🦅 AVIATOR ELITE v8.7</h1>", unsafe_allow_html=True)

# FILA 1: MÉTRICAS (Contabilidad Real)
ganancia_neta = st.session_state.saldo_dinamico - saldo_in
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="elite-card" style="border:2px solid #fff;"><p class="label-elite">Saldo Actual</p><h2 class="valor-elite">{int(st.session_state.saldo_dinamico):,} Gs</h2></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="elite-card" style="border:2px solid #00ff41;"><p class="label-elite">Ganancia</p><h2 class="valor-elite" style="color:#00ff41!important;">+{int(max(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="elite-card" style="border:2px solid #ff3131;"><p class="label-elite">Pérdida</p><h2 class="valor-elite" style="color:#ff3131!important;">{int(min(0, ganancia_neta)):,} Gs</h2></div>', unsafe_allow_html=True)

# FILA 2: RELOJES
t1, t2 = st.columns(2)
with t1:
    st.markdown('<div class="elite-card" style="padding:10px;"><p class="label-elite">🌸 ÚLTIMA 10X</p>', unsafe_allow_html=True)
    st.text_input("H10", key="h_10x_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
with t2:
    st.markdown('<div class="elite-card" style="padding:10px;"><p class="label-elite">✈️ GIGANTE 100X</p>', unsafe_allow_html=True)
    st.text_input("H100", key="h_100x_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# FILA 3: SEMÁFORO
txt_s, col_s = obtener_semaforo()
st.markdown(f'<div class="semaforo-box" style="background-color:{col_s}; border:4px solid rgba(255,255,255,0.2);"><p class="semaforo-texto">{txt_s}</p></div>', unsafe_allow_html=True)

# FILA 4: ENTRADA Y ACCIONES
st.markdown("<br>", unsafe_allow_html=True)
col_in, col_ap, col_ck, col_undo = st.columns([2, 1, 1, 1])
with col_in: st.text_input("VUELO:", key="entrada_manual", on_change=registrar_valor)
with col_ap: st.number_input("APUESTA:", value=2000, step=1000, key="valor_apuesta_manual")
with col_ck: st.write("##"); st.checkbox("¿APOSTÉ?", key="check_apuesta")
with col_undo: st.write("##"); st.button("🔙 DESHACER", on_click=deshacer_accion)

# HISTORIAL
if st.session_state.historial:
    h_html = "".join([f'<div class="burbuja" style="background-color:{"#3498db" if v < 2 else "#9b59b6" if v < 10 else "#e91e63"};">{v:.1f}</div>' for v in reversed(st.session_state.historial[-10:])])
    st.markdown(f'<div style="display:flex; gap:10px; overflow-x:auto; padding:15px; background:#111; border-radius:15px; margin-top:20px; border:1px solid #333;">{h_html}</div>', unsafe_allow_html=True)
