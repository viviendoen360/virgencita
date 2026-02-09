import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import urllib.parse

# 1. Configuración DEBE ser lo primero
st.set_page_config(page_title="Custodia de la Virgen", page_icon="🙏", layout="centered")

# 2. Título visible para confirmar que la app carga
st.title("🙏 Camino de la Virgen")

# 3. Bloque de prueba de librerías y archivos
try:
    # Intentamos importar openpyxl manualmente para ver si está instalado
    import openpyxl
except ImportError:
    st.error("🚨 ERROR CRÍTICO: Falta instalar 'openpyxl'.")
    st.warning("Solución: Abre el archivo 'requirements.txt' en GitHub y asegúrate de que contenga la palabra: openpyxl")
    st.stop() # Detiene la app aquí

# 4. Verificación del Archivo
ARCHIVO_DEFAULT = "lista.xlsx"

if not os.path.exists(ARCHIVO_DEFAULT):
    st.error(f"🚨 ERROR: No encuentro el archivo '{ARCHIVO_DEFAULT}'")
    st.info("Archivos encontrados en el sistema:")
    st.code("\n".join(os.listdir())) # Muestra qué archivos SÍ existen
    st.warning("Solución: Revisa si tu Excel en GitHub tiene mayúsculas (ej: Lista.xlsx) y cambia el nombre en el código o en el archivo.")
    st.stop()

# --- SI LLEGAMOS AQUÍ, TODO ESTÁ BIEN. EJECUTAMOS LA APP NORMAL ---

# Estilos CSS
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #25D366; color: white; font-weight: bold; border: none; }
    .card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; color: #31333F !important; }
    .card h3, .card h4, .card p, .card small { color: #31333F !important; }
    </style>
    """, unsafe_allow_html=True)

ORACION = "“Madre, en tus manos ponemos nuestro trabajo y nuestras familias. Amén.”"

def generar_link_wa(telefono, mensaje):
    s_tel = "".join(filter(str.isdigit, str(telefono)))
    if s_tel.startswith("09"): s_tel = "593" + s_tel[1:]
    elif s_tel.startswith("9"): s_tel = "593" + s_tel
    return f"https://wa.me/{s_tel}?text={urllib.parse.quote(mensaje)}"

def generar_link_calendar(fecha_obj, nombre_entrega):
    f_inicio = fecha_obj.strftime('%Y%m%d')
    f_fin = (fecha_obj + timedelta(days=1)).strftime('%Y%m%d')
    titulo = "🙏 Recibir Virgen María"
    descripcion = f"Recibir de: {nombre_entrega}. \n\n{ORACION}"
    params = {'action': 'TEMPLATE', 'text': titulo, 'details': descripcion, 'dates': f"{f_inicio}/{f_fin}"}
    return f"https://www.google.com/calendar/render?{urllib.parse.urlencode(params)}"

# Carga de datos con reporte de error detallado
try:
    df = pd.read_excel(ARCHIVO_DEFAULT, engine='openpyxl')
    df.columns = [c.strip().capitalize() for c in df.columns]
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
except Exception as e:
    st.error(f"🚨 El archivo Excel tiene un formato incorrecto: {e}")
    st.stop()

# Lógica Principal
hoy = datetime.now().date()
fila_hoy = df[df['Fecha'] == hoy]

st.markdown("### 📅 Estado del día")

if not fila_hoy.empty:
    idx_hoy = fila_hoy.index[0]
    p_recibe = df.iloc[idx_hoy]
    
    if idx_hoy > 0:
        p_entrega = df.iloc[idx_hoy - 1]
        
        st.info(f"**{hoy.strftime('%d/%m/%Y')}** - Hoy hay cambio.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='card'><h3>Entrega</h3><h4>{p_entrega['Nombre']}</h4><small>{p_entrega['Departamento']}</small></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='card'><h3>Recibe</h3><h4>{p_recibe['Nombre']}</h4><small>{p_recibe['Departamento']}</small></div>", unsafe_allow_html=True)
        
        msg_e = f"Hola {p_entrega['Nombre']}, hoy entregas la Virgen a {p_recibe['Nombre']}.\n\n{ORACION}"
        msg_r = f"Hola {p_recibe['Nombre']}, hoy recibes la Virgen de {p_entrega['Nombre']}.\n\n{ORACION}"
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1: st.link_button(f"📲 Avisar a {p_entrega['Nombre']}", generar_link_wa(p_entrega['Telefono'], msg_e))
        with col_btn2: st.link_button(f"📩 Avisar a {p_recibe['Nombre']}", generar_link_wa(p_recibe['Telefono'], msg_r))
    else:
        st.info(f"Recibe hoy: **{p_recibe['Nombre']}** (Inicio de lista)")
else:
    st.warning(f"Hoy ({hoy}) no hay entregas.")

st.markdown("---")
st.header("🔍 Busca tu fecha")
lista = sorted(df['Nombre'].unique())
sel = st.selectbox("Nombre:", lista)
if sel:
    turnos = df[df['Nombre'] == sel]
    if not turnos.empty:
        for i, r in turnos.iterrows():
            f_turno = r['Fecha']
            n_ent = df.iloc[i-1]['Nombre'] if i > 0 else "Inicio"
            st.write(f"🗓️ **{f_turno.strftime('%d/%m')}** (Recibes de {n_ent})")
            st.link_button("📅 Agendar", generar_link_calendar(f_turno, n_ent))
