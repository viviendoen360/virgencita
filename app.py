import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Custodia de la Virgen",
    page_icon="🙏",
    layout="centered"
)

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #25D366; 
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #128C7E;
        color: white;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-off {
        padding: 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        color: #856404;
        text-align: center;
        border: 1px solid #ffeeba;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES ---
ORACION = "“Madre, en tus manos ponemos nuestro trabajo y nuestras familias. Amén.”"
ARCHIVO_DEFAULT = "lista.xlsx"

# --- FUNCIONES ---
def limpiar_telefono(telefono):
    s_tel = str(telefono)
    s_tel = "".join(filter(str.isdigit, s_tel))
    if s_tel.startswith("09"):
        return "593" + s_tel[1:]
    elif s_tel.startswith("9"):
         return "593" + s_tel
    return s_tel

def generar_link_wa(telefono, mensaje):
    tel_clean = limpiar_telefono(telefono)
    msg_encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{tel_clean}?text={msg_encoded}"

def cargar_datos(archivo):
    try:
        df = pd.read_excel(archivo, engine='openpyxl')
        # Limpiar nombres de columnas (quitar espacios y poner mayúscula inicial)
        df.columns = [c.strip().capitalize() for c in df.columns]
        # Asegurar que la columna Fecha sea tipo fecha
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
        return None

# --- INTERFAZ PRINCIPAL ---
st.title("🙏 Camino de la Virgen")

# Carga de datos
df = None
if os.path.exists(ARCHIVO_DEFAULT):
    df = cargar_datos(ARCHIVO_DEFAULT)
    st.caption("✅ Lista cargada automáticamente desde el sistema.")

uploaded_file = st.sidebar.file_uploader("📂 Actualizar lista (Excel)", type=["xlsx"])
if uploaded_file:
    df = cargar_datos(uploaded_file)
    st.caption("✅ Lista actualizada manualmente.")

# --- LÓGICA DE FECHAS ---
if df is not None:
    # Verificación de columnas
    req = {'Fecha', 'Nombre', 'Telefono', 'Departamento'}
    if not req.issubset(df.columns):
        st.error(f"⚠️ Faltan columnas en el Excel. Debe tener: {', '.join(req)}")
    else:
        # Obtener fecha de hoy
        hoy = datetime.now().date()
        
        # Buscar si HOY existe en la columna Fecha
        fila_hoy = df[df['Fecha'] == hoy]
        
        if not fila_hoy.empty:
            # --- CASO 1: HOY ES DÍA DE ENTREGA ---
            idx_hoy = fila_hoy.index[0]
            
            p_recibe = df.iloc[idx_hoy]
            
            # Quién entrega es la persona de la fila ANTERIOR en la lista
            # (Si es la primera fila, no hay anterior, manejamos ese error)
            if idx_hoy > 0:
                p_entrega = df.iloc[idx_hoy - 1]
                
                st.info(f"📅 **{hoy.strftime('%d/%m/%Y')}** - Hoy hay cambio de custodia.")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <div style='font-size:2em;'>📤</div>
                        <h3>Entrega</h3>
                        <h2>{p_entrega['Nombre']}</h2>
                        <p>{p_entrega['Departamento']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="card">
                        <div style='font-size:2em;'>📥</div>
                        <h3>Recibe</h3>
                        <h2>{p_recibe['Nombre']}</h2>
                        <p>{p_recibe['Departamento']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botones de WhatsApp
                msg_e = f"👋 Hola *{p_entrega['Nombre']}*, hoy ({hoy}) entregas la imagen de la Virgen a *{p_recibe['Nombre']}* ({p_recibe['Departamento']}).\n\n{ORACION}"
                msg_r = f"👋 Hola *{p_recibe['Nombre']}*, hoy ({hoy}) recibes la visita de la Virgen de manos de *{p_entrega['Nombre']}*.\n\n{ORACION}"
                
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button(f"📲 Avisar a {p_entrega['Nombre']}", generar_link_wa(p_entrega['Telefono'], msg_e))
                with c2:
                    st.link_button(f"📩 Avisar a {p_recibe['Nombre']}", generar_link_wa(p_recibe['Telefono'], msg_r))
            
            else:
                st.warning("Hoy es el primer día de la lista. No hay registro de quién entrega (fila anterior).")
                st.info(f"Recibe hoy: **{p_recibe['Nombre']}**")

        else:
            # --- CASO 2: HOY NO ESTÁ EN LA LISTA (Feriado/Fin de semana) ---
            st.markdown(f"""
            <div class="status-off">
                <h3>⏸️ Hoy no hay entregas programadas</h3>
                <p>Fecha: {hoy.strftime('%d/%m/%Y')}</p>
                <p>La Virgen permanece con la última persona asignada.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Opcional: Mostrar quién fue el último en tenerla
            fechas_pasadas = df[df['Fecha'] < hoy]
            if not fechas_pasadas.empty:
                ultimo = fechas_pasadas.iloc[-1]
                st.write(f"📍 Última ubicación conocida ({ultimo['Fecha'].strftime('%d/%m')}): **{ultimo['Nombre']}** ({ultimo['Departamento']})")

else:
    st.warning("⚠️ No se ha cargado ninguna lista. Sube el archivo Excel.")
