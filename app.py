import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Custodia de la Virgen",
    page_icon="🙏",
    layout="centered"
)

# --- ESTILOS VISUALES (FIX DARK MODE) ---
st.markdown("""
    <style>
    /* Botones estilo WhatsApp */
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
    
    /* ESTILO DE TARJETAS (Fixed para Dark Mode) */
    .card {
        background-color: #f0f2f6; /* Fondo gris claro */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        
        /* FUERZA EL TEXTO A NEGRO SIEMPRE */
        color: #31333F !important; 
    }
    
    /* Forzar color negro en todos los textos dentro de la tarjeta */
    .card h3, .card h4, .card p, .card small {
        color: #31333F !important;
    }

    /* Botón de Calendario (Azul) */
    .calendar-btn {
        background-color: #4285F4 !important;
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

def generar_link_calendar(fecha_obj, nombre_entrega):
    f_inicio = fecha_obj.strftime('%Y%m%d')
    f_fin = (fecha_obj + timedelta(days=1)).strftime('%Y%m%d')
    
    titulo = "🙏 Recibir Virgen María"
    descripcion = f"Recibir la imagen de manos de {nombre_entrega}. \n\n{ORACION}"
    
    params = {
        'action': 'TEMPLATE',
        'text': titulo,
        'details': descripcion,
        'dates': f"{f_inicio}/{f_fin}"
    }
    return f"https://www.google.com/calendar/render?{urllib.parse.urlencode(params)}"

def cargar_datos(archivo):
    try:
        df = pd.read_excel(archivo, engine='openpyxl')
        df.columns = [c.strip().capitalize() for c in df.columns]
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
        return None

# --- INTERFAZ PRINCIPAL ---
st.title("🙏 Camino de la Virgen")

# 1. BARRA LATERAL (Siempre visible)
st.sidebar.header("Configuración")
uploaded_file = st.sidebar.file_uploader("📂 Actualizar lista (Excel)", type=["xlsx"])

# 2. LÓGICA DE CARGA (Prioridad: Archivo subido > Archivo en GitHub)
df = None

if uploaded_file:
    df = cargar_datos(uploaded_file)
    if df is not None:
        st.sidebar.success("✅ Usando lista subida manualmente")
elif os.path.exists(ARCHIVO_DEFAULT):
    df = cargar_datos(ARCHIVO_DEFAULT)
    # st.sidebar.info("Usando lista predeterminada del sistema")

# --- LÓGICA DEL PROGRAMA ---
if df is not None:
    # A. SECCIÓN DE HOY
    hoy = datetime.now().date()
    fila_hoy = df[df['Fecha'] == hoy]
    
    st.markdown("### 📅 Estado del día")
    
    if not fila_hoy.empty:
        idx_hoy = fila_hoy.index[0]
        p_recibe = df.iloc[idx_hoy]
        
        if idx_hoy > 0:
            p_entrega = df.iloc[idx_hoy - 1]
            
            st.info(f"**{hoy.strftime('%d/%m/%Y')}** - Hoy hay cambio de custodia.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div style='font-size:2em;'>📤</div>
                    <h3>Entrega</h3>
                    <h4>{p_entrega['Nombre']}</h4>
                    <small>{p_entrega['Departamento']}</small>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="card">
                    <div style='font-size:2em;'>📥</div>
                    <h3>Recibe</h3>
                    <h4>{p_recibe['Nombre']}</h4>
                    <small>{p_recibe['Departamento']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            # Botones WA
            msg_e = f"👋 Hola *{p_entrega['Nombre']}*, hoy ({hoy}) entregas la imagen de la Virgen a *{p_recibe['Nombre']}* ({p_recibe['Departamento']}).\n\n{ORACION}"
            msg_r = f"👋 Hola *{p_recibe['Nombre']}*, hoy ({hoy}) recibes la visita de la Virgen de manos de *{p_entrega['Nombre']}*.\n\n{ORACION}"
            
            c1, c2 = st.columns(2)
            with c1:
                st.link_button(f"📲 Avisar a {p_entrega['Nombre']}", generar_link_wa(p_entrega['Telefono'], msg_e))
            with c2:
                st.link_button(f"📩 Avisar a {p_recibe['Nombre']}", generar_link_wa(p_recibe['Telefono'], msg_r))
        else:
            st.info(f"Recibe hoy: **{p_recibe['Nombre']}** (Primer día de la lista)")
    else:
        st.warning(f"Hoy ({hoy.strftime('%d/%m')}) no hay entregas programadas.")

    # B. BUSCADOR
    st.markdown("---")
    st.header("🔍 Busca tu fecha")
    st.write("Selecciona tu nombre para saber cuándo te toca.")

    lista_nombres = sorted(df['Nombre'].unique())
    nombre_seleccionado = st.selectbox("Escribe o selecciona tu nombre:", lista_nombres)

    if nombre_seleccionado:
        mis_turnos = df[df['Nombre'] == nombre_seleccionado]
        
        if not mis_turnos.empty:
            st.success(f"Hola **{nombre_seleccionado}**, te toca recibir la imagen en estas fechas:")
            
            for idx, row in mis_turnos.iterrows():
                fecha_turno = row['Fecha']
                
                nombre_entrega = "un compañero"
                if idx > 0:
                    nombre_entrega = df.iloc[idx - 1]['Nombre']
                
                link_cal = generar_link_calendar(fecha_turno, nombre_entrega)
                
                col_a, col_b = st.columns([2, 2])
                with col_a:
                    st.markdown(f"🗓️ **{fecha_turno.strftime('%d/%m/%Y')}**")
                    st.caption(f"Recibes de: {nombre_entrega}")
                with col_b:
                    st.link_button("📅 Agendar en Google", link_cal)
                st.markdown("---")
        else:
            st.info("No tienes fechas asignadas en la lista actual.")

else:
    st.warning("⚠️ No se ha cargado ninguna lista.")
    st.info("Sube el archivo Excel en el menú de la izquierda.")
